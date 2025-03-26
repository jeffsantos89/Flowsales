import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';
import { config } from '../config';

interface SwaggerConfig {
  title: string;
  version: string;
  description: string;
  contact?: {
    name?: string;
    email?: string;
    url?: string;
  };
  license?: {
    name: string;
    url: string;
  };
}

class SwaggerSetup {
  private readonly swaggerSpec: object;

  constructor(private config: SwaggerConfig) {
    this.swaggerSpec = this.createSwaggerSpec();
  }

  private createSwaggerSpec(): object {
    const options: swaggerJsdoc.Options = {
      definition: {
        openapi: '3.0.0',
        info: {
          title: this.config.title,
          version: this.config.version,
          description: this.config.description,
          contact: this.config.contact,
          license: this.config.license,
        },
        servers: [
          {
            url: config.apiUrl || 'http://localhost:3333/api/v1',
            description: 'API Server',
          },
          {
            url: config.stagingUrl || 'https://staging-api.flowsale.com/api/v1',
            description: 'Staging Server',
          },
          {
            url: config.productionUrl || 'https://api.flowsale.com/api/v1',
            description: 'Production Server',
          },
        ],
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
              bearerFormat: 'JWT',
            },
          },
        },
        security: [
          {
            bearerAuth: [],
          },
        ],
      },
      apis: ['src/routes/*.ts', 'src/models/*.ts', 'src/controllers/*.ts'],
    };

    return swaggerJsdoc(options);
  }

  public setup(app: Express): void {
    if (!app) {
      throw new Error('Express app instance is required');
    }

    const swaggerUiOptions = {
      explorer: true,
      customCss: '.swagger-ui .topbar { display: none }',
      customSiteTitle: this.config.title,
    };

    app.use('/api-docs', swaggerUi.serve);
    app.get('/api-docs', swaggerUi.setup(this.swaggerSpec, swaggerUiOptions));

    // Endpoint para baixar a especificação do Swagger em formato JSON
    app.get('/api-docs.json', (req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.send(this.swaggerSpec);
    });
  }
}

export const createSwaggerSetup = (config: SwaggerConfig) => {
  return new SwaggerSetup(config);
};
