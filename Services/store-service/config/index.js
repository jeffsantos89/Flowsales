require('dotenv').config();
const path = require('path');

const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3007', 10),
  logLevel: process.env.LOG_LEVEL || 'info',
  logFile: process.env.LOG_FILE || './logs/store.log',

  db: {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASS || 'postgres',
    database: process.env.DB_NAME || 'flowsale',
    port: parseInt(process.env.DB_PORT || '5432', 10)
  },

  jwtSecret: process.env.JWT_SECRET || 'secret',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',

  cluster: process.env.CLUSTER === 'true'
};

module.exports = config;
