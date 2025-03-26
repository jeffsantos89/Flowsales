import { segmentLeads } from '../utils/segmentationUtils';

describe('Segmentation Service', () => {
  it('should segment leads correctly', () => {
    const leads = [{ score: 10 }, { score: 20 }];
    const criteria = lead => lead.score > 15;
    const result = segmentLeads(leads, criteria);

    expect(result).toHaveLength(1);
  });
});
