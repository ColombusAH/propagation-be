import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { ProductCard } from '@/components/ProductCard';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const TitleRow = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
`;

const SearchContainer = styled.div`
  position: relative;
`;

const SearchIcon = styled.span`
  position: absolute;
  right: ${theme.spacing.md};
  top: 50%;
  transform: translateY(-50%);
  color: ${theme.colors.textMuted};
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${theme.spacing.md} ${theme.spacing.md} ${theme.spacing.md} ${theme.spacing.md};
  padding-right: 2.75rem;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.sm};
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  transition: all ${theme.transitions.fast};

  &::placeholder {
    color: ${theme.colors.textMuted};
  }

  &:focus {
    outline: none;
    border-color: ${theme.colors.borderFocus};
    background: ${theme.colors.surfaceHover};
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: ${theme.spacing.lg};

  @media (max-width: ${theme.breakpoints.mobile}) {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: ${theme.spacing.md};
  }
`;

const Toast = styled.div<{ show: boolean }>`
  position: fixed;
  bottom: ${theme.spacing.xl};
  left: 50%;
  transform: translateX(-50%);
  background-color: ${theme.colors.success};
  color: ${theme.colors.text};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.md};
  box-shadow: ${theme.shadows.lg};
  display: ${(props) => (props.show ? 'flex' : 'none')};
  align-items: center;
  gap: ${theme.spacing.sm};
  z-index: ${theme.zIndex.modal};
  font-size: ${theme.typography.fontSize.sm};
`;

const MaterialIcon = ({ name, size = 20 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

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
    setToastMessage(t('scan.productAdded', { product: product?.name || 'מוצר' }));
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  return (
    <Layout>
      <Container>
        <Header>
          <TitleRow>
            <MaterialIcon name="inventory_2" size={24} />
            <Title>{t('catalog.title')}</Title>
          </TitleRow>
          <SearchContainer>
            <SearchIcon>
              <MaterialIcon name="search" size={20} />
            </SearchIcon>
            <SearchInput
              type="text"
              placeholder={t('catalog.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchContainer>
        </Header>

        {displayProducts.length === 0 ? (
          <EmptyState
            icon="search_off"
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
        <MaterialIcon name="check_circle" size={18} />
        {toastMessage}
      </Toast>
    </Layout>
  );
}
