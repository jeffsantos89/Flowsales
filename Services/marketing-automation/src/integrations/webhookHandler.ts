// src/integrations/webhookHandler.ts
import axios from 'axios';
import { logger } from '../utils/logger';

export const handleWebhook = async (url: string, payload: object) => {
  try {
    const response = await axios.post(url, payload);
    logger.info(`Webhook sent to ${url} with status ${response.status}`);
  } catch (error) {
    logger.error('Error sending webhook:', error);
    throw error;
  }
};
