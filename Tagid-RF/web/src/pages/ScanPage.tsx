import { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { CameraView } from '@/components/CameraView';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: ${theme.spacing.lg};
  color: ${theme.colors.text};
  font-size: ${theme.typography.fontSize['3xl']};
`;

const CameraContainer = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const FallbackSection = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-top: ${theme.spacing.lg};
`;

const FallbackTitle = styled.h3`
  font-size: ${theme.typography.fontSize.lg};
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.text};
`;

const InputGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
`;

const Input = styled.input`
  flex: 1;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: background-color ${theme.transitions.fast};

  &:hover {
    background-color: ${theme.colors.primaryDark};
  }

  &:disabled {
    background-color: ${theme.colors.gray[300]};
    cursor: not-allowed;
  }
`;

const slideUp = keyframes`
  from {
    transform: translateY(100px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`;

const ScanResult = styled.div<{ $type: 'product' | 'container' }>`
  position: fixed;
  bottom: ${theme.spacing.xl};
  left: 50%;
  transform: translateX(-50%);
  background: ${props => props.$type === 'container' ? theme.colors.info : theme.colors.success};
  color: white;
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.xl};
  z-index: ${theme.zIndex.modal};
  animation: ${slideUp} 0.3s ease;
  min-width: 300px;
  max-width: 500px;
`;

const ResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.sm};
`;

const ResultIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: ${theme.borderRadius.full};
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
`;

const ResultTitle = styled.div`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
`;

const ResultMessage = styled.div`
  font-size: ${theme.typography.fontSize.base};
  opacity: 0.95;
  line-height: ${theme.typography.lineHeight.relaxed};
`;

const ProductList = styled.ul`
  margin: ${theme.spacing.sm} 0 0 0;
  padding-left: ${theme.spacing.lg};
  list-style: disc;
`;

const ErrorContainer = styled.div`
  margin-top: ${theme.spacing.lg};
`;

interface ScanResultData {
  type: 'product' | 'container';
  title: string;
  message: string;
  products?: string[];
}

export function ScanPage() {
  const navigate = useNavigate();
  const {
    addByBarcode,
    getProductByBarcode,
    isContainer,
    getContainerByBarcode,
    addByProductId,
    getProductById
  } = useStore();
  const { t } = useTranslation();
  const [manualBarcode, setManualBarcode] = useState('');
  const [scanResult, setScanResult] = useState<ScanResultData | null>(null);
  const [cameraError, setCameraError] = useState<Error | null>(null);

  const showScanResult = (result: ScanResultData) => {
    setScanResult(result);
    setTimeout(() => {
      setScanResult(null);
    }, 4000);
  };

  const handleScan = (barcode: string) => {
    // Check if it's a container first
    if (isContainer(barcode)) {
      const container = getContainerByBarcode(barcode);
      if (container && container.products.length > 0) {
        // Add all products from container to cart
        const productNames: string[] = [];
        container.products.forEach(({ productId, qty }) => {
          const product = getProductById(productId);
          if (product) {
            productNames.push(`${product.name} × ${qty}`);
          }
          for (let i = 0; i < qty; i++) {
            addByProductId(productId);
          }
        });

        showScanResult({
          type: 'container',
          title: `מיכל: ${container.name}`,
          message: `נוספו ${container.products.reduce((sum, p) => sum + p.qty, 0)} מוצרים לעגלה`,
          products: productNames
        });
      } else {
        showScanResult({
          type: 'container',
          title: 'מיכל ריק',
          message: 'המיכל לא מכיל מוצרים'
        });
      }
      return;
    }

    // Regular product scan
    const success = addByBarcode(barcode);
    if (success) {
      const product = getProductByBarcode(barcode);
      showScanResult({
        type: 'product',
        title: 'מוצר נוסף',
        message: product?.name || 'מוצר'
      });
    } else {
      showScanResult({
        type: 'product',
        title: 'מוצר לא נמצא',
        message: 'הברקוד לא מזוהה במערכת'
      });
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualBarcode.trim()) {
      handleScan(manualBarcode.trim());
      setManualBarcode('');
    }
  };

  const handleCameraError = (error: Error) => {
    // NotFoundException is expected when no barcode is in view - ignore it
    if (error.name === 'NotFoundException' || error.message.includes('No MultiFormat Readers')) {
      return;
    }
    console.error('Camera error:', error);
    setCameraError(error);
  };

  return (
    <Layout>
      <Container>
        <Title>סריקת ברקוד או QR</Title>

        {cameraError ? (
          <ErrorContainer>
            <EmptyState
              icon="📷"
              title="מצלמה לא זמינה"
              message={`${cameraError.message}. אנא השתמש בהזנה ידנית או בדוק הרשאות מצלמה.`}
            />
          </ErrorContainer>
        ) : (
          <CameraContainer>
            <CameraView onScan={handleScan} onError={handleCameraError} />
          </CameraContainer>
        )}

        <FallbackSection>
          <FallbackTitle>הזנה ידנית</FallbackTitle>
          <form onSubmit={handleManualSubmit}>
            <InputGroup>
              <Input
                type="text"
                placeholder="הזן ברקוד או QR באופן ידני..."
                value={manualBarcode}
                onChange={(e) => setManualBarcode(e.target.value)}
              />
              <Button type="submit" disabled={!manualBarcode.trim()}>
                הוסף
              </Button>
            </InputGroup>
          </form>
        </FallbackSection>

        <FallbackSection>
          <Button onClick={() => navigate('/catalog')}>
            עבור לקטלוג →
          </Button>
        </FallbackSection>
      </Container>

      {scanResult && (
        <ScanResult $type={scanResult.type} role="alert" aria-live="polite">
          <ResultHeader>
            <ResultIcon>{scanResult.type === 'container' ? 'C' : 'P'}</ResultIcon>
            <ResultTitle>{scanResult.title}</ResultTitle>
          </ResultHeader>
          <ResultMessage>
            {scanResult.message}
            {scanResult.products && scanResult.products.length > 0 && (
              <ProductList>
                {scanResult.products.map((product, index) => (
                  <li key={index}>{product}</li>
                ))}
              </ProductList>
            )}
          </ResultMessage>
        </ScanResult>
      )}
    </Layout>
  );
}
