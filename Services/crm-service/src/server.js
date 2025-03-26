require('dotenv').config();
const express = require('express');
const logger = require('./logger');
const contactsRoutes = require('./routes/contacts');
const opportunitiesRoutes = require('./routes/opportunities');
const ticketsRoutes = require('./routes/tickets');

const app = express();
app.use(express.json());

// Rotas CRM
app.use('/contacts', contactsRoutes);
app.use('/opportunities', opportunitiesRoutes);
app.use('/tickets', ticketsRoutes);

const PORT = process.env.PORT || 3004;
app.listen(PORT, () => {
  logger.info(`CRM service running on port ${PORT}`);
});