import { useEffect, useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './styles/global';
import { lightTheme, darkTheme } from './styles/theme';
import { AppRoutes } from './app.routes';
import { useStore } from './store';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastContainer } from './components/Toast/ToastContainer';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { GlobalAlerts } from './components/GlobalAlerts';
import { VerificationPage } from './pages/VerificationPage';
import { API_BASE_URL } from './api/config';

function AppContent() {
  const locale = useStore((state) => state.locale);
  const darkMode = useStore((state) => state.darkMode);
  const { isAuthenticated, login } = useAuth();
  const [view, setView] = useState<'login' | 'register' | 'verify'>('login');
  const [pendingEmail, setPendingEmail] = useState<string>('');

  const loadProducts = useStore((state) => state.loadProducts);

  // Global product fetching
  useEffect(() => {
    if (isAuthenticated) {
      const fetchProducts = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/products/?t=` + new Date().getTime());
          if (response.ok) {
            const data = await response.json();
            const mappedProducts = data.map((p: any) => ({
              id: p.id,
              name: p.name,
              priceInCents: Math.round(p.price * 100),
              sku: p.sku,
              barcode: p.sku || p.id,
              description: p.description
            }));
            loadProducts(mappedProducts);
          }
        } catch (error) {
          console.error('Failed to fetch products:', error);
        }
      };

      fetchProducts();
    }
  }, [isAuthenticated, loadProducts]);

  // Set RTL direction based on locale
  useEffect(() => {
    document.documentElement.dir = locale === 'he' ? 'rtl' : 'ltr';
    document.documentElement.lang = locale;

    // Load Facebook SDK
    const fbAppId = import.meta.env.VITE_FACEBOOK_APP_ID;
    console.log('Initializing FB SDK with ID:', fbAppId);

    if (fbAppId) {
      (window as any).fbAsyncInit = function () {
        console.log('FB SDK Async Init started');
        (window as any).FB.init({
          appId: fbAppId,
          cookie: true,
          xfbml: true,
          version: 'v18.0'
        });
        console.log('FB SDK Initialized');
      };

      (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) {
          console.log('FB SDK script already in DOM');
          return;
        }
        js = d.createElement(s); js.id = id;
        (js as any).src = "https://connect.facebook.net/he_IL/sdk.js";
        fjs?.parentNode?.insertBefore(js, fjs);
        console.log('FB SDK script injected');
      }(document, 'script', 'facebook-jssdk'));
    } else {
      console.warn('VITE_FACEBOOK_APP_ID is missing');
    }
  }, [locale]);

  if (!isAuthenticated) {
    if (view === 'verify') {
      return (
        <VerificationPage
          email={pendingEmail}
          onVerified={(role, token) => login(role, token)}
          onCancel={() => setView('login')}
        />
      );
    }

    if (view === 'register') {
      return (
        <RegisterPage
          onBackToLogin={() => setView('login')}
          onRegisterSuccess={(email) => {
            setPendingEmail(email);
            setView('verify');
          }}
        />
      );
    }
    return <LoginPage onLogin={login} onToggleRegister={() => setView('register')} />;
  }

  const currentTheme = darkMode ? darkTheme : lightTheme;

  return (
    <ErrorBoundary>
      <ThemeProvider theme={currentTheme}>
        <GlobalStyles />
        <GlobalAlerts />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
        <ToastContainer />
      </ThemeProvider>
    </ErrorBoundary>
  );
}

import { GoogleOAuthProvider } from '@react-oauth/google';

export function App() {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

