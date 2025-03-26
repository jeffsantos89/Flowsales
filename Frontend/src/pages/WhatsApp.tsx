import { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-toastify'; // Adicione react-toastify ao projeto
import { useQuery, useMutation, useQueryClient } from 'react-query'; // Adicione react-query
import api from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorBoundary } from '../components/ErrorBoundary';

interface Campaign {
    id: string;
    title: string;
    message: string;
    status: 'rascunho' | 'agendada' | 'enviada' | 'erro';
    scheduledAt?: string;
    createdAt: string;
}

interface CampaignInput {
    title: string;
    message: string;
    scheduledAt?: string;
}

const initialCampaignState: CampaignInput = {
    title: '',
    message: '',
    scheduledAt: undefined,
};

const fetchCampaigns = async (): Promise<Campaign[]> => {
    const { data } = await api.get<Campaign[]>('/whatsapp/campaigns');
    return data;
};

export default function WhatsApp() {
    const queryClient = useQueryClient();
    const [newCampaign, setNewCampaign] = useState<CampaignInput>(initialCampaignState);

    // Usando React Query para gerenciamento de estado e cache
    const { data: campaigns = [], isLoading, error } = useQuery<Campaign[], Error>(
        'campaigns',
        fetchCampaigns,
        {
            staleTime: 1000 * 60 * 5, // 5 minutos
            refetchOnWindowFocus: true,
        }
    );

    const createMutation = useMutation(
        (campaign: CampaignInput) => api.post('/whatsapp/campaigns', campaign),
        {
            onSuccess: () => {
                queryClient.invalidateQueries('campaigns');
                setNewCampaign(initialCampaignState);
                toast.success('Campanha criada com sucesso!');
            },
            onError: (error: Error) => {
                toast.error(`Erro ao criar campanha: ${error.message}`);
            },
        }
    );

    const handleCreate = useCallback(async () => {
        if (!newCampaign.title.trim() || !newCampaign.message.trim()) {
            toast.warning('Preencha todos os campos obrigatórios');
            return;
        }
        createMutation.mutate(newCampaign);
    }, [newCampaign, createMutation]);

    const handleInputChange = useCallback((
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value } = e.target;
        setNewCampaign(prev => ({ ...prev, [name]: value }));
    }, []);

    const getStatusBadgeColor = (status: Campaign['status']) => {
        const colors = {
            rascunho: 'bg-gray-200 text-gray-800',
            agendada: 'bg-yellow-200 text-yellow-800',
            enviada: 'bg-green-200 text-green-800',
            erro: 'bg-red-200 text-red-800',
        };
        return colors[status];
    };

    if (error) {
        return <div className="text-red-600">Erro ao carregar campanhas: {error.message}</div>;
    }

    return (
        <ErrorBoundary>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
                <h1 className="text-3xl font-bold text-gray-900">Campanhas de WhatsApp</h1>

                <div className="bg-white p-6 rounded-lg shadow-lg space-y-4">
                    <h2 className="text-xl font-semibold text-gray-800">Nova Campanha</h2>
                    <div className="space-y-4">
                        <input
                            type="text"
                            name="title"
                            placeholder="Título"
                            className="border border-gray-300 p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            value={newCampaign.title}
                            onChange={handleInputChange}
                        />
                        <textarea
                            name="message"
                            placeholder="Mensagem"
                            className="border border-gray-300 p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            rows={4}
                            value={newCampaign.message}
                            onChange={handleInputChange}
                        />
                        <input
                            type="datetime-local"
                            name="scheduledAt"
                            className="border border-gray-300 p-2 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            value={newCampaign.scheduledAt || ''}
                            onChange={handleInputChange}
                        />
                        <button
                            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 
                                                 transition-colors duration-200 disabled:opacity-50"
                            onClick={handleCreate}
                            disabled={createMutation.isLoading}
                        >
                            {createMutation.isLoading ? 'Criando...' : 'Criar Campanha'}
                        </button>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                    {isLoading ? (
                        <LoadingSpinner />
                    ) : (
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Título
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Mensagem
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Agendada
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Criada em
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {campaigns.map((campaign) => (
                                    <tr key={campaign.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">{campaign.title}</td>
                                        <td className="px-6 py-4">{campaign.message}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadgeColor(campaign.status)}`}>
                                                {campaign.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {campaign.scheduledAt ? new Date(campaign.scheduledAt).toLocaleString() : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {new Date(campaign.createdAt).toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </ErrorBoundary>
    );
}</td></tr></th></div>
