// src/backup/backupService.ts
import { exec } from 'child_process';
import { logger } from '../utils/logger';

export const runBackup = () => {
  const backupCommand = `pg_dump -h localhost -U postgres -F c flowsale > ./backups/flowsale_$(date +%F).sql`;
  exec(backupCommand, (err, stdout, stderr) => {
    if (err) {
      logger.error('Backup failed:', stderr);
    } else {
      logger.info('Backup successful:', stdout);
    }
  });
};
