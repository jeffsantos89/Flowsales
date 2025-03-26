import { FC, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';

// Types
interface Module {
    id: string;
    name: string;
    description: string;
    route: string;
    icon?: string;
    enabled: boolean;
}

// Constants
const MODULES: Module[] = [
    {
        id: 'automation',
        name: 'Automação de Fluxos',
        description: 'Construa automações visuais inteligentes com IA e canvas.',
        route: '/automacoes',
        enabled: true,
    },
    {
        id: 'tags',
        name: 'Gerenciador de Tags',
        description: 'Crie e vincule tags de comportamento ao seu CRM.',
        route: '/tags',
        enabled: true,
    },
    {
        id: 'lgpd',
        name: 'Auditoria LGPD',
        description: 'Visualize e exporte consentimentos dos usuários.',
        route: '/consentimentos',
        enabled: true,
    },
    {
        id: 'crm',
        name: 'Leads e CRM',
        description: 'Acompanhe leads, status e lead scoring.',
        route: '/crm',
        enabled: true,
    },
    {
        id: 'whatsapp',
        name: 'Campanhas WhatsApp',
        description: 'Configure campanhas de disparo automatizado com IA.',
        route: '/whatsapp',
        enabled: true,
    },
];

// Components
const ModuleCard: FC<{ module: Module }> = ({ module }) => {
    const navigate = useNavigate();

    const handleModuleClick = () => {
        if (!module.enabled) return;
        navigate(module.route);
    };

    return (
        <div
            onClick={handleModuleClick}
            className={`
                cursor-pointer bg-white rounded-xl p-6 transition
                ${module.enabled 
                    ? 'shadow-md hover:shadow-xl hover:scale-105' 
                    : 'opacity-50 cursor-not-allowed'}
            `}
            data-testid={`module-card-${module.id}`}
        >
            <h2 className="text-xl font-semibold">{module.name}</h2>
            <p className="text-gray-600 mt-2">{module.description}</p>
            {!module.enabled && (
                <span className="text-sm text-red-500 mt-2">Em breve</span>
            )}
        </div>
    );
};

const ErrorFallback: FC<{ error: Error }> = ({ error }) => (
    <div className="text-red-500 p-4">
        <h2>Oops! Algo deu errado.</h2>
        <pre>{error.message}</pre>
    </div>
);

const LoadingState: FC = () => (
    <div className="animate-pulse grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((n) => (
            <div key={n} className="h-32 bg-gray-200 rounded-xl" />
        ))}
    </div>
);

// Main Component
const Dashboard: FC = () => {
    return (
        <div className="p-10 bg-gray-100 min-h-screen">
            <h1 className="text-3xl font-bold mb-6">
                Painel da Plataforma Flowsale 🚀
            </h1>
            <ErrorBoundary FallbackComponent={ErrorFallback}>
                <Suspense fallback={<LoadingState />}>
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {MODULES.map((module) => (
                            <ModuleCard key={module.id} module={module} />
                        ))}
                    </div>
                </Suspense>
            </ErrorBoundary>
        </div>
    );
};

export default Dashboard;
