const express = require('express');
const router = express.Router();
const { validateSocialPost } = require('../validations/socialValidation');
const { postSocialNow, scheduleSocialPost } = require('../helpers/integrationsWorker');

router.post('/post', validateSocialPost, async (req, res, next) => {
  try {
    const { platform, message } = req.body;
    const result = await postSocialNow(platform, message);
    res.json({ message: 'Social post successful', result });
  } catch (err) {
    next(err);
  }
});

router.post('/schedule', validateSocialPost, async (req, res, next) => {
  try {
    const { platform, message, delayMillis } = req.body;
    if (!delayMillis) {
      return res.status(400).json({ error: 'delayMillis is required' });
    }
    await scheduleSocialPost(platform, message, delayMillis);
    res.json({ message: 'Social post scheduled', delayMillis });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
