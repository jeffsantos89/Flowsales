import { getContacts, createContact } from '../integrations/crmIntegration';
import axios from 'axios';

jest.mock('axios');

describe('CRM Integration', () => {
  it('should fetch contacts', async () => {
    const contacts = [{ id: 1, name: 'John Doe' }];
    (axios.get as jest.Mock).mockResolvedValue({ data: contacts });

    const result = await getContacts();
    expect(result).toEqual(contacts);
  });

  it('should create a contact', async () => {
    const contact = { id: 2, name: 'Jane Doe' };
    (axios.post as jest.Mock).mockResolvedValue({ data: contact });

    const result = await createContact(contact);
    expect(result).toEqual(contact);
  });
});