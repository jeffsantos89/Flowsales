const axios = require('axios');
const logger = require('../logger');
const integrationsQueue = require('../bull/integrationsQueue');
const { createIntegrationLog } = require('../models/logsModel');
const cfg = require('../../config');
const twilio = require('twilio');

async function postSocialNow(platform, message) {
  logger.info(`Posting on ${platform}: ${message}`);

  let result;
  let status = 'success';
  let errorMsg = null;
  try {
    if (platform === 'facebook') {
      // Exemplo real
      // const token = ... (obtido do cfg)
      // const response = await axios.post(`https://graph.facebook.com/v12.0/me/feed?access_token=${token}`, { message });
      // result = response.data;
      result = { platform, posted: true };
    } else if (platform === 'twitter') {
      // Chamar Twitter API v2 ...
      result = { platform, posted: true };
    } else {
      throw new Error(`Unsupported platform: ${platform}`);
    }
  } catch (err) {
    status = 'failed';
    errorMsg = err.message;
    throw err;
  } finally {
    await createIntegrationLog(platform, 'postNow', { message }, status, errorMsg);
  }
  return result;
}

async function scheduleSocialPost(platform, message, delayMillis) {
  await integrationsQueue.add(
    { type: 'social', payload: { platform, message } },
    { delay: delayMillis }
  );
  logger.info(`[SCHEDULED] Social post on ${platform} in ${delayMillis}ms queued`);
}

async function sendSmsNow(to, text) {
  logger.info(`Sending SMS to ${to}: ${text}`);

  let status = 'success';
  let errorMsg = null;
  try {
    const client = twilio(cfg.twilioAccountSid, cfg.twilioAuthToken);
    // const response = await client.messages.create({
    //   body: text,
    //   from: cfg.twilioPhoneNumber,
    //   to
    // });
  } catch (err) {
    status = 'failed';
    errorMsg = err.message;
    throw err;
  } finally {
    await createIntegrationLog('sms', 'sendNow', { to, text }, status, errorMsg);
  }
  return { to, text, sent: true };
}

async function scheduleSms(to, text, delayMillis) {
  await integrationsQueue.add(
    { type: 'sms', payload: { to, text } },
    { delay: delayMillis }
  );
  logger.info(`[SCHEDULED] SMS to ${to} in ${delayMillis}ms queued`);
}

module.exports = {
  postSocialNow,
  scheduleSocialPost,
  sendSmsNow,
  scheduleSms
};
