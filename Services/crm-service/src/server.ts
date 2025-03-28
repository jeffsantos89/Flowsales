import express from 'express';
import leadRoutes from './interfaces/routes/leadRoutes';
import { tracingMiddleware } from './interfaces/middleware/tracingMiddleware';
import './infrastructure/observability/tracing';

const app = express();
app.use(express.json());
app.use(tracingMiddleware);
app.use('/crm', leadRoutes);

app.listen(3003, () => console.log('🚀 CRM Enterprise com observabilidade na porta 3003'));
