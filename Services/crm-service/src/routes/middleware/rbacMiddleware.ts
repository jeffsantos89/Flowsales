export const checkRole = (role: string) => {
  return (req, res, next) => {
    const userRole = req.user?.role;
    if (!userRole || (userRole !== role && userRole !== 'admin')) {
      return res.status(403).json({ error: 'Acesso negado: role insuficiente' });
    }
    next();
  };
};
