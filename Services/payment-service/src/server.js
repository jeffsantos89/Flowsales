require('dotenv').config();
const express = require('express');
const paymentRoutes = require('./routes/payment');
const logger = require('./logger');

const app = express();
app.use(express.json());

app.use('/payment', paymentRoutes);

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  logger.info(`Payment service running on port ${PORT}`);
});