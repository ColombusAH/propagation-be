import { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
    userRole: string | null;
    token: string | null;
    login: (role: string, token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [userRole, setUserRole] = useState<string | null>(() => {
        return localStorage.getItem('userRole');
    });
    const [token, setToken] = useState<string | null>(() => {
        return localStorage.getItem('authToken');
    });

    const login = (role: string, token: string) => {
        setUserRole(role);
        setToken(token);
        localStorage.setItem('userRole', role);
        localStorage.setItem('authToken', token);
    };

    const logout = () => {
        setUserRole(null);
        setToken(null);
        localStorage.removeItem('userRole');
        localStorage.removeItem('authToken');
    };

    return (
        <AuthContext.Provider
            value={{
                userRole,
                token,
                login,
                logout,
                isAuthenticated: !!userRole && !!token,
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
