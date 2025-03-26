// src/services/smsService.ts
import axios from 'axios';

const SMS_API_URL = process.env.SMS_API_URL;
const SMS_API_KEY = process.env.SMS_API_KEY;
const SMS_API_SECRET = process.env.SMS_API_SECRET;

export const sendSMS = async (to: string, message: string) => {
  const response = await axios.post(
    `${SMS_API_URL}/send`,
    { to, message },
    {
      auth: {
        username: SMS_API_KEY,
        password: SMS_API_SECRET,
      },
    }
  );
  return response.data;
};
