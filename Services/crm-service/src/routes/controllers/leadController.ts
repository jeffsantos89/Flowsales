import { Request, Response } from 'express';
import { CreateLead } from '../../application/usecases/CreateLead';
import { KnexLeadRepository } from '../../infrastructure/database/knex/KnexLeadRepository';
import { AiTagRecommender } from '../../shared/openai/aiRecommender';
import { AuditLogger } from '../../application/services/AuditLogger';
import { LeadAuditEvent } from '../../domain/events/LeadAuditEvent';

const repo = new KnexLeadRepository();
const recommender = new AiTagRecommender();
const usecase = new CreateLead(repo, recommender);
const audit = new AuditLogger();

export const createLeadHandler = async (req: Request, res: Response) => {
  try {
    const lead = await usecase.execute(req.body);
    audit.log(new LeadAuditEvent(req.user?.username || 'anonymous', 'CREATE_LEAD', lead.id));
    res.status(201).json(lead);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
