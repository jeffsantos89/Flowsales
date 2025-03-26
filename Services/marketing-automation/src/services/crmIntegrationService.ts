// src/services/crmIntegrationService.ts
import axios from 'axios';
import { logger } from '../utils/logger';

const CRM_API_URL = process.env.CRM_API_URL || 'https://crm.example.com/api';

export const syncContacts = async () => {
  try {
    const { data } = await axios.get(`${CRM_API_URL}/contacts`);
    return data;
  } catch (error) {
    logger.error('Error syncing contacts:', error);
    throw error;
  }
};
