import { LeadAuditEvent } from '../../domain/events/LeadAuditEvent';

const auditLog: LeadAuditEvent[] = [];

export class AuditLogger {
  log(event: LeadAuditEvent) {
    auditLog.push(event);
    console.log("📘 AUDIT:", event);
  }

  getAll() {
    return auditLog;
  }
}
