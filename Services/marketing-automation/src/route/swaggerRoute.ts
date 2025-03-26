import express from 'express';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';

const router = express.Router();
const swaggerDocument = YAML.load('./src/docs/swagger.yaml');

router.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

export default router;
