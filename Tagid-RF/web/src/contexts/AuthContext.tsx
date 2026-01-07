import { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
    userRole: string | null;
    login: (role: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [userRole, setUserRole] = useState<string | null>(() => {
        // Check localStorage for saved role
        return localStorage.getItem('userRole');
    });

    const login = (role: string) => {
        setUserRole(role);
        localStorage.setItem('userRole', role);
    };

    const logout = () => {
        setUserRole(null);
        localStorage.removeItem('userRole');
    };

    return (
        <AuthContext.Provider
            value={{
                userRole,
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
