// src/ai/trainModel.ts
import * as tf from '@tensorflow/tfjs-node';
import { logger } from '../utils/logger';

export const trainModel = async () => {
  const model = tf.sequential();
  model.add(tf.layers.dense({ inputShape: [10], units: 16, activation: 'relu' }));
  model.add(tf.layers.dense({ units: 1, activation: 'sigmoid' }));

  model.compile({
    optimizer: tf.train.adam(),
    loss: 'binaryCrossentropy',
    metrics: ['accuracy'],
  });

  const data = tf.tensor2d([[1, 0, 0], [0, 1, 1], [1, 1, 0]]);
  const labels = tf.tensor2d([[0], [1], [0]]);

  await model.fit(data, labels, {
    epochs: 10,
    batchSize: 32,
    verbose: 1,
  });

  await model.save('file://./models/churn-model');
  logger.info('Model trained and saved.');
};
