import { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-toastify'; // Adicione react-toastify para notificações
import * as z from 'zod'; // Adicione Zod para validação
import api from '../services/api';
import { Loading } from '../components/Loading'; // Crie este componente
import { ErrorBoundary } from '../components/ErrorBoundary'; // Crie este componente

// Schema de validação
const affiliateSchema = z.object({
    name: z.string().min(3, 'Nome deve ter no mínimo 3 caracteres'),
    email: z.string().email('Email inválido'),
    code: z.string().min(3, 'Código deve ter no mínimo 3 caracteres'),
});

type AffiliateFormData = z.infer<typeof affiliateSchema>;

interface Affiliate extends AffiliateFormData {
    id: string;
    createdAt: string;
}

export default function Affiliates() {
    const [affiliates, setAffiliates] = useState<Affiliate[]>([]);
    const [form, setForm] = useState<AffiliateFormData>({ name: '', email: '', code: '' });
    const [isLoading, setIsLoading] = useState(false);
    const
      await api.post('/api/affiliates', form);
      setForm({ name: '', email: '', code: '' });
      fetchAffiliates();
    } catch {
      alert('Erro ao criar afiliado');
    }
  };

  useEffect(() => {
    fetchAffiliates();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Afiliados</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <input
          className="border p-2 rounded"
          placeholder="Nome"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <input
          className="border p-2 rounded"
          placeholder="Código"
          value={form.code}
          onChange={(e) => setForm({ ...form, code: e.target.value })}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={createAffiliate}
        >
          Cadastrar
        </button>
      </div>

      <div className="overflow-auto">
        <table className="w-full table-auto text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2">Nome</th>
              <th>Email</th>
              <th>Código</th>
              <th>Criado em</th>
            </tr>
          </thead>
          <tbody>
            {affiliates.map((a) => (
              <tr key={a.id} className="border-t">
                <td className="p-2">{a.name}</td>
                <td>{a.email}</td>
                <td>{a.code}</td>
                <td>{new Date(a.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
