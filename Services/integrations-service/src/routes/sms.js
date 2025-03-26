const express = require('express');
const router = express.Router();
const { validateSmsSend } = require('../validations/smsValidation');
const { sendSmsNow, scheduleSms } = require('../helpers/integrationsWorker');

router.post('/send', validateSmsSend, async (req, res, next) => {
  try {
    const { to, message } = req.body;
    const result = await sendSmsNow(to, message);
    res.json({ message: 'SMS sent', result });
  } catch (err) {
    next(err);
  }
});

router.post('/schedule', validateSmsSend, async (req, res, next) => {
  try {
    const { to, message, delayMillis } = req.body;
    if (!delayMillis) {
      return res.status(400).json({ error: 'delayMillis is required' });
    }
    await scheduleSms(to, message, delayMillis);
    res.json({ message: 'SMS scheduled', delayMillis });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
