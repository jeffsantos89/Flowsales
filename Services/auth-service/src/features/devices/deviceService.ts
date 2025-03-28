import crypto from 'crypto';
const trustedDevices: Record<string, string[]> = {};

export const generateDeviceId = (userAgent: string, ip: string): string => {
  return crypto.createHash('sha256').update(userAgent + ip).digest('hex');
};

export const isTrustedDevice = (username: string, deviceId: string): boolean => {
  return trustedDevices[username]?.includes(deviceId) ?? false;
};

export const saveTrustedDevice = (username: string, deviceId: string) => {
  trustedDevices[username] = [...(trustedDevices[username] || []), deviceId];
};
