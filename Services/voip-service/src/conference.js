const express = require('express');
const router = express.Router();
const logger = require('./logger');
const { getClient } = require('./ariClient');

// GET /conference
router.get('/', async (req, res) => {
  logger.info('List conferences (placeholder)');
  // Exemplo: list all active bridges
  // const ari = getClient();
  // const bridges = await ari.bridges.list();
  res.json({ message: 'Conference list not implemented' });
});

// POST /conference/create
router.post('/create', async (req, res) => {
  logger.info('Create a new conference (placeholder)');
  // Exemplo: create a new bridge
  // const ari = getClient();
  // const bridge = await ari.bridges.create({ type: 'mixing' });
  // ...
  res.json({ message: 'Conference created (placeholder)' });
});

module.exports = router;
