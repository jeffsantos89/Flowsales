
import { Router, Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';

const router = Router();
const automacoes = [];

router.post('/automacoes', (req: Request, res: Response) => {
  const { nome, descricao, nodes, edges } = req.body;
  const novaAutomacao = {
    id: uuidv4(),
    nome,
    descricao,
    nodes,
    edges,
    status: 'ativo',
    criadoEm: new Date()
  };
  automacoes.push(novaAutomacao);
  res.status(201).json(novaAutomacao);
});

router.get('/automacoes', (req: Request, res: Response) => {
  res.status(200).json(automacoes);
});

router.get('/automacoes/:id', (req: Request, res: Response) => {
  const automacao = automacoes.find(a => a.id === req.params.id);
  if (!automacao) {
    return res.status(404).json({ message: 'Automação não encontrada' });
  }
  res.status(200).json(automacao);
});

export default router;
    