// src/analytics/predictChurn.ts
import { fetchLeadData } from '../repository/leadRepository';
import { LogisticRegression } from 'ml-regression';

export const predictChurn = async (leadId: number) => {
  const leadData = await fetchLeadData(leadId);

  const model = new LogisticRegression();
  model.train(leadData.features, leadData.labels);

  const prediction = model.predict(leadData.newFeatures);
  return prediction > 0.5 ? 'high risk' : 'low risk';
};
