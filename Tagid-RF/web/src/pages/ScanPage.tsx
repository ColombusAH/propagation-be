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
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
`;

const TitleRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
`;

const CameraContainer = styled.div`
  margin-bottom: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  overflow: hidden;
  border: 1px solid ${theme.colors.border};
`;

const FallbackSection = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-top: ${theme.spacing.lg};
`;

const FallbackTitle = styled.h3`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  margin: 0 0 ${theme.spacing.md} 0;
  color: ${theme.colors.text};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const InputGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
`;

const Input = styled.input`
  flex: 1;
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  transition: all ${theme.transitions.fast};

  &::placeholder {
    color: ${theme.colors.textMuted};
  }

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: ${theme.shadows.focus};
  }
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: ${theme.colors.textInverse};
  border: 1px solid ${theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};

  &:hover {
    background-color: ${theme.colors.primaryDark};
    border-color: ${theme.colors.primaryDark};
  }

  &:disabled {
    opacity: 0.5;
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
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.xl};
  z-index: ${theme.zIndex.modal};
  animation: ${slideUp} 0.3s ease;
  min-width: 280px;
  max-width: 450px;
  border: 2px solid ${props => props.$type === 'container' ? theme.colors.info : theme.colors.success};
`;

const ResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.sm};
`;

const ResultIcon = styled.div`
  width: 36px;
  height: 36px;
  border-radius: ${theme.borderRadius.md};
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ResultTitle = styled.div`
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.semibold};
`;

const ResultMessage = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  opacity: 0.9;
  line-height: ${theme.typography.lineHeight.relaxed};
`;

const ProductList = styled.ul`
  margin: ${theme.spacing.sm} 0 0 0;
  padding-right: ${theme.spacing.lg};
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

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

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
    if (isContainer(barcode)) {
      const container = getContainerByBarcode(barcode);
      if (container && container.products.length > 0) {
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

        const totalItems = container.products.reduce((sum, p) => sum + p.qty, 0);
        showScanResult({
          type: 'container',
          title: t('scan.containerFound', { container: container.name }),
          message: t('scan.containerAdded', { count: totalItems }),
          products: productNames
        });
      } else {
        showScanResult({
          type: 'container',
          title: t('scan.containerEmpty'),
          message: t('scan.containerEmptyMessage')
        });
      }
      return;
    }

    const success = addByBarcode(barcode);
    if (success) {
      const product = getProductByBarcode(barcode);
      showScanResult({
        type: 'product',
        title: t('scan.productFound'),
        message: product?.name || t('scan.product')
      });
    } else {
      showScanResult({
        type: 'product',
        title: t('scan.productNotFound'),
        message: t('scan.barcodeNotRecognized')
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
    if (error.name === 'NotFoundException' || error.message.includes('No MultiFormat Readers')) {
      return;
    }
    console.error('Camera error:', error);
    setCameraError(error);
  };

  return (
    <Layout>
      <Container>
        <TitleRow>
          <MaterialIcon name="qr_code_scanner" size={24} />
          <Title>סריקת ברקוד או QR</Title>
        </TitleRow>

        {cameraError ? (
          <ErrorContainer>
            <EmptyState
              icon="photo_camera"
              title={t('scan.cameraUnavailable')}
              message={t('errors.cameraPermission')}
            />
          </ErrorContainer>
        ) : (
          <CameraContainer>
            <CameraView onScan={handleScan} onError={handleCameraError} />
          </CameraContainer>
        )}

        <FallbackSection>
          <FallbackTitle>
            <MaterialIcon name="keyboard" /> הזנה ידנית
          </FallbackTitle>
          <form onSubmit={handleManualSubmit}>
            <InputGroup>
              <Input
                type="text"
                placeholder="הזן ברקוד או QR באופן ידני..."
                value={manualBarcode}
                onChange={(e) => setManualBarcode(e.target.value)}
              />
              <Button type="submit" disabled={!manualBarcode.trim()}>
                <MaterialIcon name="add" /> {t('scan.add')}
              </Button>
            </InputGroup>
          </form>
        </FallbackSection>

        <FallbackSection>
          <Button onClick={() => navigate('/catalog')} style={{ width: '100%', justifyContent: 'center' }}>
            <MaterialIcon name="inventory_2" /> {t('scan.browseCatalog')}
          </Button>
        </FallbackSection>
      </Container>

      {scanResult && (
        <ScanResult $type={scanResult.type} role="alert" aria-live="polite">
          <ResultHeader>
            <ResultIcon>
              <MaterialIcon name={scanResult.type === 'container' ? 'inventory' : 'check'} size={20} />
            </ResultIcon>
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
