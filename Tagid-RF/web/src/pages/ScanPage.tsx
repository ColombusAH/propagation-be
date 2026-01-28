import { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { CameraView } from '@/components/CameraView';
import { EmptyState } from '@/components/EmptyState';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';
import { useWebSocket } from '@/hooks/useWebSocket';

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

const RFIDSection = styled.div`
  background-color: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-top: ${theme.spacing.lg};
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.md};
`;

const StatusIndicator = styled.div<{ $connected: boolean }>`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};
  font-size: ${theme.typography.fontSize.xs};
  color: ${props => props.$connected ? theme.colors.success : theme.colors.error};
  
  &::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: currentColor;
    box-shadow: 0 0 5px currentColor;
  }
`;

const TagList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
  max-height: 300px;
  overflow-y: auto;
  padding-right: ${theme.spacing.xs};
`;

const TagItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  background: rgba(255, 255, 255, 0.05);
  border-radius: ${theme.borderRadius.md};
  border-right: 3px solid ${theme.colors.primary};
`;

const TagInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const TagEpc = styled.span`
  font-family: monospace;
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const TagRssi = styled.div<{ $level: number }>`
  display: flex;
  align-items: center;
  gap: 2px;
  
  & > div {
    width: 3px;
    background: ${props => props.$level > 1 ? theme.colors.success : theme.colors.textMuted};
    border-radius: 1px;
  }
`;

const RSSIBar = styled.div<{ $active: boolean, $height: string }>`
  height: ${props => props.$height};
  width: 3px;
  background: ${props => props.$active ? theme.colors.success : 'rgba(255,255,255,0.1)'};
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
  const [recentTags, setRecentTags] = useState<any[]>([]);

  const { status: wsStatus } = useWebSocket({
    url: '/ws/rfid',
    onMessage: (message) => {
      if (message.type === 'tag_scanned') {
        const tag = message.data;
        handleScan(tag.epc, 'rfid');

        // Add to recent tags list
        setRecentTags(prev => {
          const filtered = prev.filter(t => t.epc !== tag.epc);
          return [tag, ...filtered].slice(0, 10);
        });
      }
    }
  });

  const showScanResult = (result: ScanResultData) => {
    setScanResult(result);
    setTimeout(() => {
      setScanResult(null);
    }, 4000);
  };

  const handleScan = (code: string, method: 'barcode' | 'rfid' = 'barcode') => {
    const isRfid = method === 'rfid';

    if (isContainer(code)) {
      const container = getContainerByBarcode(code);
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

    const success = addByBarcode(code);
    if (success) {
      const product = getProductByBarcode(code);
      showScanResult({
        type: 'product',
        title: isRfid ? t('scan.rfidTagScanned') : t('scan.productFound'),
        message: product?.name || (isRfid ? `EPC: ${code}` : t('scan.product'))
      });
    } else {
      showScanResult({
        type: 'product',
        title: isRfid ? t('scan.rfidTagUnknown') : t('scan.productNotFound'),
        message: isRfid ? t('scan.rfidTagNotLinked', { epc: code }) : t('scan.barcodeNotRecognized')
      });
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualBarcode.trim()) {
      // Logic for testing: if it looks like EPC (hex, long), treat as RFID
      const isHex = /^[0-9A-Fa-f]+$/.test(manualBarcode.trim());
      const method = (isHex && manualBarcode.length > 12) ? 'rfid' : 'barcode';
      handleScan(manualBarcode.trim(), method);
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
          <Title>{t('scan.title')}</Title>
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
            <MaterialIcon name="keyboard" /> {t('scan.manualInput')}
          </FallbackTitle>
          <form onSubmit={handleManualSubmit}>
            <InputGroup>
              <Input
                type="text"
                placeholder={t('scan.manualPlaceholder')}
                value={manualBarcode}
                onChange={(e) => setManualBarcode(e.target.value)}
              />
              <Button type="submit" disabled={!manualBarcode.trim()}>
                <MaterialIcon name="add" /> {t('scan.add')}
              </Button>
            </InputGroup>
          </form>
        </FallbackSection>

        <RFIDSection>
          <SectionHeader>
            <FallbackTitle>
              <MaterialIcon name="sensors" /> {t('scan.rfidReader')}
            </FallbackTitle>
            <StatusIndicator $connected={wsStatus === 'connected'}>
              {wsStatus === 'connected' ? t('scan.connected') : t('scan.connecting')}
            </StatusIndicator>
          </SectionHeader>

          {recentTags.length === 0 ? (
            <div style={{ textAlign: 'center', opacity: 0.5, padding: '20px' }}>
              {t('scan.waitingForTags')}
            </div>
          ) : (
            <TagList>
              {recentTags.map((tag, idx) => {
                // Calculate RSSI level for bars (0 to 4)
                // Assuming RSSI is between -90 and -30
                const rssi = tag.rssi || -70;
                const level = Math.max(0, Math.min(4, Math.floor((rssi + 90) / 15)));

                return (
                  <TagItem key={`${tag.epc}-${idx}`}>
                    <TagInfo>
                      <TagEpc>{tag.epc}</TagEpc>
                      <span style={{ fontSize: '10px', opacity: 0.7 }}>
                        RSSI: {rssi} dBm | Ant: {tag.antenna_port || 1}
                      </span>
                    </TagInfo>
                    <TagRssi $level={level}>
                      <RSSIBar $active={level >= 1} $height="4px" />
                      <RSSIBar $active={level >= 2} $height="8px" />
                      <RSSIBar $active={level >= 3} $height="12px" />
                      <RSSIBar $active={level >= 4} $height="16px" />
                    </TagRssi>
                  </TagItem>
                );
              })}
            </TagList>
          )}
        </RFIDSection>

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
