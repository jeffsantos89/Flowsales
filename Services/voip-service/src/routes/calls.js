const express = require('express');
const router = express.Router();
const logger = require('../logger');
const { getClient } = require('../ariClient');

// POST /calls/originate
router.post('/originate', async (req, res) => {
  const { endpoint, callerId, app } = req.body;
  if (!endpoint || !callerId || !app) {
    return res.status(400).json({ error: 'Missing endpoint, callerId or app' });
  }
  try {
    const ari = getClient();
    // Originate channel
    const channel = await ari.channels.originate({
      endpoint,
      app,
      callerId
    });
    logger.info(`Call originated to ${endpoint}, channelId=${channel.id}`);
    res.json({ message: 'Call originated', channelId: channel.id });
  } catch (error) {
    logger.error('Error originating call', error);
    res.status(500).json({ error: error.message });
  }
});

// POST /calls/hangup
router.post('/hangup', async (req, res) => {
  const { channelId } = req.body;
  if (!channelId) {
    return res.status(400).json({ error: 'Missing channelId' });
  }
  try {
    const ari = getClient();
    await ari.channels.hangup({ channelId });
    logger.info(`Channel ${channelId} hung up`);
    res.json({ message: `Channel ${channelId} hung up` });
  } catch (error) {
    logger.error('Error hanging up call', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
