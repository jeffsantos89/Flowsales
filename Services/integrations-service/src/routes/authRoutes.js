const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const logger = require('../logger');
const cfg = require('../../config');

// Exemplo de usuários mock
const users = [
  { id: 1, username: 'admin', password: 'admin123' },
  { id: 2, username: 'user', password: 'user123' }
];

router.post('/login', (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username && u.password === password);
  if (!user) {
    logger.warn(`Login failed for username=${username}`);
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const token = jwt.sign({ userId: user.id }, cfg.jwtSecret, {
    expiresIn: cfg.jwtExpiresIn
  });
  logger.info(`User ${username} logged in`);
  res.json({ token });
});

module.exports = router;
