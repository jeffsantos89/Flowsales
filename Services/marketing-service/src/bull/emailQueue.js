const Bull = require('bull');
const logger = require('../logger');

const emailQueue = new Bull('emailQueue', {
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || undefined
  }
});

// Definimos o “processador” de emails
emailQueue.process(async (job) => {
  const { transporter, mailOptions } = job.data;
  const info = await transporter.sendMail(mailOptions);
  logger.info(`[BULL] Email sent to ${mailOptions.to} messageId=${info.messageId}`);
  return info;
});

module.exports = emailQueue;
