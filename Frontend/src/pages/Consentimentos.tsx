import { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-toastify'; // Assuming you'll add react-toastify
import { useQuery } from 'react-query'; // Adding react-query for better data fetching
import { format } from 'date-fns'; // For better date formatting
import api from '../services/api';

interface Consent {
    id: string;
    name: string;
    email: string;
    cpfCnpj: string;
    acceptedTerms: boolean;
    purposes: string[];
    createdAt: string;
    ip: string;
}

interface FilterOptions {
    searchTerm: string;
    sortBy: keyof Consent;
    sortOrder: 'asc' | 'desc';
}

export default function Consentimentos() {
    const [filterOptions, setFilterOptions] = useState<FilterOptions>({
        searchTerm: '',
        sortBy: 'createdAt',
        sortOrder: 'desc',
    });

    const { data: consents = [], isLoading, error, refetch } = useQuery<Consent[]>(
        ['consents'],
        async () => {
            const response = await api.get('/consent');
            return response.data;
        },
        {
            staleTime: 5 * 60 * 1000, // Cache for 5 minutes
            retry: 3,
            onError: (err) => {
                toast.error('Erro ao carregar consentimentos. Tente novamente.');
                console.error('Erro ao carregar consentimentos', err);
            },
        }
    );

    const handleSort = useCallback((field: keyof Consent) => {
        setFilterOptions((prev) => ({
            ...prev,
            sortBy: field,
            sortOrder: prev.sortBy === field && prev.sortOrder === 'asc' ? 'desc' : 'asc',
        }));
    }, []);

    const exportCSV = useCallback(() => {
        try {
            const header = 'Nome,Email,CPF/CNPJ,IP,Data,Finalidades\n';
            const rows = filtered.map(c =>
                `"${c.name}","${c.email}","${c.cpfCnpj}","${c.ip}","${format(new Date(c.createdAt), 'dd/MM/yyyy HH:mm:ss')}","${c.purposes.join('|')}"`
            );
      </div>

      <input
        type="text"
        placeholder="Filtrar por nome, e-mail ou CPF/CNPJ"
        className="w-full p-2 border rounded"
        onChange={(e) => setFilter(e.target.value)}
      />

      <div className="overflow-auto border rounded">
        <table className="w-full table-auto text-sm">
          <thead className="bg-gray-200">
            <tr>
              <th className="p-2">Nome</th>
              <th>E-mail</th>
              <th>CPF/CNPJ</th>
              <th>IP</th>
              <th>Finalidades</th>
              <th>Data</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={c.id} className="border-t">
                <td className="p-2">{c.name}</td>
                <td>{c.email}</td>
                <td>{c.cpfCnpj}</td>
                <td>{c.ip}</td>
                <td>{c.purposes.join(', ')}</td>
                <td>{new Date(c.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
