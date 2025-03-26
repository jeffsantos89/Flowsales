const jwt = require('jsonwebtoken');
const logger = require('./logger');
const cfg = require('../config');

function jwtAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    logger.warn('Nenhum header de autorização presente');
    return res.status(401).json({ error: 'Acesso não autorizado' });
  }
  const token = authHeader.split(' ')[1];
  if (!token) {
    logger.warn('Token não fornecido');
    return res.status(401).json({ error: 'Token não fornecido' });
  }
  try {
    const decoded = jwt.verify(token, cfg.jwtSecret);
    req.user = decoded;
    return next();
  } catch (err) {
    logger.warn('Token inválido', { error: err.message });
    return res.status(401).json({ error: 'Token inválido' });
  }
}

module.exports = jwtAuth;
