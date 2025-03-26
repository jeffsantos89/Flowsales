const fs = require('fs');
const path = require('path');
const cfg = require('../config');

function getCredentials() {
  if (!cfg.useHttps) return null;

  if (!cfg.sslKeyPath || !cfg.sslCertPath) {
    throw new Error('SSL_KEY_PATH and SSL_CERT_PATH must be set if USE_HTTPS=true');
  }
  return {
    key: fs.readFileSync(path.resolve(cfg.sslKeyPath)),
    cert: fs.readFileSync(path.resolve(cfg.sslCertPath))
  };
}

module.exports = { getCredentials };
