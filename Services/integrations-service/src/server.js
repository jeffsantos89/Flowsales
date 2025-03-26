const express = require('express');
const http = require('http');
const https = require('https');
const cfg = require('../config');
const logger = require('./logger');
const { getCredentials } = require('./ssl');
const errorHandling = require('./errorHandling');
const jwtAuth = require('./auth');

const authRoutes = require('./routes/authRoutes');
const socialRoutes = require('./routes/social');
const smsRoutes = require('./routes/sms');
const webhooksRoutes = require('./routes/webhooks');

const app = express();
app.use(express.json());

// Liveness & Readiness (exemplo)
app.get(cfg.livenessPath, (req, res) => res.json({ status: 'live' }));
app.get(cfg.readinessPath, (req, res) => res.json({ status: 'ready' }));

// Health
app.get('/health', (req, res) => {
  res.json({ status: 'ok', pid: process.pid, time: new Date() });
});

// Rota de login
app.use('/auth', authRoutes);

// Rotas que exigem JWT
app.use(jwtAuth);

// Rotas integrações
app.use('/social', socialRoutes);
app.use('/sms', smsRoutes);
app.use('/webhooks', webhooksRoutes);

// Erros
app.use(errorHandling);

function startServer() {
  if (cfg.useHttps) {
    const credentials = getCredentials();
    if (!credentials) {
      logger.error('HTTPS requested but no credentials');
      process.exit(1);
    }
    const server = https.createServer(credentials, app);
    server.listen(cfg.port, () => {
      logger.info(`Integrations service (HTTPS) worker=${process.pid} on port ${cfg.port}`);
    });
  } else {
    const server = http.createServer(app);
    server.listen(cfg.port, () => {
      logger.info(`Integrations service (HTTP) worker=${process.pid} on port ${cfg.port}`);
    });
  }
}

// Export app for tests
module.exports = { app, startServer };
