const express = require('express');
const router = express.Router();
const logger = require('./logger');

// GET /sip/config
router.get('/config', (req, res) => {
  logger.info('Retrieving SIP config (placeholder)');
  res.json({ message: 'SIP config not implemented' });
});

// POST /sip/reload
router.post('/reload', (req, res) => {
  logger.info('Reloading SIP stack (placeholder)');
  res.json({ message: 'SIP reload triggered (placeholder)' });
});

module.exports = router;













