import { useState } from 'react';
import styled from 'styled-components';
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
    background-color: ${theme.colors.borderDark};
    cursor: not-allowed;
  }
`;

const Toast = styled.div<{ show: boolean; success: boolean }>`
  position: fixed;
  bottom: ${theme.spacing.xl};
  left: 50%;
  transform: translateX(-50%);
  background-color: ${(props) =>
    props.success ? theme.colors.success : theme.colors.error};
  color: white;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.lg};
  display: ${(props) => (props.show ? 'block' : 'none')};
  z-index: ${theme.zIndex.modal};
  animation: slideUp 0.3s ease;

  @keyframes slideUp {
    from {
      transform: translateX(-50%) translateY(100px);
      opacity: 0;
    }
    to {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }
  }
`;

const ErrorContainer = styled.div`
  margin-top: ${theme.spacing.lg};
`;

export function ScanPage() {
  const navigate = useNavigate();
  const {
    addByBarcode,
    getProductByBarcode,
    isContainer,
    getContainerByBarcode,
    addByProductId
  } = useStore();
  const { t } = useTranslation();
  const [manualBarcode, setManualBarcode] = useState('');
  const [toast, setToast] = useState<{
    show: boolean;
    message: string;
    success: boolean;
  }>({ show: false, message: '', success: true });
  const [cameraError, setCameraError] = useState<Error | null>(null);

  const showToast = (message: string, success = true) => {
    setToast({ show: true, message, success });
    setTimeout(() => {
      setToast({ show: false, message: '', success: true });
    }, 2000);
  };

  const handleScan = (barcode: string) => {
    // Check if it's a container first
    if (isContainer(barcode)) {
      const container = getContainerByBarcode(barcode);
      if (container && container.products.length > 0) {
        // Add all products from container to cart
        container.products.forEach(({ productId, qty }) => {
          for (let i = 0; i < qty; i++) {
            addByProductId(productId);
          }
        });
        showToast(t('scan.containerAdded', { container: container.name }), true);
      } else {
        showToast(t('containers.empty'), false);
      }
      return;
    }

    // Regular product scan
    const success = addByBarcode(barcode);
    if (success) {
      const product = getProductByBarcode(barcode);
      showToast(t('scan.productAdded', { product: product?.name || 'product' }), true);
    } else {
      showToast(t('scan.productNotFound'), false);
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
        <Title>📷 Scan Barcode or QR Code</Title>

        {cameraError ? (
          <ErrorContainer>
            <EmptyState
              icon="📷"
              title="Camera Unavailable"
              message={`${cameraError.message}. Please use manual input below or check camera permissions.`}
            />
          </ErrorContainer>
        ) : (
          <CameraContainer>
            <CameraView onScan={handleScan} onError={handleCameraError} />
          </CameraContainer>
        )}

        <FallbackSection>
          <FallbackTitle>Manual Entry</FallbackTitle>
          <form onSubmit={handleManualSubmit}>
            <InputGroup>
              <Input
                type="text"
                placeholder="Enter barcode or QR code manually..."
                value={manualBarcode}
                onChange={(e) => setManualBarcode(e.target.value)}
              />
              <Button type="submit" disabled={!manualBarcode.trim()}>
                Add
              </Button>
            </InputGroup>
          </form>
        </FallbackSection>

        <FallbackSection>
          <Button onClick={() => navigate('/catalog')}>
            Browse Catalog →
          </Button>
        </FallbackSection>
      </Container>

      <Toast show={toast.show} success={toast.success} aria-live="polite">
        {toast.message}
      </Toast>
    </Layout>
  );
}

