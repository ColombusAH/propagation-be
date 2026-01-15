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
  transition: all ${theme.transitions.fast};

  &:hover {
    border-color: ${theme.colors.borderDark};
    box-shadow: ${theme.shadows.md};
  }
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  aspect-ratio: 1;
  background: ${theme.colors.backgroundAlt};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${theme.colors.textMuted};
`;

const Image = styled.img`
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: ${theme.borderRadius.md};
  border: 1px solid ${theme.colors.border};
`;

const Name = styled.h3`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
  margin: 0;
  line-height: ${theme.typography.lineHeight.snug};
`;

const Info = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const Price = styled.span`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
`;

const Sku = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
  font-family: ${theme.typography.fontFamily.mono};
`;

const Button = styled.button`
  background-color: ${theme.colors.gray[800]};
  color: ${theme.colors.text};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  margin-top: ${theme.spacing.sm};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.xs};

  &:hover {
    background-color: ${theme.colors.gray[700]};
    border-color: ${theme.colors.borderDark};
  }

  &:active {
    transform: scale(0.98);
  }
`;

const MaterialIcon = ({ name, size = 16 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const { t, formatPrice } = useTranslation();

  return (
    <Card>
      {product.imageUrl ? (
        <Image src={product.imageUrl} alt={product.name} />
      ) : (
        <ImagePlaceholder>
          <MaterialIcon name="inventory_2" size={40} />
        </ImagePlaceholder>
      )}
      <Name>{product.name}</Name>
      <Info>
        <Price>{formatPrice(product.priceInCents)}</Price>
        {product.sku && <Sku>{product.sku}</Sku>}
      </Info>
      <Button onClick={() => onAddToCart(product.id)}>
        <MaterialIcon name="add_shopping_cart" /> {t('catalog.addToCart')}
      </Button>
    </Card>
  );
}
