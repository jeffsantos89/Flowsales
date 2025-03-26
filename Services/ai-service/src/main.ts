import "reflect-metadata";
import express from "express";
import helmet from "helmet";
import cors from "cors";
import compression from "compression";
import rateLimit from "express-rate-limit";
import { createConnection } from "typeorm";
import { logger } from "./utils/logger";
import { redisClient } from "./cache/redisClient";
import { configureKafka } from "./events/kafkaConfig";
import { routes } from "./routes";
import { errorHandler } from "./middleware/errorHandler";
import { validateEnv } from "./utils/validateEnv";
import swaggerUi from "swagger-ui-express";
import swaggerDocument from "./swagger.json";
import "./monitoring/observability"; // Inicializa Prometheus, OpenTelemetry

validateEnv();

const app = express();
const PORT = process.env.PORT || 4000;

// Segurança: Helmet protege contra vulnerabilidades comuns
app.use(helmet());

// Permissões de CORS
app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(",") || "*",
    credentials: true
}));

// Compressão para otimizar desempenho
app.use(compression());

// Rate Limiting para evitar ataques DoS
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 1000,
    message: "Muitas requisições. Tente novamente mais tarde.",
});
app.use(limiter);

// Middleware para analisar JSON no corpo das requisições
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Documentação da API
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Configuração das Rotas
app.use("/api", routes);

// Middleware global de tratamento de erros
app.use(errorHandler);

// Conectar ao Banco de Dados (PostgreSQL via TypeORM)
createConnection()
    .then(() => logger.info("📌 Conectado ao Banco de Dados"))
    .catch((error) => logger.error("❌ Erro ao conectar no Banco de Dados", error));

// Conectar ao Redis
redisClient.connect().then(() => {
    logger.info("📌 Conectado ao Redis");
}).catch(error => {
    logger.error("❌ Erro ao conectar ao Redis", error);
});

// Configurar Kafka (Mensageria)
configureKafka();

// Inicializar Servidor
app.listen(PORT, () => {
    logger.info(`🚀 AI-SERVICE rodando na porta ${PORT}`);
});
