import { producer } from '../config/kafkaConfig';
import { logger } from '../utils/logger';
import * as Joi from 'joi';

interface Notification {
  email: string;
  message: string;
}

const notificationSchema = Joi.object({
  email: Joi.string().email().required(),
  message: Joi.string().min(1).required(),
});

export const sendNotification = async (notification: Notification, retries = 3) => {
  const { error } = notificationSchema.validate(notification);
  if (error) {
    logger.error('Invalid notification data:', error.details);
    throw new Error('Invalid notification data');
  }

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      await producer.send({
        topic: 'notifications',
        messages: [
          {
            value: JSON.stringify(notification),
          },
        ],
      });
      logger.info(`Notification sent to ${notification.email} on attempt ${attempt}`);
      return;
    } catch (error) {
      logger.error(`Error sending notification on attempt ${attempt}:`, error);
      if (attempt === retries) {
        throw new Error('Failed to send notification after multiple attempts');
      }
    }
  }
};
