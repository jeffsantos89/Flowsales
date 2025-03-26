// src/services/crmService.ts
import axios from 'axios';

const CRM_API_URL = process.env.CRM_API_URL || 'https://api.crm.com';

export const syncContacts = async (contacts: any[]) => {
  const response = await axios.post(`${CRM_API_URL}/contacts`, contacts);
  return response.data;
};

export const syncOpportunities = async (opportunities: any[]) => {
  const response = await axios.post(`${CRM_API_URL}/opportunities`, opportunities);
  return response.data;
};
