import nodemailer from 'nodemailer';

export const emailConfig = {
  host: process.env.EMAIL_HOST || 'smtp.mailtrap.io',
  port: parseInt(process.env.EMAIL_PORT || '587', 10),
  secure: false,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
};

export const transporter = nodemailer.createTransport(emailConfig);
