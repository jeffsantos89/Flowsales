// src/integrations/crmWebhook.ts
import { handleWebhook } from './webhookHandler';

export const sendCrmWebhook = async (event: string, data: object) => {
  const url = process.env.CRM_WEBHOOK_URL || 'https://crm.example.com/webhook';
  await handleWebhook(url, { event, data });
};
