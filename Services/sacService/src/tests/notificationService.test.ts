import { sendNotification } from '../services/notificationService';
import { producer } from '../config/kafkaConfig';

jest.mock('../config/kafkaConfig', () => ({
  producer: {
    send: jest.fn(),
  },
}));

describe('Testes para o Notification Service', () => {
  it('Deve enviar uma notificação com sucesso', async () => {
    await sendNotification({
      email: 'cliente@exemplo.com',
      message: 'Seu ticket foi criado com sucesso!',
    });

    expect(producer.send).toHaveBeenCalledWith({
      topic: 'notifications',
      messages: [
        {
          value: JSON.stringify({
            email: 'cliente@exemplo.com',
            message: 'Seu ticket foi criado com sucesso!',
          }),
        },
      ],
    });
  });
});
