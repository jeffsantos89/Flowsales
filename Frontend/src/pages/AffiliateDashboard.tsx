import { useEffect, useState, useCallback } from 'react';
import api from '../services/api';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';
import { ErrorBoundary } from 'react-error-boundary';
import { toast } from 'react-toastify';

// Types
interface DashboardData {
    totalAffiliates: number;
    totalCommissions: number;
    commissionsByDate: CommissionData[];
}

interface CommissionData {
    date: string;
    total: number;
}

interface DashboardCardProps {
    title: string;
    value: string | number;
    icon?: React.ReactNode;
}

// Components
const DashboardCard: React.FC<DashboardCardProps> = ({ title, value, icon }) => (
    <div className="bg-white p-6 rounded-lg shadow-lg transition-all hover:shadow-xl"></div>
        <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
            {icon}
        </div>
        <p className="text-3xl font-bold text-blue-600 mt-2">{value}</p>
    </div>
);

const LoadingSpinner = () => (
    <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
    </div>
);

const ErrorFallback = ({ error, resetErrorBoundary }) => (
    <div className="text-center p-4 bg-red-50 rounded-lg">
        <h2 className="text-xl font-semibold text-red-600">Algo deu errado!</h2>
        <p className="text-gray-600 mt-2">{error.message}</p>
        <button
            onClick={resetErrorBoundary}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
            Tentar novamente
        </button>
    </div>
);

export default function AffiliateDashboard() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('week');

    const loadDashboard = useCallback(async () => {
        try {
            setIsLoading(true);
            const res = await api.get(`/api/dashboard?timeRange=${timeRange}`);
            setData(res.data);
        } catch (err) {
            toast.error('Erro ao carregar dados da dashboard');
            console.error('Dashboard loading error:', err);
        } finally {
            setIsLoading(false);
        }
    }, [timeRange]);

    useEffect(() => {
        loadDashboard();
        // Set up auto-refresh every 5 minutes
        const interval = setInterval(loadDashboard, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, [loadDashboard]);

    if (isLoading) return <LoadingSpinner />;
    if (!data) return null;

    return (
        <ErrorBoundary FallbackComponent={ErrorFallback} onReset={loadDashboard}>
            <div className="space-y-8 p-6">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">Dashboard de Afiliados</h1>
                    <div className="flex gap-2">
                        {['week', 'month', 'year'].map((range) => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range as any)}
                                className={`px-4 py-2 rounded ${
                                    timeRange === range
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-200 hover:bg-gray-300'
                                }`}
                            >
                                {range.charAt(0).toUpperCase() + range.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <DashboardCard
                        title="Total de Afiliados"
                        value={data.totalAffiliates.toLocaleString()}
                    />
                    <DashboardCard</button></div>
