import { wafMiddleware } from '../security/wafMiddleware';
import { Request, Response } from 'express';

describe('WAF Middleware', () => {
  it('should block bad bots', () => {
    const req = { headers: { 'user-agent': 'BadBot' } } as Request;
    const res = {
      status: jest.fn().mockReturnThis(),
      send: jest.fn(),
    } as unknown as Response;

    wafMiddleware(req, res, jest.fn());
    expect(res.status).toHaveBeenCalledWith(403);
  });
});
