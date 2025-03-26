require('dotenv').config();
const path = require('path');

const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3006', 10),
  logLevel: process.env.LOG_LEVEL || 'info',
  logFile: process.env.LOG_FILE || './logs/integrations.log',

  // JWT
  jwtSecret: process.env.JWT_SECRET || 'CHAVE_JWT_LOCAL_DEV',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',

  // HTTPS
  useHttps: process.env.USE_HTTPS === 'true',
  sslKeyPath: process.env.SSL_KEY_PATH || './certs/key.pem',
  sslCertPath: process.env.SSL_CERT_PATH || './certs/cert.pem',

  // Redis (Bull)
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined
  },

  // DB via .env (usado pelo knexfile.js)
  db: {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASS || 'postgres',
    database: process.env.DB_NAME || 'flowsale',
    port: parseInt(process.env.DB_PORT || '5432', 10)
  },

  // Integrações (exemplo)
  facebookAppId: process.env.FACEBOOK_APP_ID,
  facebookAppSecret: process.env.FACEBOOK_APP_SECRET,
  twilioAccountSid: process.env.TWILIO_ACCOUNT_SID,
  twilioAuthToken: process.env.TWILIO_AUTH_TOKEN,
  twilioPhoneNumber: process.env.TWILIO_PHONE_NUMBER,
  // etc.

  // Observabilidade
  readinessPath: '/ready',
  livenessPath: '/live'
};

module.exports = config;
