import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './styles/global';
import { theme } from './styles/theme';
import { AppRoutes } from './app.routes';
import { useStore } from './store';
import { ErrorBoundary } from './components/ErrorBoundary';
import productsData from './data/products.json';

export function App() {
  const loadProducts = useStore((state) => state.loadProducts);
  const isLoaded = useStore((state) => state.isLoaded);

  useEffect(() => {
    if (!isLoaded) {
      loadProducts(productsData);
    }
  }, [loadProducts, isLoaded]);

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <GlobalStyles />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeProvider>
    </ErrorBoundary>
  );
}


