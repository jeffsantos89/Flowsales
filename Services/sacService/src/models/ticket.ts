import { v4 as uuidv4 } from 'uuid';
import { Database } from './database'; // Supondo que você tenha um módulo de banco de dados

export class Ticket {
    id: string;
    title: string;
    description: string;
    createdAt: Date;
    updatedAt: Date;

    constructor({ title, description }: { title: string; description: string }) {
        this.id = uuidv4();
        this.title = title;
        this.description = description;
        this.createdAt = new Date();
        this.updatedAt = new Date();
    }

    static async findById(ticketId: string): Promise<Ticket | null> {
        try {
            const result = await Database.query('SELECT * FROM tickets WHERE id = $1', [ticketId]);
            if (result.rows.length === 0) {
                return null;
            }
            const ticketData = result.rows[0];
            return new Ticket({
                title: ticketData.title,
                description: ticketData.description,
            });
        } catch (error) {
            console.error('Error finding ticket by ID:', error);
            throw new Error('Database query failed');
        }
    }

    async save(): Promise<void> {
        try {
            await Database.query(
                'INSERT INTO tickets (id, title, description, created_at, updated_at) VALUES ($1, $2, $3, $4, $5)',
                [this.id, this.title, this.description, this.createdAt, this.updatedAt]
            );
        } catch (error) {
            console.error('Error saving ticket:', error);
            throw new Error('Database insert failed');
        }
    }

    async update(fields: Partial<{ title: string; description: string }>): Promise<void> {
        try {
            if (fields.title) this.title = fields.title;
            if (fields.description) this.description = fields.description;
            this.updatedAt = new Date();

            await Database.query(
                'UPDATE tickets SET title = $1, description = $2, updated_at = $3 WHERE id = $4',
                [this.title, this.description, this.updatedAt, this.id]
            );
        } catch (error) {
            console.error('Error updating ticket:', error);
            throw new Error('Database update failed');
        }
    }
}