import { Request, Response, Router } from 'express';
import { redisClient } from '../services/redisService';
import { getKafkaHealth } from '../services/kafkaHealthCheck';
import { dataSource } from '../config/database';
import { Logger } from '../utils/logger'; // Assumindo que você tem um logger configurado

interface HealthCheck {
    status: 'ok' | 'error';
    details: string;
    timestamp: string;
}

interface HealthResponse {
    status: 'ok' | 'error';
    checks: {
        database: HealthCheck;
        redis: HealthCheck;
        kafka: HealthCheck;
    };
    timestamp: string;
    version: string;
}

class HealthController {
    private static readonly TIMEOUT = 5000; // 5 seconds timeout

    private static async checkDatabase(): Promise<HealthCheck> {
        try {
            const isHealthy = dataSource.isInitialized;
            return {
                status: isHealthy ? 'ok' : 'error',
                details: isHealthy ? 'Connected' : 'Disconnected',
                timestamp: new Date().toISOString(),
            };
        } catch (error) {
            Logger.error('Database health check failed:', error);
            return {
                status: 'error',
                details: 'Database check failed',
                timestamp: new Date().toISOString(),
            };
        }
    }

    private static async checkRedis(): Promise<HealthCheck> {
        try {
            const result = await Promise.race([
                redisClient.ping(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Redis timeout')), this.TIMEOUT)
                ),
            ]);
            
            return {
                status: result === 'PONG' ? 'ok' : 'error',
                details: result === 'PONG' ? 'Connected' : 'Invalid response',
                timestamp: new Date().toISOString(),
            };
        } catch (error) {
            Logger.error('Redis health check failed:', error);
            return {
                status: 'error',
                details: error instanceof Error ? error.message : 'Redis check failed',
                timestamp: new Date().toISOString(),
            };
        }
    }

    private static async checkKafka(): Promise<HealthCheck> {
        try {
            const isHealthy = await Promise.race([
                getKafkaHealth(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Kafka timeout')), this.TIMEOUT)
                ),
            ]);

            return {
                status: isHealthy ? 'ok' : 'error',
                details: isHealthy ? 'Connected' : 'Disconnected',
                timestamp: new Date().toISOString(),
            };
        } catch (error) {
            Logger.error('Kafka health check failed:', error);
            return {
                status: 'error',
                details: error instanceof Error ? error.message : 'Kafka check failed',
                timestamp: new Date().toISOString(),
            };
        }
    }

    public static async getHealth(_req: Request, res: Response): Promise<void> {
        try {
            const [database, redis, kafka] = await Promise.all([
                this.checkDatabase(),
                this.checkRedis(),
                this.checkKafka(),
            ]);

            const allOk = [database, redis, kafka]
                .every(check => check.status === 'ok');

            const response: HealthResponse = {
                status: allOk ? 'ok' : 'error',
                checks: {
                    database,
                    redis,
                    kafka,
                },
                timestamp: new Date().toISOString(),
                version: process.env.APP_VERSION || '1.0.0',
            };

            res.status(allOk ? 200 : 500).json(response);
        } catch (error) {
            Logger.error('Health check failed:', error);
            res.status(500).json({
                status: 'error',
                details: 'Health check failed',
                timestamp: new Date().toISOString(),
            });
        }
    }
}

const router = Router();
router.get('/healthz', HealthController.getHealth);

export default router;
