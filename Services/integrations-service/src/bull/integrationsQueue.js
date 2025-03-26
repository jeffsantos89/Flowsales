const Bull = require('bull');
const logger = require('../logger');
const cfg = require('../../config');

const integrationsQueue = new Bull('integrationsQueue', {
  redis: {
    host: cfg.redis.host,
    port: cfg.redis.port,
    password: cfg.redis.password
  }
});

integrationsQueue.process(async (job) => {
  const { type, payload } = job.data;
  logger.info(`[BULL] Processing type=${type}`, { payload });
  // Chama real worker
  // ...
  return { status: 'ok', type, payload };
});

module.exports = integrationsQueue;
