import { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'SUPER_ADMIN' | 'NETWORK_MANAGER' | 'NETWORK_ADMIN' | 'STORE_MANAGER' | 'SELLER' | 'CUSTOMER';

interface AuthContextType {
    userId: string | null;
    userRole: UserRole | null;
    token: string | null;
    login: (role: UserRole, token?: string, userId?: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [userId, setUserId] = useState<string | null>(() => {
        return localStorage.getItem('userId');
    });
    const [userRole, setUserRole] = useState<UserRole | null>(() => {
        return localStorage.getItem('userRole') as UserRole | null;
    });
    const [token, setToken] = useState<string | null>(() => {
        const stored = localStorage.getItem('authToken');
        // Clean up legacy demo token
        if (stored === 'demo-token') {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userRole');
            localStorage.removeItem('userId');
            return null;
        }
        return stored;
    });

    const login = (role: UserRole, authToken?: string, id?: string) => {
        setUserRole(role);
        setUserId(id || null);
        const tokenValue = authToken || '';
        setToken(tokenValue);
        localStorage.setItem('userRole', role);
        localStorage.setItem('authToken', tokenValue);
        if (id) localStorage.setItem('userId', id);
    };

    const logout = () => {
        setUserRole(null);
        setToken(null);
        setUserId(null);
        localStorage.removeItem('userRole');
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
    };

    return (
        <AuthContext.Provider
            value={{
                userId,
                userRole,
                token,
                login,
                logout,
                isAuthenticated: !!userRole,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
