const jwt = require('jsonwebtoken');
const logger = require('./logger');

function jwtAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    logger.warn('No authorization header');
    return res.status(401).json({ error: 'No authorization header' });
  }
  const token = authHeader.split(' ')[1];
  if (!token) {
    logger.warn('Token not provided');
    return res.status(401).json({ error: 'Token not provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // anexa payload do JWT para uso posterior
    return next();
  } catch (err) {
    logger.warn('Invalid token', { error: err.message });
    return res.status(401).json({ error: 'Invalid token' });
  }
}

module.exports = jwtAuth;
