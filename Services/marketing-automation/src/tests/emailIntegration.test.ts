import { sendEmail } from '../integrations/emailIntegration';
import nodemailer from 'nodemailer';

jest.mock('nodemailer');

describe('Email Integration', () => {
  const sendMailMock = jest.fn();

  beforeAll(() => {
    (nodemailer.createTransport as jest.Mock).mockReturnValue({
      sendMail: sendMailMock,
    });
  });

  it('should send an email', async () => {
    await sendEmail('test@example.com', 'Test', '<h1>Test</h1>');
    expect(sendMailMock).toHaveBeenCalledTimes(1);
    expect(sendMailMock).toHaveBeenCalledWith({
      from: expect.any(String),
      to: 'test@example.com',
      subject: 'Test',
      html: '<h1>Test</h1>',
    });
  });
});
