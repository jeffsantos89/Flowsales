import cors from 'cors';

export const corsConfig = cors({
  origin: ['https://yourdomain.com', 'https://app.yourdomain.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
});
