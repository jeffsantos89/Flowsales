const auditLog: any[] = [];

export const recordAudit = (username: string, action: string, metadata: any = {}) => {
  auditLog.push({
    username,
    action,
    timestamp: new Date().toISOString(),
    metadata
  });
  console.log("📘 Auditoria:", username, action, metadata);
};
