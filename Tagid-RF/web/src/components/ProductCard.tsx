import styled from 'styled-components';
import { Product } from '@/store/types';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';

interface ProductCardProps {
  product: Product;
  onAddToCart: (productId: string) => void;
}

const Card = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md};
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
  transition: box-shadow ${theme.transitions.fast};

  &:hover {
    box-shadow: ${theme.shadows.md};
  }
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  aspect-ratio: 1;
  background: linear-gradient(
    135deg,
    ${theme.colors.backgroundAlt} 0%,
    ${theme.colors.border} 100%
  );
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${theme.typography.fontSize['3xl']};
`;

const Image = styled.img`
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: ${theme.borderRadius.md};
`;

const Name = styled.h3`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
`;

const Info = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const Price = styled.span`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
`;

const Sku = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: background-color ${theme.transitions.fast};
  margin-top: ${theme.spacing.sm};

  &:hover {
    background-color: ${theme.colors.primaryDark};
  }

  &:active {
    transform: scale(0.98);
  }
`;

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const { t, formatPrice } = useTranslation();

  return (
    <Card>
      {product.imageUrl ? (
        <Image src={product.imageUrl} alt={product.name} />
      ) : (
        <ImagePlaceholder>📦</ImagePlaceholder>
      )}
      <Name>{product.name}</Name>
      <Info>
        <Price>{formatPrice(product.priceInCents)}</Price>
        {product.sku && <Sku>SKU: {product.sku}</Sku>}
      </Info>
      <Button onClick={() => onAddToCart(product.id)}>{t('catalog.addToCart')}</Button>
    </Card>
  );
}

