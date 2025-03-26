const nodemailer = require('nodemailer');
const logger = require('../logger');
const emailQueue = require('../bull/emailQueue');

async function sendEmailNow({ from, to, subject, text, html }) {
  const transporter = createTransport();
  const info = await transporter.sendMail({ from, to, subject, text, html });
  logger.info(`[IMMEDIATE] Email sent to ${to}, messageId=${info.messageId}`);
  return info;
}

async function scheduleEmail({ from, to, subject, text, html, delayMillis }) {
  const transporter = createTransport();
  await emailQueue.add(
    { mailOptions: { from, to, subject, text, html }, transporter },
    { delay: delayMillis }
  );
  logger.info(`[SCHEDULED] Email to ${to} in ${delayMillis}ms queued`);
}

function createTransport() {
  const { EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS } = process.env;
  return nodemailer.createTransport({
    host: EMAIL_HOST,
    port: Number(EMAIL_PORT),
    secure: false, 
    auth: {
      user: EMAIL_USER,
      pass: EMAIL_PASS
    }
  });
}

module.exports = {
  sendEmailNow,
  scheduleEmail
};
