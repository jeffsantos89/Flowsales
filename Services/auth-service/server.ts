import express from 'express';
import authRoutes from './api/routes/auth';

const app = express();
app.use(express.json());
app.use('/auth', authRoutes);

app.listen(3001, () => console.log('✅ Auth-service enterprise rodando na porta 3001'));
