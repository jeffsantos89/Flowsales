import { Lead } from '../../domain/entities/Lead';
import { LeadRepository } from '../../domain/repositories/LeadRepository';
import { AiTagRecommender } from '../../shared/openai/aiRecommender';

export class CreateLead {
  constructor(
    private readonly leadRepo: LeadRepository,
    private readonly recommender: AiTagRecommender
  ) {}

  async execute(data: { name: string; email: string }) {
    const lead = new Lead(Date.now().toString(), data.name, data.email);
    lead.score = await this.recommender.recommendScore(data);
    await this.leadRepo.save(lead);
    return lead;
  }
}
