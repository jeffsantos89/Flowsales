const express = require('express');
const router = express.Router();
const logger = require('../logger');
const { createIntegrationLog } = require('../models/logsModel');

// Exemplo: Twilio inbound SMS
router.post('/twilio/sms', async (req, res) => {
  try {
    logger.info('[WEBHOOK] Twilio SMS inbound', req.body);
    // Salva log no DB
    await createIntegrationLog('sms', 'webhook', req.body, 'success', null);
    // Twilio exige 200 com <Response></Response>
    return res.type('text/xml').send('<Response></Response>');
  } catch (err) {
    logger.error('[WEBHOOK] Twilio SMS error', { error: err.message });
    return res.status(500).send('Error');
  }
});

// Exemplo: Facebook event
router.post('/facebook/events', async (req, res) => {
  try {
    logger.info('[WEBHOOK] Facebook event', req.body);
    await createIntegrationLog('facebook', 'webhook', req.body, 'success', null);
    res.json({ message: 'ok' });
  } catch (err) {
    logger.error('[WEBHOOK] Facebook event error', { error: err.message });
    res.status(500).json({ error: 'Error processing event' });
  }
});

module.exports = router;
