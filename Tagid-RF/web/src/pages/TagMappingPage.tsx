import { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { QRCodeSVG } from 'qrcode.react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { Link } from 'react-router-dom';

// --- Types ---

interface InventoryProduct {
    id: string;
    name: string;
    sku: string;
    minStock: number;
    count: number;
    status: 'OK' | 'LOW_STOCK' | 'OUT_OF_STOCK';
    price: number; // Added for Print
    category: string; // Added for Print
}

interface UnlinkedTag {
    id: string;
    epc: string;
    scannedAt: Date;
}

interface LinkedTag {
    tag: UnlinkedTag;
    product: InventoryProduct;
    qrCode: string; // The encrypted QR string
}

// --- API ---

const INVENTORY_API = '/api/v1/inventory';
const TAGS_API = '/api/v1/tags';

// --- Components ---

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem;
  background-color: #f8fafc;
  min-height: 100vh;
`;

const PageHeader = styled.div`
  position: relative;
  background: linear-gradient(120deg, #2563eb 0%, #1e40af 100%);
  padding: 3rem 2rem;
  border-radius: 24px;
  color: white;
  margin-bottom: 2rem;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
    transform: translate(30%, -30%);
    border-radius: 50%;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div<{ $type?: 'warning' | 'default' }>`
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
  border: 1px solid ${props => props.$type === 'warning' ? '#fef3c7' : '#f3f4f6'};
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
  }

  h3 {
    color: ${props => props.$type === 'warning' ? '#d97706' : '#6b7280'};
    font-size: 0.875rem;
    font-weight: 500;
  }

  p {
    color: ${props => props.$type === 'warning' ? '#b45309' : '#111827'};
    font-size: 2rem;
    font-weight: 700;
  }
`;

const StyledTable = styled.table`
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  
  th {
    background: #f9fafb;
    padding: 1rem;
    text-align: right;
    font-weight: 600;
    color: #4b5563;
    border-bottom: 1px solid #e5e7eb;
    &:first-child { border-radius: 0 12px 0 0; }
    &:last-child { border-radius: 12px 0 0 0; }
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid #f3f4f6;
    background: white;
    transition: background 0.15s;
    vertical-align: middle;
  }

  tr:hover td {
    background: #f8fafc;
  }
  
  tr:last-child td {
    border-bottom: none;
    &:first-child { border-radius: 0 0 12px 0; }
    &:last-child { border-radius: 0 0 0 12px; }
  }
`;

const MinStockInput = styled.input`
  width: 80px;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
`;

const StatusBadge = styled.span<{ type: string }>`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  
  ${({ type }) => {
        switch (type) {
            case 'OK': return `background: #dcfce7; color: #166534;`;
            case 'LOW_STOCK': return `background: #ffedd5; color: #9a3412;`;
            case 'OUT_OF_STOCK': return `background: #fee2e2; color: #991b1b;`;
            default: return `background: #f3f4f6; color: #4b5563;`;
        }
    }}
`;

const Card = styled.div`
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
  margin-bottom: 1.5rem;
  border: 1px solid #f3f4f6;
`;

const MaterialIcon = ({ name, size = 20 }: { name: string; size?: number }) => (
    <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
`;

const ModalContent = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 24px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  animation: slideUp 0.3s ease-out;

  @keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
`;

// --- Main Component ---

export function TagMappingPage() {
    const { token } = useAuth();
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Inventory State
    const [inventory, setInventory] = useState<InventoryProduct[]>([]);
    const [loadingInv, setLoadingInv] = useState(false);

    // Add Product State
    const [isAddMode, setIsAddMode] = useState(false);
    const [loadMode, setLoadMode] = useState<'template' | 'manual'>('manual');
    const [dragOver, setDragOver] = useState(false);
    const [creating, setCreating] = useState(false);

    const [newProductName, setNewProductName] = useState('');
    const [newProductPrice, setNewProductPrice] = useState('');
    const [newProductCategory, setNewProductCategory] = useState('');
    const [newProductSku, setNewProductSku] = useState('');
    const [newProductMinStock, setNewProductMinStock] = useState('');

    // Linking State
    const [linkingProduct, setLinkingProduct] = useState<InventoryProduct | null>(null);
    const [availableTags, setAvailableTags] = useState<UnlinkedTag[]>([]);
    const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());
    const [linkedResults, setLinkedResults] = useState<LinkedTag[]>([]);
    const [linking, setLinking] = useState(false);

    const CATEGORIES = [
        'ביגוד', 'הנעלה', 'אלקטרוניקה', 'אביזרים', 'קוסמטיקה', 'מזון', 'משקאות', 'אחר'
    ];

    // Stats
    const totalItems = inventory.reduce((acc, curr) => acc + curr.count, 0);
    const lowStockItems = inventory.filter(i => i.status !== 'OK').length;
    const totalProducts = inventory.length;

    // --- Inventory Actions ---

    const fetchInventory = async () => {
        setLoadingInv(true);
        try {
            const res = await fetch(`${INVENTORY_API}/stock`);
            if (res.ok) {
                const data = await res.json();
                setInventory(data.products || []);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoadingInv(false);
        }
    };

    const updateMinStock = async (id: string, newVal: number) => {
        try {
            await fetch(`${INVENTORY_API}/product/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ minStock: newVal })
            });
            setInventory(prev => prev.map(p => p.id === id ? { ...p, minStock: newVal } : p));
        } catch (e) { console.error(e); }
    };

    useEffect(() => {
        fetchInventory();
    }, []);

    // --- Product Creation Actions ---

    const createProductAPI = async (prod: any) => {
        const payload = {
            name: prod.name,
            price: prod.price || 0,
            sku: prod.sku || undefined,
            category: prod.category || 'General',
            description: '',
            store_id: 'store-default',
            minStock: prod.minStock || 0
        };
        const res = await fetch(`${TAGS_API}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Failed to create product');
        return await res.json();
    };

    const handleAddProduct = async () => {
        if (!newProductName.trim()) return;
        setCreating(true);
        try {
            await createProductAPI({
                name: newProductName.trim(),
                price: parseFloat(newProductPrice) || 0,
                category: newProductCategory,
                sku: newProductSku.trim(),
                minStock: parseInt(newProductMinStock) || 0
            });

            setNewProductName('');
            setNewProductPrice('');
            setNewProductCategory('');
            setNewProductSku('');
            setNewProductMinStock('');

            fetchInventory();
            setIsAddMode(false);
        } catch (e) {
            console.error(e);
            alert('שגיאה ביצירת מוצר');
        } finally {
            setCreating(false);
        }
    };

    const handleFileUpload = (file: File) => {
        const reader = new FileReader();
        reader.onload = async (e) => {
            setCreating(true);
            try {
                const content = e.target?.result as string;
                let parsedProducts: any[] = [];
                if (file.name.endsWith('.json')) {
                    parsedProducts = JSON.parse(content);
                } else if (file.name.endsWith('.csv')) {
                    const lines = content.split('\n').filter(l => l.trim());
                    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
                    parsedProducts = lines.slice(1).map((line) => {
                        const values = line.split(',').map(v => v.trim());
                        return {
                            name: values[headers.indexOf('name')] || values[0] || '',
                            price: parseFloat(values[headers.indexOf('price')] || values[1]) || 0,
                            category: values[headers.indexOf('category')] || values[2] || '',
                            sku: values[headers.indexOf('sku')] || values[3] || '',
                        };
                    }).filter(p => p.name);
                }
                for (const p of parsedProducts) {
                    await createProductAPI(p).catch(console.error);
                }
                fetchInventory();
                setIsAddMode(false);
            } catch (err) {
                console.error(err);
                alert('שגיאה בטעינת הקובץ');
            } finally {
                setCreating(false);
            }
        };
        reader.readAsText(file);
    };

    const handleDownloadTemplate = () => {
        const csvContent = "\uFEFFname,price,category,sku\nחולצה לדוגמה,99.90,ביגוד,SKU-EXAMPLE";
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'products_template.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // --- Linking Actions ---

    const openLinkingModal = (product: InventoryProduct) => {
        setLinkingProduct(product);
        setAvailableTags([]);
        setSelectedTags(new Set());
        setLinkedResults([]);
    };

    const simulateTags = () => {
        const newTags: UnlinkedTag[] = Array.from({ length: 5 }, (_, i) => ({
            id: `tag-${Date.now()}-${i}`,
            epc: `E200${Math.random().toString(16).substring(2, 14).toUpperCase()}`,
            scannedAt: new Date(),
        }));
        setAvailableTags(prev => [...prev, ...newTags]);
    };

    const handleToggleTag = (tagId: string) => {
        setSelectedTags(prev => {
            const next = new Set(prev);
            if (next.has(tagId)) next.delete(tagId);
            else next.add(tagId);
            return next;
        });
    };

    const registerTagAPI = async (epc: string) => {
        const res = await fetch(`${TAGS_API}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ epc, store_id: 'store-default' })
        });
        if (!res.ok) throw new Error('Failed to register tag');
        return res.json();
    };

    const linkTagAPI = async (tagId: string, productId: string) => {
        const res = await fetch(`${TAGS_API}/${tagId}/link-product`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        if (!res.ok) throw new Error('Failed to link tag');
        return res.json();
    };

    const handleLinkTags = async () => {
        if (!linkingProduct || selectedTags.size === 0) return;
        setLinking(true);
        const newLinkedTags: LinkedTag[] = [];

        try {
            for (const tagId of selectedTags) {
                const tag = availableTags.find(t => t.id === tagId);
                if (tag) {
                    try {
                        const registered = await registerTagAPI(tag.epc);
                        const linked = await linkTagAPI(registered.id, linkingProduct.id);
                        newLinkedTags.push({
                            tag: { ...tag, id: linked.id },
                            product: linkingProduct,
                            qrCode: linked.qr_code || JSON.stringify({ epc: linked.epc, productId: linkingProduct.id })
                        });
                    } catch (e) {
                        console.error(`Failed to link tag ${tag.epc}`, e);
                    }
                }
            }
            setLinkedResults(prev => [...prev, ...newLinkedTags]);
            // Remove from available
            setAvailableTags(prev => prev.filter(t => !selectedTags.has(t.id)));
            setSelectedTags(new Set());
            // Refresh Inventory to show updated count
            fetchInventory();
        } finally {
            setLinking(false);
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
            <title>תגי QR - ${linkingProduct?.name || 'מוצרים'}</title>
            <style>
              body { font-family: 'Heebo', sans-serif; margin: 0; padding: 20px; }
              .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
              .qr-item { border: 1px solid #ddd; padding: 15px; text-align: center; border-radius: 8px; page-break-inside: avoid; }
              .qr-item img { width: 120px; height: 120px; }
              .product-name { font-weight: bold; margin-top: 10px; color: #2563EB; }
              .epc { font-family: monospace; font-size: 10px; color: #666; margin-top: 5px; word-break: break-all; }
              @media print { .qr-item { break-inside: avoid; } }
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


    return (
        <Layout>
            <Container>
                <PageHeader>
                    <div className="relative z-10 flex flex-wrap justify-between items-end gap-4">
                        <div>
                            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                                <MaterialIcon name="inventory_2" size={40} />
                                ניהול מלאי
                            </h1>
                            <p className="text-blue-100/90 text-lg">מעקב מלאי, הוספת מוצרים וצימוד תגים במסך אחד</p>
                        </div>
                        <button
                            onClick={() => setIsAddMode(!isAddMode)}
                            className="bg-white text-blue-600 px-6 py-3 rounded-xl font-bold hover:bg-blue-50 transition-colors shadow-lg flex items-center gap-2"
                        >
                            <MaterialIcon name={isAddMode ? "close" : "add"} />
                            {isAddMode ? 'סגור הוספה' : 'הוסף מוצר חדש'}
                        </button>
                    </div>
                </PageHeader>

                <StatsGrid>
                    <StatCard>
                        <div className="flex justify-between items-start">
                            <div><h3>סה"כ פריטים במלאי</h3><p>{totalItems}</p></div>
                            <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><MaterialIcon name="layers" size={24} /></div>
                        </div>
                    </StatCard>
                    <StatCard>
                        <div className="flex justify-between items-start">
                            <div><h3>סוגי מוצרים</h3><p>{totalProducts}</p></div>
                            <div className="p-3 bg-purple-50 text-purple-600 rounded-lg"><MaterialIcon name="category" size={24} /></div>
                        </div>
                    </StatCard>
                    <StatCard $type={lowStockItems > 0 ? 'warning' : 'default'}>
                        <div className="flex justify-between items-start">
                            <div><h3>דורשים טיפול / מלאי נמוך</h3><p>{lowStockItems}</p></div>
                            <div className={`p-3 rounded-lg ${lowStockItems > 0 ? 'bg-orange-100 text-orange-600' : 'bg-green-50 text-green-600'}`}>
                                <MaterialIcon name={lowStockItems > 0 ? "warning" : "check_circle"} size={24} />
                            </div>
                        </div>
                    </StatCard>
                </StatsGrid>

                {isAddMode && (
                    <Card style={{ padding: '2rem', border: '2px solid #2563eb', marginBottom: '2rem' }}>
                        <h2 className="text-xl font-bold mb-6 text-blue-800 flex items-center gap-2">
                            <MaterialIcon name="add_box" />
                            הוספת מוצרים למלאי
                        </h2>

                        <div className="flex gap-4 mb-6">
                            <button
                                onClick={() => setLoadMode('manual')}
                                className={`flex-1 p-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${loadMode === 'manual' ? 'bg-blue-600 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                <MaterialIcon name="edit" /> הזנה ידנית
                            </button>
                            <button
                                onClick={() => setLoadMode('template')}
                                className={`flex-1 p-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${loadMode === 'template' ? 'bg-blue-600 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                <MaterialIcon name="upload_file" /> טעינה מקובץ
                            </button>
                        </div>

                        {loadMode === 'manual' ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                                <div><label className="block text-sm font-bold mb-1">שם המוצר *</label>
                                    <input className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={newProductName} onChange={e => setNewProductName(e.target.value)} placeholder="לדוגמה: חולצה כחולה" /></div>
                                <div><label className="block text-sm font-bold mb-1">מחיר</label>
                                    <input type="number" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={newProductPrice} onChange={e => setNewProductPrice(e.target.value)} placeholder="0.00" /></div>
                                <div><label className="block text-sm font-bold mb-1">קטגוריה</label>
                                    <select className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white" value={newProductCategory} onChange={e => setNewProductCategory(e.target.value)}>
                                        <option value="">בחר קטגוריה</option>{CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                                    </select></div>
                                <div><label className="block text-sm font-bold mb-1">מק"ט</label>
                                    <input className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={newProductSku} onChange={e => setNewProductSku(e.target.value)} placeholder="SKU-123" /></div>
                                <div><label className="block text-sm font-bold mb-1">מלאי מינימום</label>
                                    <input type="number" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" value={newProductMinStock} onChange={e => setNewProductMinStock(e.target.value)} placeholder="10" /></div>
                                <div className="md:col-span-2 mt-4">
                                    <button onClick={handleAddProduct} disabled={creating || !newProductName} className="w-full py-4 bg-green-600 text-white rounded-xl font-bold text-lg hover:bg-green-700 shadow-md flex justify-center items-center gap-2">
                                        {creating ? 'יוצר...' : <><MaterialIcon name="add" /> הוסף מוצר למערכת</>}
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
                                    onDragOver={e => { e.preventDefault(); setDragOver(true); }} onDragLeave={() => setDragOver(false)} onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) handleFileUpload(e.dataTransfer.files[0]) }} onClick={() => fileInputRef.current?.click()}>
                                    <MaterialIcon name="cloud_upload" size={64} />
                                    <p className="text-xl mt-4 font-medium text-gray-600">גרור לכאן קובץ CSV או JSON</p>
                                    <input ref={fileInputRef} type="file" accept=".csv,.json" className="hidden" onChange={e => e.target.files?.[0] && handleFileUpload(e.target.files[0])} />
                                </div>
                                <div className="text-center">
                                    <button
                                        onClick={handleDownloadTemplate}
                                        className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center justify-center gap-2 mx-auto"
                                    >
                                        <MaterialIcon name="download" size={18} />
                                        הורד תבנית CSV לדוגמה
                                    </button>
                                </div>
                            </div>
                        )}
                    </Card>
                )}

                <Card>
                    <div className="flex justify-between items-center p-6 border-b border-gray-100 bg-white">
                        <div>
                            <h2 className="text-lg font-bold">פירוט מלאי לפי מוצר</h2>
                            <p className="text-sm text-gray-500">לחץ על כפתור הצימוד כדי להוסיף מלאי</p>
                        </div>
                        <div className="flex gap-2">
                            <Link to="/notification-settings" className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-blue-600 flex items-center gap-2 font-medium">
                                <MaterialIcon name="settings" size={18} /> הגדרות ערוצי התראה
                            </Link>
                            <button onClick={fetchInventory} className="p-2 rounded-lg text-gray-500 hover:bg-gray-100"><MaterialIcon name="refresh" /></button>
                        </div>
                    </div>
                    {loadingInv ? <div className="p-20 text-center text-gray-400">טוען...</div> : (
                        <div className="overflow-x-auto">
                            <StyledTable>
                                <thead>
                                    <tr>
                                        <th>שם מוצר</th>
                                        <th>מק"ט (SKU)</th>
                                        <th>מלאי בפועל</th>
                                        <th>התראה (מספר)</th>
                                        <th>סטטוס</th>
                                        <th>פעולות</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {inventory.map(prod => (
                                        <tr key={prod.id}>
                                            <td className="font-medium text-gray-900">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400"><MaterialIcon name="shopping_bag" /></div>
                                                    {prod.name}
                                                </div>
                                            </td>
                                            <td className="text-gray-500 font-mono text-sm">{prod.sku || '-'}</td>
                                            <td><span className="font-bold text-lg text-gray-800">{prod.count}</span><span className="text-xs text-gray-400 mr-1">יח'</span></td>
                                            <td><MinStockInput type="number" defaultValue={prod.minStock} onBlur={(e) => updateMinStock(prod.id, parseInt(e.target.value))} /></td>
                                            <td><StatusBadge type={prod.status}>{prod.status}</StatusBadge></td>
                                            <td>
                                                <button
                                                    onClick={() => openLinkingModal(prod)}
                                                    className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg font-medium hover:bg-blue-100 transition-colors flex items-center gap-2"
                                                >
                                                    <MaterialIcon name="link" size={18} />
                                                    צימוד
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </StyledTable>
                        </div>
                    )}
                </Card>

                {/* Linking Modal */}
                {linkingProduct && (
                    <ModalOverlay onClick={() => setLinkingProduct(null)}>
                        <ModalContent onClick={e => e.stopPropagation()}>
                            <div className="flex justify-between items-center mb-6 border-b pb-4">
                                <div>
                                    <h2 className="text-2xl font-bold flex items-center gap-2">
                                        <MaterialIcon name="link" size={32} />
                                        צימוד תגים למוצר
                                    </h2>
                                    <p className="text-gray-500 mt-1">
                                        מוצר: <span className="font-bold text-blue-600">{linkingProduct.name}</span>
                                        <span className="mx-2">|</span>
                                        מק"ט: {linkingProduct.sku || 'ללא'}
                                    </p>
                                </div>
                                <button onClick={() => setLinkingProduct(null)} className="p-2 hover:bg-gray-100 rounded-full">
                                    <MaterialIcon name="close" />
                                </button>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                {/* Left Side: Tag Scanning */}
                                <div>
                                    <div className="bg-gray-50 p-6 rounded-xl border border-gray-200 text-center mb-6">
                                        <div className="w-20 h-20 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <MaterialIcon name="sensors" size={40} />
                                        </div>
                                        <h3 className="text-lg font-bold mb-2">סריקת תגים</h3>
                                        <p className="text-gray-500 text-sm mb-4">קרב את התגים לקורא ה-RFID או בצע סימולציה</p>
                                        <button
                                            onClick={simulateTags}
                                            className="w-full py-3 bg-white border-2 border-blue-600 text-blue-600 rounded-xl font-bold hover:bg-blue-50 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <MaterialIcon name="waves" />
                                            סמלץ סריקה
                                        </button>
                                    </div>

                                    {availableTags.length > 0 && (
                                        <div className="border border-gray-200 rounded-xl overflow-hidden">
                                            <div className="bg-gray-50 p-3 border-b border-gray-200 font-bold flex justify-between">
                                                <span>תגים שנסרקו ({availableTags.length})</span>
                                                <button
                                                    className="text-sm text-blue-600"
                                                    onClick={() => setSelectedTags(new Set(availableTags.map(t => t.id)))}
                                                >
                                                    בחר הכל
                                                </button>
                                            </div>
                                            <div className="max-h-60 overflow-y-auto p-2">
                                                {availableTags.map(tag => (
                                                    <div
                                                        key={tag.id}
                                                        onClick={() => handleToggleTag(tag.id)}
                                                        className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${selectedTags.has(tag.id) ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50 border border-transparent'}`}
                                                    >
                                                        <div className={`w-5 h-5 rounded border flex items-center justify-center ${selectedTags.has(tag.id) ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-300'}`}>
                                                            {selectedTags.has(tag.id) && <MaterialIcon name="check" size={14} />}
                                                        </div>
                                                        <span className="font-mono text-sm">{tag.epc}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <button
                                        onClick={handleLinkTags}
                                        disabled={selectedTags.size === 0 || linking}
                                        className="w-full py-4 mt-6 bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-blue-700 shadow-lg disabled:opacity-50 flex justify-center items-center gap-2"
                                    >
                                        {linking ? 'מבצע צימוד...' : `צמד ${selectedTags.size} תגים נבחרים`}
                                    </button>
                                </div>

                                {/* Right Side: Results */}
                                <div className="border-r border-gray-200 pr-8">
                                    <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                                        <MaterialIcon name="qr_code_2" />
                                        תגים שצומדו בהצלחה ({linkedResults.length})
                                    </h3>

                                    {linkedResults.length > 0 ? (
                                        <>
                                            <div className="max-h-96 overflow-y-auto mb-4 grid grid-cols-2 gap-4">
                                                {linkedResults.map((lr, i) => (
                                                    <div key={i} className="border p-3 rounded-lg text-center bg-gray-50">
                                                        <QRCodeSVG value={lr.qrCode} size={80} className="mx-auto mb-2" />
                                                        <div className="text-xs font-mono text-gray-500 truncate">{lr.tag.epc}</div>
                                                    </div>
                                                ))}
                                            </div>
                                            <button
                                                onClick={handlePrint}
                                                className="w-full py-3 bg-gray-800 text-white rounded-xl font-bold hover:bg-gray-900 flex justify-center items-center gap-2"
                                            >
                                                <MaterialIcon name="print" />
                                                הדפס מדבקות QR
                                            </button>
                                        </>
                                    ) : (
                                        <div className="text-center py-12 text-gray-400 bg-gray-50 rounded-xl">
                                            <MaterialIcon name="qr_code_scanner" size={48} />
                                            <p className="mt-2">כאן יופיעו התגים לאחר הצימוד</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </ModalContent>
                    </ModalOverlay>
                )}
            </Container>
        </Layout>
    );
}
