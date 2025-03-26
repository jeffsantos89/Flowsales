import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: 587,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

export const sendAlertEmail = async (message: string) => {
  await transporter.sendMail({
    from: process.env.EMAIL_FROM,
    to: process.env.ALERT_EMAIL,
    subject: 'Alerta de Segurança',
    text: message,
  });
};
