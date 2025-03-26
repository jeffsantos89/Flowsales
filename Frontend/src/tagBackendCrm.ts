
import { Router, Request, Response } from 'express';

const router = Router();
const tags = [];

router.post('/tags', (req: Request, res: Response) => {
  const { nome, origem, lead_ids } = req.body;
  const newTag = { id: tags.length + 1, nome, origem, lead_ids, criadoEm: new Date() };
  tags.push(newTag);
  res.status(201).json(newTag);
});

router.put('/tags/:id/leads', (req: Request, res: Response) => {
  const tag = tags.find(t => t.id === parseInt(req.params.id));
  if (!tag) {
    return res.status(404).json({ message: 'Tag não encontrada' });
  }
  tag.lead_ids = [...tag.lead_ids, ...req.body.leads];
  res.status(200).json(tag);
});

router.get('/tags', (req: Request, res: Response) => {
  res.status(200).json(tags);
});

export default router;
    