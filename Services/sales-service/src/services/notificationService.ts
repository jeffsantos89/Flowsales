import nodemailer from 'nodemailer';
import twilio from 'twilio';
import { emailConfig, smsConfig } from '../config';

const transporter = nodemailer.createTransport(emailConfig);

export const sendEmail = async (to: string, subject: string, html: string) => {
  await transporter.sendMail({
    from: emailConfig.auth.user,
    to,
    subject,
    html,
  });
};

const smsClient = twilio(smsConfig.accountSid, smsConfig.authToken);

export const sendSMS = async (to: string, message: string) => {
  await smsClient.messages.create({
    body: message,
    from: smsConfig.from,
    to,
  });
};
