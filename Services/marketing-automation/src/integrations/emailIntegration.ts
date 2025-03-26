// src/integrations/emailIntegration.ts
import nodemailer from 'nodemailer';
import { logger } from '../utils/logger';

const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: 587,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

export const sendEmail = async (to: string, subject: string, html: string) => {
  try {
    await transporter.sendMail({ from: process.env.EMAIL_FROM, to, subject, html });
    logger.info(`Email sent to ${to}`);
  } catch (error) {
    logger.error('Error sending email:', error);
    throw error;
  }
};
