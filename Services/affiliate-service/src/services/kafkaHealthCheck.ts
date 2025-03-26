import { kafka } from '../config/kafkaConfig';
import { Admin } from 'kafkajs';
import { Logger } from '../utils/logger'; // Você precisará implementar ou usar uma lib de logging

interface KafkaHealthStatus {
    isHealthy: boolean;
    details: {
        connected: boolean;
        topicsAccessible: boolean;
        responseTimeMs: number;
        lastChecked: Date;
        error?: string;
    };
}

export class KafkaHealthChecker {
    private static readonly TIMEOUT_MS = 5000;
    private readonly logger: Logger;
    private admin: Admin | null = null;

    constructor(logger: Logger) {
        this.logger = logger;
    }

    public async getHealth(): Promise<KafkaHealthStatus> {
        const startTime = Date.now();
        const status: KafkaHealthStatus = {
            isHealthy: false,
            details: {
                connected: false,
                topicsAccessible: false,
                responseTimeMs: 0,
                lastChecked: new Date(),
            },
        };

        try {
            this.admin = kafka.admin();

            // Adiciona timeout para a conexão
            const connectPromise = this.admin.connect();
            await Promise.race([
                connectPromise,
                new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Connection timeout')), KafkaHealthChecker.TIMEOUT_MS)
                ),
            ]);

            status.details.connected = true;

            // Verifica acesso aos tópicos
            await this.admin.listTopics();
            status.details.topicsAccessible = true;
            status.isHealthy = true;

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            status.details.error = errorMessage;
            this.logger.error('Kafka health check failed', { error: errorMessage });

        } finally {
            if (this.admin) {
                try {
                    await this.admin.disconnect();
                } catch (error) {
                    this.logger.warn('Error disconnecting from Kafka', { error });
                }
            }

            status.details.responseTimeMs = Date.now() - startTime;
            this.logger.info('Kafka health check completed', { status });
        }

        return status;
    }

    public static async checkHealth(logger: Logger): Promise<KafkaHealthStatus> {
        const checker = new KafkaHealthChecker(logger);
        return checker.getHealth();
    }
}
