const fs = require('fs');
const path = require('path');

function getCredentials() {
  const useHttps = process.env.USE_HTTPS === 'true';
  if (!useHttps) return null;

  const keyPath = process.env.SSL_KEY_PATH;
  const certPath = process.env.SSL_CERT_PATH;
  if (!keyPath || !certPath) {
    throw new Error('SSL_KEY_PATH and SSL_CERT_PATH must be set if USE_HTTPS=true');
  }
  return {
    key: fs.readFileSync(path.resolve(keyPath)),
    cert: fs.readFileSync(path.resolve(certPath))
  };
}

module.exports = { getCredentials };
 const fs = require('fs');
 const path = require('path');

 function getCredentials() {
   const useHttps = process.env.USE_HTTPS === 'true';
   if (!useHttps) return null;

   const keyPath = process.env.SSL_KEY_PATH;
   const certPath = process.env.SSL_CERT_PATH;
   if (!keyPath || !certPath) {
     throw new Error('SSL_KEY_PATH and SSL_CERT_PATH must be set if USE_HTTPS=true');
   }
   return {
     key: fs.readFileSync(path.resolve(keyPath)),
     cert: fs.readFileSync(path.resolve(certPath))
   };
 }

 module.exports = { getCredentials };
