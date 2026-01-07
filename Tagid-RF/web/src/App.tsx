import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './styles/global';
import { theme } from './styles/theme';
import { AppRoutes } from './app.routes';
import { useStore } from './store';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastContainer } from './components/Toast/ToastContainer';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoginPage } from './pages/LoginPage';
import productsData from './data/products.json';

function AppContent() {
  const loadProducts = useStore((state) => state.loadProducts);
  const isLoaded = useStore((state) => state.isLoaded);
  const { isAuthenticated, login } = useAuth();

  useEffect(() => {
    if (!isLoaded) {
      loadProducts(productsData);
    }
  }, [loadProducts, isLoaded]);

  if (!isAuthenticated) {
    return <LoginPage onLogin={login} />;
  }

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <GlobalStyles />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
        <ToastContainer />
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

