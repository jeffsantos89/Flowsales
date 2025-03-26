// src/ai/predictionService.ts
import * as tf from '@tensorflow/tfjs';
import { logger } from '../utils/logger';

export const predictChurn = async (features: number[]) => {
  const model = await tf.loadLayersModel('file://./models/churn-model.json');
  const input = tf.tensor2d([features]);
  const prediction = model.predict(input) as tf.Tensor;
  const result = prediction.dataSync();
  logger.info(`Churn Prediction: ${result[0] > 0.5 ? 'Churn' : 'No Churn'}`);
  return result[0] > 0.5 ? 'Churn' : 'No Churn';
};
