import { Request, Response } from 'express';
import { CreateLead } from '../../application/usecases/CreateLead';
import { KnexLeadRepository } from '../../infrastructure/database/knex/KnexLeadRepository';
import { AiTagRecommender } from '../../shared/openai/aiRecommender';

const repo = new KnexLeadRepository();
const recommender = new AiTagRecommender();
const usecase = new CreateLead(repo, recommender);

export const createLeadHandler = async (req: Request, res: Response) => {
  try {
    const lead = await usecase.execute(req.body);
    res.status(201).json(lead);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
