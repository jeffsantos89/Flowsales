import { mtlsMiddleware } from '../security/mtlsMiddleware';
import { Request, Response } from 'express';

describe('mTLS Middleware', () => {
  it('should return 401 if not authorized', () => {
    const req = {
      client: { authorized: false },
      socket: { getPeerCertificate: () => ({}) },
    } as unknown as Request;

    const res = {
      status: jest.fn().mockReturnThis(),
      send: jest.fn(),
    } as unknown as Response;

    mtlsMiddleware(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(401);
  });
});