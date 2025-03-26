const { createLogger, format, transports } = require('winston');
const path = require('path');
const cfg = require('../config');

const logger = createLogger({
  level: cfg.logLevel,
  format: format.combine(
    format.timestamp(),
    format.json()
  ),
  transports: [
    new transports.Console(),
    new transports.File({
      filename: path.resolve(cfg.logFile),
      maxsize: 1048576,
      maxFiles: 5
    })
  ]
});

module.exports = logger;
