import { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-toastify'; // Adicione react-toastify para notificações
import { ErrorBoundary } from 'react-error-boundary';
import { useQuery } from
  id: string;
  affiliateCode: string;
  product: string;
  value: number;
  status: 'pendente' | 'pago' | 'cancelado';
  createdAt: string;
}

export default function Commissions() {
  const [commissions, setCommissions] = useState<Commission[]>([]);

  const fetchCommissions = async () => {
    try {
      const res = await api.get('/api/commissions');
      setCommissions(res.data);
    } catch (err) {
      alert('Erro ao carregar comissões');
    }
  };

  useEffect(() => {
    fetchCommissions();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Comissões</h1>

      <div className="overflow-auto border rounded">
        <table className="w-full text-sm table-auto">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2">Código Afiliado</th>
              <th>Produto</th>
              <th>Valor</th>
              <th>Status</th>
              <th>Data</th>
            </tr>
          </thead>
          <tbody>
            {commissions.map((c) => (
              <tr key={c.id} className="border-t">
                <td className="p-2">{c.affiliateCode}</td>
                <td>{c.product}</td>
                <td>R$ {c.value.toFixed(2)}</td>
                <td>
                  <span
                    className={`px-2 py-1 rounded text-white ${
                      c.status === 'pago'
                        ? 'bg-green-600'
                        : c.status === 'pendente'
                        ? 'bg-yellow-500'
                        : 'bg-red-600'
                    }`}
                  >
                    {c.status}
                  </span>
                </td>
                <td>{new Date(c.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
