export class LeadAuditEvent {
  constructor(
    public user: string,
    public action: string,
    public entityId: string,
    public timestamp: Date = new Date()
  ) {}
}
