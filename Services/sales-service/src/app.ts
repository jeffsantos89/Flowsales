import express from 'express';
import { AppDataSource } from './config/database';
import orderRoutes from './routes/orderRoutes';
import cartRoutes from './routes/cartRoutes';
import paymentRoutes from './routes/paymentRoutes';
import { authMiddleware } from './middlewares/authMiddleware';
import { errorMiddleware } from './middlewares/errorMiddleware';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/orders', authMiddleware, orderRoutes);
app.use('/api/cart', authMiddleware, cartRoutes);
app.use('/api/payment', authMiddleware, paymentRoutes);
app.use(errorMiddleware);

AppDataSource.initialize()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Sales Service is running on http://localhost:${PORT}`);
    });
  })
  .catch((error) => console.log('Database connection error:', error));
  import express from 'express';
  import cors from 'cors';
  import morgan from 'morgan';
  import helmet from 'helmet';
  import { errorMiddleware } from './middlewares/errorMiddleware';
  import cartRoutes from './routes/cartRoutes';
  import paymentRoutes from './routes/paymentRoutes';
  import orderRoutes from './routes/orderRoutes';
  
  const app = express();
  
  app.use(cors());
  app.use(helmet());
  app.use(morgan('dev'));
  app.use(express.json());
  
  app.use('/api/cart', cartRoutes);
  app.use('/api/payments', paymentRoutes);
  app.use('/api/orders', orderRoutes);
  
  app.use(errorMiddleware);
  
  export default app;
  import express from 'express';
import bodyParser from 'body-parser';
import notificationRoutes from './routes/notificationRoutes';

const app = express();

app.use(bodyParser.json());
app.use('/api/notifications', notificationRoutes);

export default app;
import express from 'express';
import bodyParser from 'body-parser';
import webhookRoutes from './routes/webhookRoutes';

const app = express();

app.use(bodyParser.json());
app.use('/api/webhooks', webhookRoutes);

export default app;
