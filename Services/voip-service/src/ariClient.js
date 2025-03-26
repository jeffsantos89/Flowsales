const ari = require('asterisk-ari-client');
const logger = require('./logger');

let ariClient = null;

async function connectARI() {
  const { ARI_URL, ARI_USER, ARI_PASS } = process.env;
  if (!ARI_URL || !ARI_USER || !ARI_PASS) {
    throw new Error('ARI_URL, ARI_USER, ARI_PASS must be set in .env');
  }

  logger.info(`Connecting to ARI at ${ARI_URL} as user ${ARI_USER}...`);

  // Conexão
  ariClient = await ari.connect(ARI_URL, ARI_USER, ARI_PASS);

  // Registrar eventos
  ariClient.on('StasisStart', (event, channel) => {
    logger.info(`Channel ${channel.id} entered Stasis`);
  });

  ariClient.on('StasisEnd', (event, channel) => {
    logger.info(`Channel ${channel.id} left Stasis`);
  });

  logger.info('Connected to ARI successfully.');
}

function getClient() {
  if (!ariClient) {
    throw new Error('ARI client not connected');
  }
  return ariClient;
}

module.exports = {
  connectARI,
  getClient
};
