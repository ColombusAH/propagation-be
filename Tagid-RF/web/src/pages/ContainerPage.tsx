import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { QRGenerator } from '@/components/QRGenerator';
import { useStore } from '@/store';
import { useTranslation } from '@/hooks/useTranslation';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h1`
  margin-bottom: ${theme.spacing.lg};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.xl};

  @media (max-width: ${theme.breakpoints.tablet}) {
    grid-template-columns: 1fr;
  }
`;

const Section = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  margin-bottom: ${theme.spacing.md};
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const Label = styled.label`
  font-weight: ${theme.typography.fontWeight.medium};
`;

const Input = styled.input`
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  background: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: background ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.primaryDark};
  }

  &:disabled {
    background: ${theme.colors.borderDark};
    cursor: not-allowed;
  }
`;

const ContainerList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const ContainerCard = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const ContainerInfo = styled.div`
  flex: 1;
`;

const ContainerName = styled.h3`
  margin: 0 0 ${theme.spacing.xs} 0;
`;

const ContainerBarcode = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textLight};
  font-family: monospace;
`;

const ProductCount = styled.span`
  background: ${theme.colors.primary};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.sm};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${theme.spacing.xs};
`;

const IconButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  background: transparent;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.surface};
    border-color: ${theme.colors.primary};
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing.xl};
  color: ${theme.colors.textLight};
`;

const Modal = styled.div<{ $show: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: ${props => props.$show ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: ${theme.zIndex.modal};
`;

const ModalContent = styled.div`
  background: white;
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.lg};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: ${theme.borderRadius.sm};
  transition: background ${theme.transitions.fast};
  
  &:hover {
    background: ${theme.colors.surfaceHover};
  }
`;

const ProductList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
  margin-top: ${theme.spacing.md};
`;

const ProductItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${theme.spacing.sm};
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.sm};
`;

const Select = styled.select`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  flex: 1;
`;

export function ContainerPage() {
    const { t, formatPrice } = useTranslation();
    const {
        containers,
        addContainer,
        removeContainer,
        products,
        getProductById,
        addProductToContainer,
        removeProductFromContainer
    } = useStore();

    const [name, setName] = useState('');
    const [barcode, setBarcode] = useState('');
    const [selectedContainer, setSelectedContainer] = useState<string | null>(null);
    const [showQRModal, setShowQRModal] = useState(false);
    const [qrValue, setQrValue] = useState('');
    const [selectedProductId, setSelectedProductId] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (name && barcode) {
            addContainer({
                name,
                barcode,
                products: [],
            });
            setName('');
            setBarcode('');
        }
    };

    const handleShowQR = (containerBarcode: string) => {
        setQrValue(containerBarcode);
        setShowQRModal(true);
    };

    const handleAddProductToContainer = () => {
        if (selectedContainer && selectedProductId) {
            addProductToContainer(selectedContainer, selectedProductId, 1);
            setSelectedProductId('');
        }
    };

    const selectedContainerData = selectedContainer
        ? containers.find(c => c.id === selectedContainer)
        : null;

    return (
        <Layout>
            <Container>
                <Title>🛁 {t('containers.title')}</Title>

                <Grid>
                    {/* Create New Container */}
                    <Section>
                        <SectionTitle>➕ {t('containers.create')}</SectionTitle>
                        <Form onSubmit={handleSubmit}>
                            <FormGroup>
                                <Label>{t('containers.name')}</Label>
                                <Input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="e.g., אמבטיה A1"
                                />
                            </FormGroup>
                            <FormGroup>
                                <Label>{t('containers.barcode')}</Label>
                                <Input
                                    type="text"
                                    value={barcode}
                                    onChange={(e) => setBarcode(e.target.value)}
                                    placeholder="e.g., CONTAINER-001"
                                />
                            </FormGroup>
                            <Button type="submit" disabled={!name || !barcode}>
                                {t('containers.create')}
                            </Button>
                        </Form>
                    </Section>

                    {/* Container List */}
                    <Section>
                        <SectionTitle>📦 {t('containers.title')}</SectionTitle>
                        {containers.length === 0 ? (
                            <EmptyState>{t('containers.empty')}</EmptyState>
                        ) : (
                            <ContainerList>
                                {containers.map((container) => (
                                    <ContainerCard key={container.id}>
                                        <ContainerInfo>
                                            <ContainerName>{container.name}</ContainerName>
                                            <ContainerBarcode>{container.barcode}</ContainerBarcode>
                                        </ContainerInfo>
                                        <ProductCount>
                                            {container.products.reduce((sum, p) => sum + p.qty, 0)} {t('containers.products')}
                                        </ProductCount>
                                        <ActionButtons>
                                            <IconButton onClick={() => setSelectedContainer(container.id)} title="Edit">
                                                ✏️
                                            </IconButton>
                                            <IconButton onClick={() => handleShowQR(container.barcode)} title="QR">
                                                📱
                                            </IconButton>
                                            <IconButton onClick={() => removeContainer(container.id)} title="Delete">
                                                🗑️
                                            </IconButton>
                                        </ActionButtons>
                                    </ContainerCard>
                                ))}
                            </ContainerList>
                        )}
                    </Section>
                </Grid>

                {/* Edit Container Modal */}
                <Modal $show={!!selectedContainer} onClick={() => setSelectedContainer(null)}>
                    <ModalContent onClick={(e) => e.stopPropagation()}>
                        <ModalHeader>
                            <h2>{selectedContainerData?.name}</h2>
                            <CloseButton onClick={() => setSelectedContainer(null)}>×</CloseButton>
                        </ModalHeader>

                        <FormGroup>
                            <Label>{t('containers.addProduct')}</Label>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <Select
                                    value={selectedProductId}
                                    onChange={(e) => setSelectedProductId(e.target.value)}
                                >
                                    <option value="">-- Select Product --</option>
                                    {products.map((product) => (
                                        <option key={product.id} value={product.id}>
                                            {product.name} ({formatPrice(product.priceInCents)})
                                        </option>
                                    ))}
                                </Select>
                                <Button
                                    type="button"
                                    onClick={handleAddProductToContainer}
                                    disabled={!selectedProductId}
                                >
                                    +
                                </Button>
                            </div>
                        </FormGroup>

                        <ProductList>
                            {selectedContainerData?.products.map((item) => {
                                const product = getProductById(item.productId);
                                return (
                                    <ProductItem key={item.productId}>
                                        <span>{product?.name} × {item.qty}</span>
                                        <IconButton
                                            onClick={() => selectedContainer && removeProductFromContainer(selectedContainer, item.productId)}
                                        >
                                            🗑️
                                        </IconButton>
                                    </ProductItem>
                                );
                            })}
                            {selectedContainerData?.products.length === 0 && (
                                <EmptyState>No products in this container</EmptyState>
                            )}
                        </ProductList>
                    </ModalContent>
                </Modal>

                {/* QR Code Modal */}
                <Modal $show={showQRModal} onClick={() => setShowQRModal(false)}>
                    <ModalContent onClick={(e) => e.stopPropagation()}>
                        <ModalHeader>
                            <h2>{t('containers.generateQR')}</h2>
                            <CloseButton onClick={() => setShowQRModal(false)}>×</CloseButton>
                        </ModalHeader>
                        <QRGenerator initialValue={qrValue} />
                    </ModalContent>
                </Modal>
            </Container>
        </Layout>
    );
}
