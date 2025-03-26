import { Router } from 'express';
import { createCampaign } from '../controllers/campaignController';
const router = Router();

router.post('/', createCampaign);

export default router;
