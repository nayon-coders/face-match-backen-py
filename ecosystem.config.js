module.exports = {
  apps: [
    {
      name: "hrm-backend",
      script: "venv/bin/uvicorn",
      args: "main:app --host 0.0.0.0 --port 8008",
      cwd: "/var/www/karalasoft/hrm/backend",
      interpreter: "none",
      autorestart: true,
      max_restarts: 10,
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
