
// src/services/templateService.ts
import handlebars from 'handlebars';
import { logger } from '../utils/logger';

export const compileTemplate = (templateString: string, data: object) => {
  try {
    const template = handlebars.compile(templateString);
    return template(data);
  } catch (error) {
    logger.error('Error compiling template:', error);
    throw error;
  }
};
