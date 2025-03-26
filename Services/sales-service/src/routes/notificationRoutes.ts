import { Router } from 'express';
import { sendEmailNotification, sendSMSNotification } from '../controllers/notificationController';

const router = Router();

router.post('/email', sendEmailNotification);
router.post('/sms', sendSMSNotification);

export default router;
