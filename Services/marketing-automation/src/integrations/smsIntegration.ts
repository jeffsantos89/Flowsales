// src/integrations/smsIntegration.ts
import axios from 'axios';
import { logger } from '../utils/logger';

export const sendSms = async (phoneNumber: string, message: string) => {
  try {
    const response = await axios.post('https://sms-provider.com/api/send', {
      to: phoneNumber,
      message,
    });
    logger.info(`SMS sent to ${phoneNumber} with status ${response.status}`);
  } catch (error) {
    logger.error('Error sending SMS:', error);
    throw error;
  }
};
