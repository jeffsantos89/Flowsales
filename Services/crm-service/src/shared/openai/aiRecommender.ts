import axios from 'axios';

export class AiTagRecommender {
  async recommendScore(input: { name: string; email: string }) {
    const res = await axios.post('http://ai-service:3005/score', { input });
    return res.data?.score || 0;
  }
}
