import { runBackup } from '../backup/backupService';
import { exec } from 'child_process';

jest.mock('child_process');

describe('Backup Service', () => {
  it('should run backup command', () => {
    const execMock = jest.spyOn(exec, 'exec').mockImplementation((_, cb) => cb(null, 'Backup done!', ''));
    runBackup();
    expect(execMock).toHaveBeenCalled();
  });
});
