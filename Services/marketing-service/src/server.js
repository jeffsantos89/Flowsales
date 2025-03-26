require('dotenv').config();
const express = require('express');
const http = require('http');
const https = require('https');
const logger = require('./logger');
const { getCredentials } = require('./ssl');
const errorHandling = require('./errorHandling');
const jwtAuth = require('./auth');
const emailAutomationsRoutes = require('./routes/emailAutomations');

const app = express();
app.use(express.json());

// Rota de saúde (sem auth)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', pid: process.pid, time: new Date() });
});

// Middleware JWT (todas as rotas abaixo exigem token)
app.use(jwtAuth);

// Rotas
app.use('/email-automations', emailAutomationsRoutes);

// Tratamento de erros
app.use(errorHandling);

const PORT = process.env.PORT || 3005;
const useHttps = process.env.USE_HTTPS === 'true';

if (useHttps) {
  const credentials = getCredentials();
  if (!credentials) {
    logger.error('HTTPS requested but credentials not provided');
    process.exit(1);
  }
  const server = https.createServer(credentials, app);
  server.listen(PORT, () => {
    logger.info(`Marketing service (HTTPS) worker=${process.pid} on port ${PORT}`);
  });
} else {
  const server = http.createServer(app);
  server.listen(PORT, () => {
    logger.info(`Marketing service (HTTP) worker=${process.pid} on port ${PORT}`);
  });
}
