import openaiClient from '../client/openaiClient';

export const runChurnPrediction = async (leadData: any) => {
  const response = await openaiClient.post('/predict/churn', { input: leadData });
  return response.data;
};
