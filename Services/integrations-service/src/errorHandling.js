const logger = require('./logger');

function errorHandling(err, req, res, next) {
  logger.error('Unhandled error', { message: err.message, stack: err.stack });
  res.status(500).json({ error: err.message || 'Internal Server Error' });
}

module.exports = errorHandling;
