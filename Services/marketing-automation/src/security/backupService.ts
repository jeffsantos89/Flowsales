// src/security/backupService.ts
import { exec } from 'child_process';
import { encryptData } from './encryptionService';
import { writeFileSync } from 'fs';

export const runEncryptedBackup = () => {
  exec('pg_dump -U postgres -F c flowsale > ./backups/flowsale.sql', (err) => {
    if (err) {
      console.error('Backup failed:', err);
    } else {
      const backupData = require('fs').readFileSync('./backups/flowsale.sql');
      const encryptedBackup = encryptData(backupData.toString());
      writeFileSync('./backups/flowsale_encrypted.sql', encryptedBackup.encryptedData);
      console.log('Encrypted backup created successfully.');
    }
  });
};
