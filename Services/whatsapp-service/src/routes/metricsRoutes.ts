import { Router } from 'express';
import { metricsEndpoint } from '../middlewares/metrics';

const router = Router();

router.get('/metrics', metricsEndpoint);

export default router;
