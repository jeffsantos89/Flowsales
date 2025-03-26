const fs = require('fs');
const path = require('path');

function getCredentials() {
  const keyPath = process.env.SSL_KEY_PATH;
  const certPath = process.env.SSL_CERT_PATH;
  if (!keyPath || !certPath) {
    throw new Error('SSL_KEY_PATH and SSL_CERT_PATH must be set for HTTPS');
  }
  return {
    key: fs.readFileSync(path.resolve(keyPath)),
    cert: fs.readFileSync(path.resolve(certPath))
  };
}

module.exports = {
  getCredentials
};
