import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { ProductCard } from '@/components/ProductCard';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  margin-bottom: ${theme.spacing.md};
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${theme.spacing.lg};

  @media (max-width: ${theme.breakpoints.mobile}) {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: ${theme.spacing.md};
  }
`;

const Toast = styled.div<{ show: boolean }>`
  position: fixed;
  bottom: ${theme.spacing.xl};
  left: 50%;
  transform: translateX(-50%);
  background-color: ${theme.colors.success};
  color: white;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.lg};
  display: ${(props) => (props.show ? 'block' : 'none')};
  z-index: ${theme.zIndex.modal};
`;

export function CatalogPage() {
  const { products, searchProducts, addByProductId, getProductById } =
    useStore();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const displayProducts = searchQuery
    ? searchProducts(searchQuery)
    : products;

  const handleAddToCart = (productId: string) => {
    addByProductId(productId);
    const product = getProductById(productId);
    setToastMessage(t('scan.productAdded', { product: product?.name || 'product' }));
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  return (
    <Layout>
      <Container>
        <Header>
          <Title>📦 {t('catalog.title')}</Title>
          <SearchInput
            type="text"
            placeholder={t('catalog.searchPlaceholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </Header>

        {displayProducts.length === 0 ? (
          <EmptyState
            icon="🔍"
            title={t('catalog.noProducts')}
            message={
              searchQuery
                ? t('catalog.noProducts')
                : t('catalog.noProducts')
            }
          />
        ) : (
          <Grid>
            {displayProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </Grid>
        )}
      </Container>

      <Toast show={showToast} aria-live="polite">
        {toastMessage}
      </Toast>
    </Layout>
  );
}

