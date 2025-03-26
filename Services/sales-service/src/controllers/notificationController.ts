
import { Request, Response } from 'express';
import { sendEmail, sendSMS } from '../services/notificationService';

export const sendEmailNotification = async (req: Request, res: Response) => {
  try {
    const { to, subject, message } = req.body;
    await sendEmail(to, subject, message);
    res.status(200).json({ message: 'Email enviado com sucesso!' });
  } catch (error) {
    console.error('Erro ao enviar email:', error);
    res.status(500).json({ message: 'Erro ao enviar email' });
  }
};

export const sendSMSNotification = async (req: Request, res: Response) => {
  try {
    const { to, message } = req.body;
    await sendSMS(to, message);
    res.status(200).json({ message: 'SMS enviado com sucesso!' });
  } catch (error) {
    console.error('Erro ao enviar SMS:', error);
    res.status(500).json({ message: 'Erro ao enviar SMS' });
  }
};
