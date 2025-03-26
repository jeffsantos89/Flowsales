import { sendEvent } from '../events/kafkaProducer';
import { producer } from '../config/kafkaConfig';

jest.mock('../config/kafkaConfig');

describe('Kafka Producer', () => {
  const sendMock = jest.fn();

  beforeAll(() => {
    (producer.send as jest.Mock).mockImplementation(sendMock);
  });

  it('should send an event to Kafka', async () => {
    await sendEvent('test-topic', { message: 'Test' });
    expect(sendMock).toHaveBeenCalledWith({
      topic: 'test-topic',
      messages: [{ value: JSON.stringify({ message: 'Test' }) }],
    });
  });
});
