import mongoose, { Schema, Document, Model } from 'mongoose';

interface ITicket extends Document {
  title: string;
  description: string;
  status: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ITicketModel extends Model<ITicket> {
  findByStatus(status: string): Promise<ITicket[]>;
}

const ticketSchema = new Schema<ITicket>(
  {
    title: { type: String, required: true, trim: true },
    description: { type: String, required: true, trim: true },
    status: { type: String, enum: ['open', 'in_progress', 'closed'], default: 'open' },
  },
  {
    timestamps: true,
  }
);

ticketSchema.index({ status: 1 });

ticketSchema.statics.findByStatus = function (status: string) {
  return this.find({ status });
};

export const Ticket = mongoose.model<ITicket, ITicketModel>('Ticket', ticketSchema);
