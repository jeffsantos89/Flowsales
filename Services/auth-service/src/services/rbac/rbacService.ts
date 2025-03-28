const permissionsByRole = {
  admin: ['read', 'write', 'delete'],
  user: ['read'],
  manager: ['read', 'write']
};

export const hasPermission = (role: string, permission: string): boolean => {
  const allowed = permissionsByRole[role] || [];
  return allowed.includes(permission);
};
