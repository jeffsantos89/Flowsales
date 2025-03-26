import axios from 'axios';
import opossum from 'opossum';
import { config } from '../config';

const sendMessageRequest = async (to: string, message: string) => {
  const response = await axios.post(
    `${config.apiUrl}/${config.phoneNumberId}/messages`,
    {
      messaging_product: 'whatsapp',
      to,
      type: 'text',
      text: { body: message },
    },
    {
      headers: {
        Authorization: `Bearer ${config.apiToken}`,
        'Content-Type': 'application/json',
      },
    }
  );
  return response.data;
};

const circuitBreakerOptions = {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 10000,
};

const breaker = new opossum(sendMessageRequest, circuitBreakerOptions);

export const sendMessage = (to: string, message: string) => breaker.fire(to, message);
