import numpy as np
import cv2
import json

from PIL import Image, ImageOps
import io
import os

# Set environment variable to avoid tf-keras warning if needed, but deepface handles it.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    from deepface import DeepFace
except ImportError:
    print("WARNING: deepface not installed. Please install it using pip install deepface tf-keras")

import base64

def preload_models():
    """Preload models on startup to avoid thread initialization issues."""
    try:
        print("DEBUG: Preloading DeepFace models (ArcFace & MTCNN)...")
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        DeepFace.represent(img_path=dummy_img, model_name="ArcFace", detector_backend="mtcnn", enforce_detection=False)
        print("DEBUG: DeepFace models preloaded successfully.")
    except Exception as e:
        print(f"DEBUG: Failed to preload models: {e}")

def extract_face_base64(image_bytes: bytes) -> dict:
    """
    Extracts the face from the image and returns it as a base64 string for UI preview.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        rgb_img = np.array(img)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
        
        faces = DeepFace.extract_faces(
            img_path=bgr_img, 
            detector_backend="mtcnn", 
            enforce_detection=True
        )
        
        if not faces or len(faces) == 0:
            return {"success": False, "error": "No face detected in the image."}
            
        # The first face's facial area
        face = faces[0]["face"] # This is a numpy array normalized between 0 and 1
        
        # Convert normalized float array (0-1) to uint8 (0-255)
        if face.dtype == np.float32 or face.dtype == np.float64:
            face = (face * 255).astype(np.uint8)
            
        # Convert BGR back to RGB for PIL
        # Note: DeepFace.extract_faces might return RGB if we passed BGR, let's just use it to encode.
        # Actually it returns RGB.
        face_img = Image.fromarray(face)
        
        buffered = io.BytesIO()
        face_img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {"success": True, "image": f"data:image/jpeg;base64,{img_str}"}
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        import traceback
        return {"success": False, "error": "Internal Error: " + str(e)}

def get_face_encoding(image_bytes: bytes) -> str:
    """
    Takes an image in bytes, detects faces, and returns the encoding of the first face found using ArcFace.
    """
    print(f"DEBUG: get_face_encoding called with image of size {len(image_bytes)} bytes")
    try:
        # Load image with PIL to handle EXIF rotation from iPhones
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img) # Fix rotation!
        img = img.convert("RGB")
        rgb_img = np.array(img)
        
        # Convert to BGR for DeepFace/OpenCV compatibility
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)

        print(f"DEBUG: Image decoded, shape: {bgr_img.shape}")
        
        # Extract embeddings using ArcFace
        print("DEBUG: Extracting embeddings with ArcFace...")
        # represent returns a list of dictionaries, one for each face found
        results = DeepFace.represent(
            img_path=bgr_img, 
            model_name="ArcFace", 
            detector_backend="mtcnn",
            enforce_detection=True
        )
        
        if not results or len(results) == 0:
            print("DEBUG: No face found in the image.")
            return None
            
        # Return the embedding of the most prominent face
        encoding = results[0]["embedding"]
        print(f"DEBUG: ArcFace encoding generated successfully. Dimension: {len(encoding)}")
        return json.dumps(encoding)
    except Exception as e:
        import traceback
        print(f"Error processing image: {e}")
        print(traceback.format_exc())
        return None

def verify_face(known_encoding_json: str, unknown_image_bytes: bytes, threshold: float = 0.68) -> bool:
    """
    Compares an unknown face image against a known ArcFace encoding.
    Threshold for ArcFace using Cosine Distance is typically ~0.68.
    """
    print("DEBUG: verify_face called")
    try:
        if not known_encoding_json:
            print("DEBUG: known_encoding_json is empty")
            return False
            
        # Parse known encoding
        known_encoding = json.loads(known_encoding_json)
        print(f"DEBUG: Loaded known encoding of dimension {len(known_encoding)}")
        
        # Get encoding of unknown image
        unknown_encoding_json = get_face_encoding(unknown_image_bytes)
        if not unknown_encoding_json:
            print("DEBUG: Failed to extract encoding from unknown image")
            return False
            
        unknown_encoding = json.loads(unknown_encoding_json)
        
        # Calculate Cosine Distance
        A = np.array(known_encoding)
        B = np.array(unknown_encoding)
        
        cosine_similarity = np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))
        distance = 1 - cosine_similarity
        
        print(f"DEBUG: ArcFace Compare result distance: {distance:.4f}, threshold: {threshold}")
        
        # Match if distance is less than or equal to threshold
        return bool(distance <= threshold)
    except Exception as e:
        print(f"Error verifying face: {e}")
        return False

def match_two_images(image1_bytes: bytes, image2_bytes: bytes, threshold: float = 0.68) -> dict:
    """
    Extracts face encodings from two images and compares them.
    Returns a dict with 'match', 'distance', 'error' (if any).
    """
    print("DEBUG: match_two_images called")
    try:
        # Get encoding of image 1
        encoding1_json = get_face_encoding(image1_bytes)
        if not encoding1_json:
            return {"match": False, "error": "No face found in image 1"}
            
        encoding1 = json.loads(encoding1_json)
        
        # Get encoding of image 2
        encoding2_json = get_face_encoding(image2_bytes)
        if not encoding2_json:
            return {"match": False, "error": "No face found in image 2"}
            
        encoding2 = json.loads(encoding2_json)
        
        # Calculate Cosine Distance
        A = np.array(encoding1)
        B = np.array(encoding2)
        
        cosine_similarity = np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))
        distance = 1 - cosine_similarity
        
        print(f"DEBUG: ArcFace 1:1 Compare result distance: {distance:.4f}, threshold: {threshold}")
        
        return {
            "match": bool(distance <= threshold),
            "distance": float(distance),
            "error": None
        }
    except Exception as e:
        print(f"Error matching images: {e}")
        return {"match": False, "error": str(e)}
