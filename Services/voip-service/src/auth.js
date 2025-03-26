const logger = require('./logger');

const USER = process.env.AUTH_USER || 'admin';
const PASS = process.env.AUTH_PASS || 'admin123';

function auth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    logger.warn('No authorization header');
    return res.status(401).json({ error: 'No authorization header' });
  }
  const base64 = authHeader.split(' ')[1] || '';
  const [user, pass] = Buffer.from(base64, 'base64').toString().split(':');
  if (user === USER && pass === PASS) {
    return next();
  }
  logger.warn(`Auth failed for user=${user}`);
  return res.status(401).json({ error: 'Invalid credentials' });
}

module.exports = auth;
