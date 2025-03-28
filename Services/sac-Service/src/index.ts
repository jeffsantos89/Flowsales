import * as express from 'express';
import ticketRoutes from './routes/ticketRoutes';
import { DatabaseConfig } from './config/dbConfig'; // Ou importação correta
import * as dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(express.json());

// Routes
app.use('/api', ticketRoutes);

// Database connection
const connectToDatabase = async () => {
  try {
    await DatabaseConfig.initialize(); // Ou método correto do seu módulo
    console.log('Database connected successfully');
  } catch (error) {
    console.error('Database connection failed:', error);
    throw error;
  }
};

connectToDatabase().then(() => {
  // Start server
  app.listen(PORT, () => {
    console.log(`SAC Service running on port ${PORT}`);
  });
}).catch((error) => {
  console.error('Failed to connect to the database:', error);
  process.exit(1);
});

export { app };
