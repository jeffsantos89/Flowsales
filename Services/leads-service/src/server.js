require('dotenv').config();
const express = require('express');
const logger = require('./logger');
const leadsRoutes = require('./routes/leads');

const app = express();
app.use(express.json());

// Rotas
app.use('/leads', leadsRoutes);

// Sobe o servidor
const PORT = process.env.PORT || 3003;
app.listen(PORT, () => {
  logger.info(`Leads service running on port ${PORT}`);
});