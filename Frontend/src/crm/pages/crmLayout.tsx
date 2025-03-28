import Link from 'next/link';
import { useRouter } from 'next/router';
import { ReactNode, useEffect, memo } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { NavigationItems } from '@/config/navigation';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion'; // Para animações suaves
import { ErrorBoundary } from 'react-error-boundary';

interface CRMLayoutProps {
    children: ReactNode;
}

const NavigationLink = memo(({ path, label }: { path: string; label: string }) => {
    const router = useRouter();
    return (
        <Link
            href={path}
            className={`text-sm transition-colors duration-200 ${
                router.pathname === path
                    ? 'text-blue-600 font-medium'
                    : 'text-gray-600 hover:text-blue-600'
            }`}
        >
            {label}
        </Link>
    );
});

NavigationLink.displayName = 'NavigationLink';

const ErrorFallback = ({ error }: { error: Error }) => (
    <div className="p-4 bg-red-50 text-red-600">
        <h2>Algo deu errado:</h2>
        <pre>{error.message}</pre>
    </div>
);

const CRMLayout = ({ children }: CRMLayoutProps) => {
    const router = useRouter();
    const { user, logout: handleLogout } = useAuth();

    useEffect(() => {
        if (!user) {
            router.push('/login');
        }
    }, [user, router]);

    const handleLogoutClick = async () => {
        try {
            await handleLogout();
            router.push('/login');
            toast.success('Logout realizado com sucesso');
        } catch (error) {
            toast.error('Erro ao realizar logout');
            console.error('Logout error:', error);
        }
    };

    if (!user) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
        );
    }

    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="min-h-screen bg-gray-100"
        >
            <header className="bg-white shadow-md p-4 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <motion.div whileHover={{ scale: 1.05 }}>
                        <Link 
                            href="/dashboard" 
                            className="text-lg font-semibold text-blue-600 hover:text-blue-700 transition-colors"
                        >
                            Flowsales CRM
                        </Link>
                    </motion.div>
                    <nav className="flex items-center space-x-6">
                        {NavigationItems.map((item) => (
                            <NavigationLink 
                                key={item.path} 
                                path={item.path} 
                                label={item.label} 
                            />
                        ))}
                        {user && (
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={handleLogoutClick}
                                className="text-sm px-4 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                                aria-label="Logout"
                            >
                                Sair ({user.name})
                            </motion.button>
                        )}
                    </nav>
                </div>
            </header>
            <main className="p-6 max-w-7xl mx-auto">
                <ErrorBoundary FallbackComponent={ErrorFallback}>
                    <motion.div 
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="bg-white rounded-lg shadow-sm p-6"
                    >
                        {children}
                    </motion.div>
                </ErrorBoundary>
            </main>
        </motion.div>
    );
};

export default memo(CRMLayout);
