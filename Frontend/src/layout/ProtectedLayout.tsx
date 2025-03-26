import { ReactNode, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';

interface NavLink {
    label: string;
    path: string;
    icon?: string; // You can add icons using react-icons or similar
    permissions?: string[]; // For role-based access control
}

interface ProtectedLayoutProps {
    children: ReactNode;
    className?: string;
}

const navigationLinks: NavLink[] = [
    { label: 'Dashboard', path: '/dashboard', permissions: ['view_dashboard'] },
    { label: 'Automação de Fluxos', path: '/automacoes', permissions: ['view_automations'] },
    { label: 'Gerenciador de Tags', path: '/tags', permissions: ['view_tags'] },
    { label: 'Auditoria LGPD', path: '/consentimentos', permissions: ['view_gdpr'] },
    { label: 'CRM', path: '/crm', permissions: ['view_crm'] },
    { label: 'WhatsApp', path: '/whatsapp', permissions: ['view_whatsapp'] },
];

export default function ProtectedLayout({ children, className }: ProtectedLayoutProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const { logout, user } = useAuth();

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/login', { replace: true });
        } catch (error) {
            console.error('Logout failed:', error);
            // You can add toast notification here
        }
    };

    const authorizedLinks = useMemo(() => {
        return navigationLinks.filter(link => {
            if (!link.permissions) return true;
            return link.permissions.some(permission => user?.permissions?.includes(permission));
        });
    }, [user?.permissions]);

    return (
        <div className="flex min-h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="w-64 bg-blue-900 text-white flex flex-col shadow-xl">
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="p-6 border-b border-blue-800"></div>
                        <h1 className="text-2xl font-bold tracking-wider">Flowsale</h1>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 overflow-y-auto py-4">
                        <ul className="space-y-1 px-3">
                            {authorizedLinks.map((link) => {
                                const isActive = location.pathname === link.path;
                                return (
                                    <li key={link.path}>
                                        <button
                                            onClick={() => navigate(link.path)}
                                            className={`w-full text-left px-4 py-3 rounded-lg transition-colors duration-150 
                                                ${isActive 
                                                    ? 'bg-blue-800 text-white' 
                                                    : 'text-blue-100 hover:bg-blue-800 hover:text-white'
                                                }`}
                                            aria-current={isActive ? 'page' : undefined}
                                        >
                                            {link.label}
                                        </button>
                                    </li>
                                );
                            })}
                        </ul>
                    </nav>

                    {/* User section */}
                    <div className="p-4 border-t border-blue-800">
                        <div className="mb-4">
                            <p className="text-sm text-blue-200">{user?.email}</p>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="w-full px-4 py-2 text-sm font-medium text-white bg-red-600 
                                rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 
                                focus:ring-red-500 focus:ring-offset-2 transition-colors duration-150"
                            aria-label="Sair da aplicação"
                        >
                            Sair
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main content */}
            <main className={`flex-1 overflow-auto ${className}`}>
                <div className="container mx-auto px-6 py-8">
                    {children}
                </div>
            </main>
        </div>
    );
}</div>
