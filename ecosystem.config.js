module.exports = {
    apps : [{
      name: "API_GETAWAY_SEMAFOROS",
      script: "docker-compose up",
      instances: 1,
      autorestart: true,
      watch: true,
      max_memory_restart: "2G",
      env: {
        NODE_ENV: "production"
      }
    }]
  };