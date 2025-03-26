require('dotenv').config();
const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/auth');
const logger = require('./logger');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/auth', authRoutes);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`Auth service running on port ${PORT}`);
});
