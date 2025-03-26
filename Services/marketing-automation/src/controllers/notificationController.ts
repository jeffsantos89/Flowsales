// src/controllers/notificationController.ts
import { Request, Response } from 'express';
import { sendNotification } from '../services/notificationService';
import { responseHandler } from '../utils/responseHandler';

export const sendUserNotification = async (req: Request, res: Response) => {
  try {
    const { userId, message } = req.body;
    await sendNotification(userId, message);
    responseHandler(res, 200, 'Notification sent successfully');
  } catch (error) {
    responseHandler(res, 500, 'Error sending notification', { error: error.message });
  }
};
