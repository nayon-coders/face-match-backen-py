import requests

url = "http://localhost:8000/api/attendance/clock"
data = {
    "employee_id": 3,
    "type": "clock_in",
    "latitude": 23.0,
    "longitude": 90.0
}
res = requests.post(url, data=data)
print(res.status_code, res.text)
