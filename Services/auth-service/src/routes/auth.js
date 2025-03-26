const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const logger = require('../logger');
const { createUser, findUserByEmail } = require('../models/userModel');

router.post('/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;
    const existing = await findUserByEmail(email);
    if (existing) {
      return res.status(400).json({ error: 'User already exists' });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    await createUser(name, email, hashedPassword);
    logger.info(`New user registered: ${email}`);
    return res.json({ message: 'User registered!' });
  } catch (err) {
    logger.error(err);
    return res.status(500).json({ error: 'Error registering user' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await findUserByEmail(email);
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }
    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ error: 'Incorrect password' });
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, {
      expiresIn: '1h'
    });
    return res.json({ token });
  } catch (err) {
    logger.error(err);
    return res.status(500).json({ error: 'Error logging in' });
  }
});

module.exports = router;
