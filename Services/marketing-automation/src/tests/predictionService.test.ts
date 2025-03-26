import { predictChurn } from '../ai/predictionService';

jest.mock('@tensorflow/tfjs', () => ({
  loadLayersModel: jest.fn().mockResolvedValue({
    predict: () => ({
      dataSync: () => [0.7],
    }),
  }),
}));

describe('Prediction Service', () => {
  it('should predict churn', async () => {
    const result = await predictChurn([1, 0, 0, 1, 0, 0, 1, 0, 1, 0]);
    expect(result).toBe('Churn');
  });
});
