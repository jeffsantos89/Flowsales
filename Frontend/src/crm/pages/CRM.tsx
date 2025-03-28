import { useEffect, useState, useMemo } from 'react';
import { toast } from 'react-toastify';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { useRouter } from 'next/router';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Spinner } from '@/components/Spinner';
import { ErrorBoundary } from '@/components/ErrorBoundary';

// Types
export enum LeadStage {
  NEW = 'novo',
  QUALIFIED = 'qualificado',
  PROPOSAL = 'proposta',
  CLOSED = 'fechado',
}

export interface Lead {
  id: string;
  name: string;
  email: string;
  stage: LeadStage;
  score: number;
  phone?: string;
  createdAt: string;
}

interface LeadFiltersProps {
  filter: string;
  setFilter: (value: string) => void;
  stageFilter: LeadStage | '';
  setStageFilter: (value: LeadStage | '') => void;
}

// API Services
const API_ENDPOINTS = {
  AI_SERVICE: 'http://ai-service:3005',
  CRM_SERVICE: 'http://crm-service:3003',
} as const;

const leadService = {
  predictScore: async (data: { name: string; email: string }) => {
    const response = await axios.post(`${API_ENDPOINTS.AI_SERVICE}/score`, { input: data });
    return response.data?.score ?? 0;
  },

  createLead: async (data: { name: string; email: string }, token: string) => {
    return axios.post(
      `${API_ENDPOINTS.CRM_SERVICE}/crm/leads`,
      data,
      { headers: { Authorization: `Bearer ${token}` } }
    );
  }
};

// Components
const LeadFilters: React.FC<LeadFiltersProps> = ({
  filter,
  setFilter,
  stageFilter,
  setStageFilter
}) => (
  <div className="flex gap-4 mb-4">
    <Input
      type="text"
      placeholder="Filtrar por nome ou e-mail"
      className="w-1/2"
      value={filter}
      onChange={(e) => setFilter(e.target.value)}
    />
    <select
      className="border p-2 rounded focus:ring-2 focus:ring-blue-500"
      value={stageFilter}
      onChange={(e) => setStageFilter(e.target.value as LeadStage | '')}
    >
      <option value="">Todos os estágios</option>
      {Object.values(LeadStage).map((stage) => (
        <option key={stage} value={stage}>{stage}</option>
      ))}
    </select>
  </div>
);

const LeadsTable: React.FC<{ leads: Lead[] }> = ({ leads }) => (
  <table className="w-full table-auto text-sm border rounded overflow-hidden">
    <thead className="bg-gray-200">
      <tr>
        <th className="p-2">Nome</th>
        <th>Email</th>
        <th>Telefone</th>
        <th>Estágio</th>
        <th>Score</th>
        <th>Data</th>
      </tr>
    </thead>
    <tbody>
      {leads.map((lead) => (
        <tr key={lead.id} className="border-t hover:bg-gray-50"></tr>
          <td className="p-2">{lead.name}</td>
          <td>{lead.email}</td>
          <td>{lead.phone || '-'}</td>
          <td>{lead.stage}</td>
          <td>{lead.score}</td>
          <td>{new Date(lead.createdAt).toLocaleDateString()}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

// Main Component
export default function CRMLeadForm() {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [score, setScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('');
  const [stageFilter, setStageFilter] = useState<LeadStage | ''>('');
  const router = useRouter();
  const queryClient = useQueryClient();

  const { token, user } = useMemo(() => ({
    token: typeof window !== 'undefined' ? localStorage.getItem('accessToken') : '',
    user: typeof window !== 'undefined' ? localStorage.getItem('username') : null
  }), []);

  useEffect(() => {
    if (!user) router.push('/login');
  }, [user, router]);

  const handlePredict = async () => {
    try {
      setLoading(true);
      const predictedScore = await leadService.predictScore(formData);
      setScore(predictedScore);
      toast.success('Score calculado com sucesso!');
    } catch (error) {
      toast.error('Erro ao consultar IA');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      await leadService.createLead(formData, token || '');
      toast.success('Lead criado com sucesso!');
      setFormData({ name: '', email: '' });
      setScore(null);
      queryClient.invalidateQueries('leads');
    } catch (error) {
      toast.error('Erro ao criar lead. Verifique autenticação.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <div className="max-w-xl mx-auto py-6">
        <Card>
          <CardContent className="space-y-4 p-6">
            <h2 className="text-xl font-semibold">Cadastro de Lead com IA</h2>
            {user && <p className="text-sm text-gray-500">Usuário logado: {user}</p>}
            
            <Input
              placeholder="Nome"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            />
            <Input
              placeholder="Email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            />
            
            <Button 
              onClick={handlePredict}
              disabled={loading || !formData.name || !formData.email}
              variant="outline"
            >
              {loading ? <Spinner /> : 'Prever Score IA'}
            </Button>
            
            {score !== null && (
              <p className="text-sm">
                Score sugerido: <strong>{score}</strong>
              </p>
            )}
            
            <Button 
              onClick={handleSubmit}
              disabled={loading || !formData.name || !formData.email}
              className="bg-blue-600 text-white w-full"
            >
              {loading ? <Spinner /> : 'Cadastrar Lead'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </ErrorBoundary>
  );
}</p>
