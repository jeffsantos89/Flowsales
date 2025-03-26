import { Router } from 'express';
const router = Router();

router.get('/', (req, res) => res.send('Workflows list'));

export default router;
