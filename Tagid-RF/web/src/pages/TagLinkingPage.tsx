import { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { QRCodeSVG } from 'qrcode.react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useWebSocket } from '@/hooks/useWebSocket';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(180deg, ${theme.colors.gray[50]} 0%, ${theme.colors.gray[100]} 100%);
  min-height: calc(100vh - 64px);
  animation: ${theme.animations.fadeIn};
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.lg};
  border-right: 10px solid ${theme.colors.primaryDark};
  color: white;
  animation: ${theme.animations.slideUp};

  h1, p {
    color: white;
  }
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  margin: 0;
  line-height: 1.2;
`;

const Subtitle = styled.p`
  margin: ${theme.spacing.sm} 0 0 0;
  opacity: 0.9;
`;

const StepsContainer = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
`;

const Step = styled.div<{ $active?: boolean; $completed?: boolean }>`
  flex: 1;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background: ${props => props.$active ? theme.colors.primary : props.$completed ? theme.colors.success : 'white'};
  color: ${props => (props.$active || props.$completed) ? 'white' : theme.colors.text};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.sm};
  transition: all ${theme.transitions.base};

  .step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: ${props => (props.$active || props.$completed) ? 'rgba(255,255,255,0.2)' : theme.colors.gray[100]};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: ${theme.typography.fontWeight.bold};
  }

  .step-text {
    font-weight: ${theme.typography.fontWeight.semibold};
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: ${theme.spacing.lg};

  @media (max-width: 1200px) {
    grid-template-columns: 1fr 1fr;
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.xl};
  box-shadow: ${theme.shadows.md};
  animation: ${theme.animations.slideUp};
`;

const CardTitle = styled.h2`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  margin: 0 0 ${theme.spacing.md} 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};

  .material-symbols-outlined {
    font-size: 24px;
    color: ${theme.colors.primary};
  }
`;

const TabsContainer = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  margin-bottom: ${theme.spacing.lg};
`;

const Tab = styled.button<{ $active?: boolean }>`
  flex: 1;
  padding: ${theme.spacing.md};
  background: ${props => props.$active ? theme.colors.primary : theme.colors.gray[50]};
  color: ${props => props.$active ? 'white' : theme.colors.text};
  border: 2px solid ${props => props.$active ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};

  &:hover {
    border-color: ${theme.colors.primary};
  }

  .material-symbols-outlined {
    font-size: 20px;
  }
`;

const FormGroup = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin-bottom: ${theme.spacing.xs};
`;

const Input = styled.input`
  width: 100%;
  padding: ${theme.spacing.md};
  border: 2px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.base};
  transition: all ${theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}20;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: ${theme.spacing.md};
  border: 2px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.base};
  background: white;
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}20;
  }
`;

const UploadZone = styled.div<{ $dragOver?: boolean }>`
  border: 2px dashed ${props => props.$dragOver ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  text-align: center;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  background: ${props => props.$dragOver ? `${theme.colors.primary}05` : 'white'};

  &:hover {
    border-color: ${theme.colors.primary};
    background: ${theme.colors.primary}05;
  }

  .material-symbols-outlined {
    font-size: 48px;
    color: ${theme.colors.primary};
    margin-bottom: ${theme.spacing.sm};
  }
`;

const ProductList = styled.div`
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
`;

const ProductItem = styled.div<{ $selected?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  background: ${props => props.$selected ? `${theme.colors.primary}10` : 'white'};
  border-right: ${props => props.$selected ? `3px solid ${theme.colors.primary}` : 'none'};

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: ${theme.colors.primary}05;
  }
`;

const ProductInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ProductName = styled.span`
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
`;

const ProductMeta = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textMuted};
`;

const TagsList = styled.div`
  max-height: 300px;
  overflow-y: auto;
`;

const TagItem = styled.div<{ $selected?: boolean }>`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  padding: ${theme.spacing.md};
  border: 2px solid ${props => props.$selected ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  background: ${props => props.$selected ? `${theme.colors.primary}10` : 'white'};

  &:hover {
    border-color: ${theme.colors.primary};
  }
`;

const Checkbox = styled.div<{ $checked?: boolean }>`
  width: 24px;
  height: 24px;
  border: 2px solid ${props => props.$checked ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  background: ${props => props.$checked ? theme.colors.primary : 'white'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all ${theme.transitions.fast};

  .material-symbols-outlined {
    font-size: 16px;
  }
`;

const TagEpc = styled.span`
  font-family: monospace;
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text};
`;

const ActionButton = styled.button`
  width: 100%;
  padding: ${theme.spacing.lg};
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.lg};

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px ${theme.colors.primary}40;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  .material-symbols-outlined {
    font-size: 24px;
  }
`;

const SecondaryButton = styled.button`
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background: white;
  color: ${theme.colors.primary};
  border: 2px solid ${theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.sm};
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.primary}05;
  }

  .material-symbols-outlined {
    font-size: 20px;
  }
`;

const ResultsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: ${theme.spacing.md};
  max-height: 400px;
  overflow-y: auto;
`;

const QRCard = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md};
  text-align: center;
`;

const QRLabel = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text};
  margin-top: ${theme.spacing.sm};
  font-weight: ${theme.typography.fontWeight.semibold};
`;

const QREpc = styled.div`
  font-family: monospace;
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
  margin-top: 2px;
  word-break: break-all;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing.xl};
  color: ${theme.colors.textMuted};

  .material-symbols-outlined {
    font-size: 48px;
    color: ${theme.colors.primary}40;
    margin-bottom: ${theme.spacing.sm};
  }
`;

const Badge = styled.span`
  background: ${theme.colors.primary};
  color: white;
  padding: 2px 8px;
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  margin-right: ${theme.spacing.sm};
`;

const PrintButton = styled.button`
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.success} 0%, ${theme.colors.successDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  transition: all ${theme.transitions.fast};
  box-shadow: ${theme.shadows.md};

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.lg};
  }

  .material-symbols-outlined {
    font-size: 20px;
  }
`;

const TemplateActions = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  margin-top: ${theme.spacing.md};
`;

const TemplateButton = styled.button`
  flex: 1;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background: ${theme.colors.gray[50]};
  color: ${theme.colors.primary};
  border: 2px solid ${theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.primary}10;
  }

  .material-symbols-outlined {
    font-size: 18px;
  }
`;

const categories = [
  'ביגוד',
  'הנעלה',
  'אלקטרוניקה',
  'אביזרים',
  'קוסמטיקה',
  'מזון',
  'משקאות',
  'אחר',
];

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  sku?: string;
}

interface UnlinkedTag {
  id: string;
  epc: string;
  scannedAt: Date;
}

interface LinkedTag {
  tag: UnlinkedTag;
  product: Product;
  qrCode: string;
}

export function TagLinkingPage() {
  const { userRole } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [loadMode, setLoadMode] = useState<'template' | 'manual'>('manual');
  const [dragOver, setDragOver] = useState(false);

  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);

  const [newProductName, setNewProductName] = useState('');
  const [newProductPrice, setNewProductPrice] = useState('');
  const [newProductCategory, setNewProductCategory] = useState('');
  const [newProductSku, setNewProductSku] = useState('');

  const [availableTags, setAvailableTags] = useState<UnlinkedTag[]>([]);
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());

  const [linkedResults, setLinkedResults] = useState<LinkedTag[]>([]);

  const isManager = userRole && ['SUPER_ADMIN', 'NETWORK_ADMIN', 'STORE_MANAGER'].includes(userRole);

  if (!isManager) {
    return (
      <Layout>
        <Container>
          <Card>
            <CardTitle>אין גישה</CardTitle>
            <p>עמוד זה זמין רק למנהלים</p>
          </Card>
        </Container>
      </Layout>
    );
  }

  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        let parsedProducts: Product[] = [];

        if (file.name.endsWith('.json')) {
          parsedProducts = JSON.parse(content);
        } else if (file.name.endsWith('.csv')) {
          const lines = content.split('\n').filter(l => l.trim());
          const headers = lines[0].split(',').map(h => h.trim().toLowerCase());

          parsedProducts = lines.slice(1).map((line, idx) => {
            const values = line.split(',').map(v => v.trim());
            return {
              id: `import-${idx}`,
              name: values[headers.indexOf('name')] || values[0] || '',
              price: parseFloat(values[headers.indexOf('price')] || values[1]) || 0,
              category: values[headers.indexOf('category')] || values[2] || '',
              sku: values[headers.indexOf('sku')] || values[3] || '',
            };
          }).filter(p => p.name);
        }

        setProducts(prev => [...prev, ...parsedProducts]);
      } catch (err) {
        console.error('Failed to parse file:', err);
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const handleAddProduct = () => {
    if (!newProductName.trim()) return;

    const newProduct: Product = {
      id: `manual-${Date.now()}`,
      name: newProductName.trim(),
      price: parseFloat(newProductPrice) || 0,
      category: newProductCategory,
      sku: newProductSku.trim(),
    };

    setProducts(prev => [...prev, newProduct]);
    setSelectedProduct(newProduct);
    setNewProductName('');
    setNewProductPrice('');
    setNewProductCategory('');
    setNewProductSku('');
  };

  const handleToggleTag = (tagId: string) => {
    setSelectedTags(prev => {
      const next = new Set(prev);
      if (next.has(tagId)) {
        next.delete(tagId);
      } else {
        next.add(tagId);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    const tagsToSelect = availableTags.slice(0, quantity).map(t => t.id);
    setSelectedTags(new Set(tagsToSelect));
  };

  const generateQRCode = (tag: UnlinkedTag, product: Product): string => {
    return JSON.stringify({
      epc: tag.epc,
      productId: product.id,
      productName: product.name,
      price: product.price,
      timestamp: Date.now(),
    });
  };

  const handleLinkTags = async () => {
    if (!selectedProduct) return;

    const tagsToLink = availableTags.filter(t => selectedTags.has(t.id));
    const newLinkedTags: LinkedTag[] = [];
    const errors: string[] = [];

    // Simple sequential processing for now to avoid race conditions/overwhelm
    for (const tag of tagsToLink) {
      try {
        // Update tag with product info via POST /api/v1/tags/
        // This will create or update the tag
        const response = await fetch('/api/v1/tags/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            epc: tag.epc,
            product_name: selectedProduct.name,
            product_sku: selectedProduct.sku,
            price_cents: Math.round(selectedProduct.price * 100), // Convert to cents
            is_active: true
          })
        });

        if (!response.ok) throw new Error(`Failed to link tag ${tag.epc}`);

        // If we also want to create a mapping for the QR (encrypted), we could call /tag-mapping/create
        // But for now, we'll just generate the QR locally as before or assume unencrypted for this use case.
        // The current requirements focus is on "Productionizing Tag Linking" to remove mock data.

        newLinkedTags.push({
          tag,
          product: selectedProduct,
          qrCode: generateQRCode(tag, selectedProduct)
        });

      } catch (err) {
        console.error(err);
        errors.push(tag.epc);
      }
    }

    if (newLinkedTags.length > 0) {
      setLinkedResults(prev => [...prev, ...newLinkedTags]);
      // Remove linked tags from available list
      setAvailableTags(prev => prev.filter(t => {
        const isLinked = newLinkedTags.some(lt => lt.tag.id === t.id);
        return !isLinked;
      }));
      setSelectedTags(new Set());
    }

    if (errors.length > 0) {
      alert(`Failed to link ${errors.length} tags. Check console for details.`);
    }
  };

  const handlePrint = () => {
    if (linkedResults.length === 0) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    printWindow.document.write(`
      <!DOCTYPE html>
      <html dir="rtl" lang="he">
      <head>
        <title>תגי QR - ${selectedProduct?.name || 'מוצרים'}</title>
        <style>
          body {
            font-family: 'Heebo', sans-serif;
            margin: 0;
            padding: 20px;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
          }
          .qr-item {
            border: 1px solid #ddd;
            padding: 15px;
            text-align: center;
            border-radius: 8px;
            page-break-inside: avoid;
          }
          .qr-item img {
            width: 120px;
            height: 120px;
          }
          .product-name {
            font-weight: bold;
            margin-top: 10px;
            color: #2563EB;
          }
          .epc {
            font-family: monospace;
            font-size: 10px;
            color: #666;
            margin-top: 5px;
            word-break: break-all;
          }
          @media print {
            body { margin: 0; }
            .qr-item { break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="grid">
          ${linkedResults.map(lr => `
            <div class="qr-item">
              <div id="qr-${lr.tag.id}"></div>
              <div class="product-name">${lr.product.name}</div>
              <div class="epc">${lr.tag.epc}</div>
            </div>
          `).join('')}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
        <script>
          const data = ${JSON.stringify(linkedResults.map(lr => ({ id: lr.tag.id, qr: lr.qrCode })))};
          Promise.all(data.map(item => 
            QRCode.toDataURL(item.qr, { width: 120 }).then(url => {
              const container = document.getElementById('qr-' + item.id);
              const img = document.createElement('img');
              img.src = url;
              container.appendChild(img);
            })
          )).then(() => setTimeout(() => window.print(), 500));
        </script>
      </body>
      </html>
    `);
    printWindow.document.close();
  };

  const { token } = useAuth();

  // Fetch initial available tags
  const fetchAvailableTags = useCallback(async () => {
    console.log('[TagLinkingPage] Fetching available tags...');
    try {
      const response = await fetch('/api/v1/rfid-scan/available', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('[TagLinkingPage] Fetch response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('[TagLinkingPage] Fetched tags data:', data);
        // Map API response to UnlinkedTag format
        const formattedTags = data.map((t: any) => ({
          id: t.epc, // Use EPC as ID 
          epc: t.epc,
          scannedAt: new Date(t.scannedAt || Date.now())
        }));
        setAvailableTags(formattedTags);
      } else {
        console.error('[TagLinkingPage] Failed to fetch tags:', await response.text());
      }
    } catch (error) {
      console.error('[TagLinkingPage] Failed to fetch tags error:', error);
    }
  }, [token]);

  useEffect(() => {
    fetchAvailableTags();
  }, [fetchAvailableTags]);

  // WebSocket for real-time updates
  const handleWebSocketMessage = useCallback((data: any) => {
    // console.log('[TagLinkingPage] WS Message:', data.type);
    if (data.type === 'tag_scanned') {
      const tagData = data.data;
      // Only add if NOT already linked (no product info)
      if (!tagData.product_sku && !tagData.product_name) {
        console.log('[TagLinkingPage] New unlinked tag scanned:', tagData.epc);
        setAvailableTags(prev => {
          // Avoid duplicates
          if (prev.some(t => t.epc === tagData.epc)) {
            return prev;
          }
          return [{
            id: tagData.epc,
            epc: tagData.epc,
            scannedAt: new Date(tagData.timestamp || Date.now())
          }, ...prev];
        });
      }
    }
  }, []);

  useWebSocket({
    url: '/ws/rfid',
    onMessage: handleWebSocketMessage
  });


  const handleDownloadTemplate = (format: 'csv' | 'json') => {
    if (format === 'csv') {
      const csvContent = `name,sku,price,category
חולצה כחולה L,SKU-001,99.90,ביגוד
מכנסי ג'ינס,SKU-002,199.00,ביגוד
נעלי ספורט,SKU-003,349.00,הנעלה`;
      const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'products_template.csv';
      a.click();
      URL.revokeObjectURL(url);
    } else {
      const jsonContent = [
        { name: 'חולצה כחולה L', sku: 'SKU-001', price: 99.90, category: 'ביגוד' },
        { name: 'מכנסי ג\'ינס', sku: 'SKU-002', price: 199.00, category: 'ביגוד' },
        { name: 'נעלי ספורט', sku: 'SKU-003', price: 349.00, category: 'הנעלה' },
      ];
      const blob = new Blob([JSON.stringify(jsonContent, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'products_template.json';
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const currentStep = !selectedProduct ? 1 : selectedTags.size === 0 ? 2 : 3;

  return (
    <Layout>
      <Container>
        <Header>
          <Title>צימוד מהיר - תגים למוצרים</Title>
          <Subtitle>טען מוצרים מתבנית או הזן ידנית, בחר כמות, וקשר תגים בקליק אחד</Subtitle>
        </Header>

        <StepsContainer>
          <Step $active={currentStep === 1} $completed={currentStep > 1}>
            <div className="step-number">1</div>
            <div className="step-text">בחר מוצר</div>
          </Step>
          <Step $active={currentStep === 2} $completed={currentStep > 2}>
            <div className="step-number">2</div>
            <div className="step-text">בחר תגים</div>
          </Step>
          <Step $active={currentStep === 3}>
            <div className="step-number">3</div>
            <div className="step-text">הדפסה</div>
          </Step>
        </StepsContainer>

        <Grid>
          <Card>
            <CardTitle>
              <span className="material-symbols-outlined">inventory_2</span>
              מוצרים
            </CardTitle>

            <TabsContainer>
              <Tab $active={loadMode === 'manual'} onClick={() => setLoadMode('manual')}>
                <span className="material-symbols-outlined">edit</span>
                הזנה ידנית
              </Tab>
              <Tab $active={loadMode === 'template'} onClick={() => setLoadMode('template')}>
                <span className="material-symbols-outlined">upload_file</span>
                טעינה מקובץ
              </Tab>
            </TabsContainer>

            {loadMode === 'template' ? (
              <>
                <UploadZone
                  $dragOver={dragOver}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <span className="material-symbols-outlined">cloud_upload</span>
                  <p>גרור קובץ CSV או JSON לכאן</p>
                  <p style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.textMuted }}>
                    או לחץ לבחירה
                  </p>
                </UploadZone>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file);
                  }}
                />
                <TemplateActions>
                  <TemplateButton onClick={() => handleDownloadTemplate('csv')}>
                    <span className="material-symbols-outlined">download</span>
                    הורד תבנית CSV
                  </TemplateButton>
                  <TemplateButton onClick={() => handleDownloadTemplate('json')}>
                    <span className="material-symbols-outlined">download</span>
                    הורד תבנית JSON
                  </TemplateButton>
                </TemplateActions>
              </>
            ) : (
              <>
                <FormGroup>
                  <Label>שם המוצר *</Label>
                  <Input
                    type="text"
                    placeholder='לדוגמה: חולצה כחולה L'
                    value={newProductName}
                    onChange={(e) => setNewProductName(e.target.value)}
                  />
                </FormGroup>
                <FormGroup>
                  <Label>מחיר (ש"ח)</Label>
                  <Input
                    type="number"
                    placeholder="0.00"
                    value={newProductPrice}
                    onChange={(e) => setNewProductPrice(e.target.value)}
                    step="0.01"
                    min="0"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>קטגוריה</Label>
                  <Select
                    value={newProductCategory}
                    onChange={(e) => setNewProductCategory(e.target.value)}
                  >
                    <option value="">בחר קטגוריה</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </Select>
                </FormGroup>
                <FormGroup>
                  <Label>מק"ט (אופציונלי)</Label>
                  <Input
                    type="text"
                    placeholder="SKU-12345"
                    value={newProductSku}
                    onChange={(e) => setNewProductSku(e.target.value)}
                  />
                </FormGroup>
                <SecondaryButton
                  onClick={handleAddProduct}
                  style={{ width: '100%' }}
                >
                  <span className="material-symbols-outlined">add</span>
                  הוסף מוצר
                </SecondaryButton>
              </>
            )}

            {products.length > 0 && (
              <>
                <Label style={{ marginTop: theme.spacing.lg }}>
                  מוצרים זמינים <Badge>{products.length}</Badge>
                </Label>
                <ProductList>
                  {products.map(product => (
                    <ProductItem
                      key={product.id}
                      $selected={selectedProduct?.id === product.id}
                      onClick={() => setSelectedProduct(product)}
                    >
                      <ProductInfo>
                        <ProductName>{product.name}</ProductName>
                        <ProductMeta>
                          {product.price.toFixed(2)} ש"ח | {product.category || 'ללא קטגוריה'}
                        </ProductMeta>
                      </ProductInfo>
                      {selectedProduct?.id === product.id && (
                        <span className="material-symbols-outlined" style={{ color: theme.colors.primary }}>
                          check_circle
                        </span>
                      )}
                    </ProductItem>
                  ))}
                </ProductList>
              </>
            )}

            {selectedProduct && (
              <FormGroup style={{ marginTop: theme.spacing.lg }}>
                <Label>כמות פריטים לצימוד</Label>
                <Input
                  type="number"
                  min="1"
                  max={availableTags.length || 100}
                  value={quantity}
                  onChange={(e) => {
                    setQuantity(parseInt(e.target.value) || 1);
                    setSelectedTags(new Set());
                  }}
                />
              </FormGroup>
            )}
          </Card>

          <Card>
            <CardTitle>
              <span className="material-symbols-outlined">sell</span>
              תגים זמינים
              {availableTags.length > 0 && <Badge>{availableTags.length}</Badge>}
            </CardTitle>

            <div style={{ display: 'flex', gap: theme.spacing.sm, marginBottom: theme.spacing.md }}>
              <SecondaryButton onClick={fetchAvailableTags}>
                <span className="material-symbols-outlined">refresh</span>
                רענן תגים
              </SecondaryButton>
              {availableTags.length > 0 && selectedProduct && (
                <SecondaryButton onClick={handleSelectAll}>
                  <span className="material-symbols-outlined">select_all</span>
                  בחר {quantity}
                </SecondaryButton>
              )}
            </div>

            <TagsList>
              {availableTags.length === 0 ? (
                <EmptyState>
                  <span className="material-symbols-outlined">label_off</span>
                  <p>אין תגים זמינים</p>
                  <p style={{ fontSize: theme.typography.fontSize.sm }}>סרוק תגים או לחץ "סמלץ תגים"</p>
                </EmptyState>
              ) : (
                availableTags.map(tag => (
                  <TagItem
                    key={tag.id}
                    $selected={selectedTags.has(tag.id)}
                    onClick={() => handleToggleTag(tag.id)}
                  >
                    <Checkbox $checked={selectedTags.has(tag.id)}>
                      {selectedTags.has(tag.id) && (
                        <span className="material-symbols-outlined">check</span>
                      )}
                    </Checkbox>
                    <TagEpc style={{ flex: 1 }}>{tag.epc}</TagEpc>
                  </TagItem>
                ))
              )}
            </TagsList>

            {selectedProduct && selectedTags.size > 0 && (
              <ActionButton
                onClick={handleLinkTags}
                style={{ marginTop: theme.spacing.lg }}
              >
                <span className="material-symbols-outlined">link</span>
                צמד {selectedTags.size} תגים ל-{selectedProduct.name}
              </ActionButton>
            )}
          </Card>

          <Card>
            <CardTitle>
              <span className="material-symbols-outlined">qr_code_2</span>
              תגים מקושרים
              {linkedResults.length > 0 && <Badge>{linkedResults.length}</Badge>}
            </CardTitle>

            {linkedResults.length > 0 && (
              <PrintButton onClick={handlePrint} style={{ marginBottom: theme.spacing.lg }}>
                <span className="material-symbols-outlined">print</span>
                הדפס {linkedResults.length} תגים
              </PrintButton>
            )}

            {linkedResults.length === 0 ? (
              <EmptyState>
                <span className="material-symbols-outlined">qr_code</span>
                <p>אין תגים מקושרים</p>
                <p style={{ fontSize: theme.typography.fontSize.sm }}>בחר מוצר ותגים לצימוד והדפסה</p>
              </EmptyState>
            ) : (
              <>
                <Label style={{ marginBottom: theme.spacing.sm }}>סיכום לפי מוצר:</Label>
                <ProductList style={{ marginBottom: theme.spacing.lg, maxHeight: '150px' }}>
                  {Object.entries(
                    linkedResults.reduce((acc, lr) => {
                      const key = lr.product.id;
                      if (!acc[key]) {
                        acc[key] = { product: lr.product, count: 0 };
                      }
                      acc[key].count++;
                      return acc;
                    }, {} as Record<string, { product: Product; count: number }>)
                  ).map(([id, { product, count }]) => (
                    <ProductItem key={id}>
                      <ProductInfo>
                        <ProductName>{product.name}</ProductName>
                        <ProductMeta>{product.category} | {product.price.toFixed(2)} ש"ח</ProductMeta>
                      </ProductInfo>
                      <Badge>{count} תגים</Badge>
                    </ProductItem>
                  ))}
                </ProductList>

                <Label style={{ marginBottom: theme.spacing.sm }}>תגים ({linkedResults.length}):</Label>
                <ResultsGrid>
                  {linkedResults.map(lr => (
                    <QRCard key={lr.tag.id}>
                      <QRCodeSVG
                        value={lr.qrCode}
                        size={100}
                        level="M"
                        fgColor="#1E40AF"
                      />
                      <QRLabel>{lr.product.name}</QRLabel>
                      <QREpc>{lr.tag.epc.substring(0, 12)}...</QREpc>
                    </QRCard>
                  ))}
                </ResultsGrid>
              </>
            )}
          </Card>
        </Grid>
      </Container>
    </Layout>
  );
}
