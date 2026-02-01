import { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { QRCodeSVG } from 'qrcode.react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useWebSocket } from '@/hooks/useWebSocket';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1200px;
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

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.xl};

  @media (max-width: 900px) {
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
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  margin: 0 0 ${theme.spacing.md} 0;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};

  .material-symbols-outlined {
    font-size: 28px;
    color: ${theme.colors.primary};
  }
`;

const ScanButton = styled.button`
  width: 100%;
  padding: ${theme.spacing.xl};
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.xl};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.md};
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.lg};

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px ${theme.colors.primary}40;
  }

  &:active {
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .material-symbols-outlined {
    font-size: 32px;
  }
`;

const ManualInput = styled.div`
  margin-top: ${theme.spacing.lg};
  padding-top: ${theme.spacing.lg};
  border-top: 1px solid ${theme.colors.border};
`;

const InputGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
`;

const Input = styled.input`
  flex: 1;
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

const AddButton = styled.button`
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  background: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.primaryDark};
  }
`;

const TagsList = styled.div`
  margin-top: ${theme.spacing.lg};
  max-height: 400px;
  overflow-y: auto;
`;

const TagItem = styled.div<{ $selected?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${theme.spacing.md};
  border: 2px solid ${props => props.$selected ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  background: ${props => props.$selected ? `${theme.colors.primary}10` : 'white'};

  &:hover {
    border-color: ${theme.colors.primary};
    background: ${theme.colors.primary}05;
  }
`;

const TagInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const TagEpc = styled.span`
  font-family: monospace;
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text};
  font-weight: ${theme.typography.fontWeight.semibold};
`;

const TagMeta = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
`;

const TagStatus = styled.span<{ $paid?: boolean }>`
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  background: ${props => props.$paid ? theme.colors.successLight : theme.colors.warningLight};
  color: ${props => props.$paid ? theme.colors.successDark : theme.colors.warningDark};
`;

const QRSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.lg};
`;

const QRContainer = styled.div`
  background: white;
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  border: 3px solid ${theme.colors.primary};
  box-shadow: ${theme.shadows.lg};
`;

const QRLabel = styled.div`
  text-align: center;
  margin-top: ${theme.spacing.md};
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  font-family: monospace;
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

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['3xl']};
  color: ${theme.colors.textMuted};

  .material-symbols-outlined {
    font-size: 64px;
    color: ${theme.colors.primary}40;
    margin-bottom: ${theme.spacing.md};
  }
`;

const NoSelection = styled.div`
  text-align: center;
  padding: ${theme.spacing['3xl']};
  color: ${theme.colors.textMuted};

  .material-symbols-outlined {
    font-size: 80px;
    color: ${theme.colors.primary}30;
    margin-bottom: ${theme.spacing.md};
  }

  p {
    margin: ${theme.spacing.sm} 0;
  }
`;

interface ScannedTag {
  id: string;
  epc: string;
  scannedAt: Date;
  isPaid: boolean;
  productName?: string;
}

export function TagScannerPage() {
  const { userRole, token } = useAuth();
  const [scannedTags, setScannedTags] = useState<ScannedTag[]>([]);
  const [selectedTag, setSelectedTag] = useState<ScannedTag | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [manualEpc, setManualEpc] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  const printRef = useRef<HTMLDivElement>(null);

  // WebSocket for real-time tag updates
  const { status } = useWebSocket({
    url: '/ws/rfid',
    autoConnect: true,
    onMessage: (msg) => {
      // Only process tags if we are actively scanning
      if (!isScanning) return;

      if (msg.type === 'tag_scanned') {
        const tagData = msg.data;
        // Add tag if not already present
        setScannedTags(prev => {
          if (prev.find(t => t.epc === tagData.epc)) {
            return prev;
          }
          const newTag: ScannedTag = {
            id: crypto.randomUUID(),
            epc: tagData.epc,
            scannedAt: new Date(),
            isPaid: false // Default new tags to unpaid/unmapped
          };
          return [newTag, ...prev];
        });
      }
    }
  });

  useEffect(() => {
    setWsConnected(status === 'connected');
  }, [status]);

  // Sync state with backend on mount
  useEffect(() => {
    const fetchStatus = async () => {
      if (!token) return;
      try {
        const response = await fetch('/api/v1/rfid-scan/status', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setIsScanning(data.is_scanning);
        }
      } catch (error) {
        console.error('Error fetching scanner status:', error);
      }
    };

    fetchStatus();
  }, [token]);

  // Clean up scanning on unmount
  useEffect(() => {
    return () => {
      if (isScanning) {
        stopScanning();
      }
    };
  }, [isScanning]);

  const isManager = userRole && ['SUPER_ADMIN', 'NETWORK_MANAGER', 'NETWORK_ADMIN', 'STORE_MANAGER'].includes(userRole);

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

  const generateEncryptedQR = (epc: string): string => {
    const timestamp = Date.now();
    const encoded = btoa(`${epc}:${timestamp}`);
    return `TAGID-${encoded}`;
  };

  const startScanning = async () => {
    if (!token) return;
    try {
      const response = await fetch('/api/v1/rfid-scan/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        setIsScanning(true);
      } else {
        console.error('Failed to start scanning');
        alert('שגיאה בהפעלת הסורק');
      }
    } catch (error) {
      console.error('Error starting scan:', error);
      alert('שגיאת תקשורת עם הסורק');
    }
  };

  const stopScanning = async () => {
    if (!token) return;
    try {
      const response = await fetch('/api/v1/rfid-scan/stop', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        setIsScanning(false);
      } else {
        console.error('Failed to stop scanning');
      }
    } catch (error) {
      console.error('Error stopping scan:', error);
    }
  };

  const toggleScan = () => {
    if (isScanning) {
      stopScanning();
    } else {
      startScanning();
    }
  };

  const addTag = (epc: string) => {
    const upperEpc = epc.toUpperCase();
    if (scannedTags.find(t => t.epc === upperEpc)) {
      return;
    }

    const newTag: ScannedTag = {
      id: crypto.randomUUID(),
      epc: upperEpc,
      scannedAt: new Date(),
      isPaid: false,
    };

    setScannedTags(prev => [newTag, ...prev]);
    setSelectedTag(newTag);
  };

  const handleManualAdd = () => {
    if (manualEpc.trim()) {
      addTag(manualEpc.trim());
      setManualEpc('');
    }
  };

  const handlePrint = () => {
    if (!selectedTag) return;

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const qrValue = generateEncryptedQR(selectedTag.epc);

    printWindow.document.write(`
      <!DOCTYPE html>
      <html dir="rtl" lang="he">
      <head>
        <title>QR Code - ${selectedTag.epc}</title>
        <style>
          body {
            font-family: 'Heebo', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
          }
          .qr-container {
            border: 2px solid #2563EB;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
          }
          .epc {
            font-family: monospace;
            font-size: 12px;
            color: #666;
            margin-top: 10px;
          }
          @media print {
            body { margin: 0; }
          }
        </style>
      </head>
      <body>
        <div class="qr-container">
          <svg id="qr"></svg>
          <div class="epc">${selectedTag.epc}</div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
        <script>
          QRCode.toDataURL('${qrValue}', { width: 200 }, function(err, url) {
            const img = document.createElement('img');
            img.src = url;
            img.style.width = '200px';
            document.getElementById('qr').replaceWith(img);
            setTimeout(() => window.print(), 500);
          });
        </script>
      </body>
      </html>
    `);
    printWindow.document.close();
  };

  return (
    <Layout>
      <Container>
        <Header>
          <Title>סריקת תגים והפקת QR</Title>
          <Subtitle>סרוק תגי RFID חדשים והפק קודי QR להדבקה על המוצרים</Subtitle>
        </Header>

        <Grid>
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
              <CardTitle style={{ margin: 0 }}>
                <span className="material-symbols-outlined">contactless</span>
                סריקת תגים
                <span style={{
                  fontSize: '0.8rem',
                  marginRight: '12px',
                  color: wsConnected ? theme.colors.success : theme.colors.error,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>
                    {wsConnected ? 'wifi' : 'wifi_off'}
                  </span>
                  {wsConnected ? 'מחובר' : 'מנותק'}
                </span>
              </CardTitle>

              {scannedTags.length > 0 && (
                <button
                  onClick={() => {
                    if (window.confirm('האם אתה בטוח שברצונך לנקות את כל התגים?')) {
                      setScannedTags([]);
                      setSelectedTag(null);
                    }
                  }}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: theme.colors.error,
                    cursor: 'pointer',
                    fontSize: theme.typography.fontSize.sm,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '4px 8px',
                    borderRadius: theme.borderRadius.md,
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = theme.colors.error + '10'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>delete_sweep</span>
                  נקה הכל
                </button>
              )}
            </div>

            <ScanButton onClick={toggleScan} disabled={!wsConnected && !isScanning}>
              <span className="material-symbols-outlined">
                {isScanning ? 'stop_circle' : 'sensors'}
              </span>
              {isScanning ? 'עצור סריקה' : 'התחל סריקה'}
            </ScanButton>

            <ManualInput>
              <p style={{ margin: `0 0 ${theme.spacing.md} 0`, color: theme.colors.textSecondary, fontSize: theme.typography.fontSize.sm }}>
                או הזן קוד EPC ידנית:
              </p>
              <InputGroup>
                <Input
                  type="text"
                  placeholder="E200001234567890"
                  value={manualEpc}
                  onChange={(e) => setManualEpc(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleManualAdd()}
                />
                <AddButton onClick={handleManualAdd}>
                  <span className="material-symbols-outlined">add</span>
                  הוסף
                </AddButton>
              </InputGroup>
            </ManualInput>

            <TagsList>
              {scannedTags.length === 0 ? (
                <EmptyState>
                  <span className="material-symbols-outlined">nfc</span>
                  <p>לא נסרקו תגים עדיין</p>
                  <p style={{ fontSize: theme.typography.fontSize.sm }}>לחץ על "התחל סריקה" או הזן EPC ידנית</p>
                </EmptyState>
              ) : (
                scannedTags.map(tag => (
                  <TagItem
                    key={tag.id}
                    $selected={selectedTag?.id === tag.id}
                    onClick={() => setSelectedTag(tag)}
                  >
                    <TagInfo>
                      <TagEpc>{tag.epc}</TagEpc>
                      <TagMeta>
                        נסרק: {tag.scannedAt.toLocaleTimeString('he-IL')}
                        {tag.productName && ` | ${tag.productName}`}
                      </TagMeta>
                    </TagInfo>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <TagStatus $paid={tag.isPaid}>
                        {tag.isPaid ? 'שולם' : 'לא משויך'}
                      </TagStatus>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setScannedTags(prev => prev.filter(t => t.id !== tag.id));
                          if (selectedTag?.id === tag.id) {
                            setSelectedTag(null);
                          }
                        }}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: theme.colors.textMuted,
                          cursor: 'pointer',
                          padding: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          borderRadius: '50%',
                          transition: 'all 0.2s',
                        }}
                        onMouseOver={(e) => {
                          e.currentTarget.style.color = theme.colors.error;
                          e.currentTarget.style.backgroundColor = theme.colors.error + '10';
                        }}
                        onMouseOut={(e) => {
                          e.currentTarget.style.color = theme.colors.textMuted;
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }}
                        title="מחק תג"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>delete</span>
                      </button>
                    </div>
                  </TagItem>
                ))
              )}
            </TagsList>
          </Card>

          <Card>
            <CardTitle>
              <span className="material-symbols-outlined">qr_code_2</span>
              קוד QR להדפסה
            </CardTitle>

            {selectedTag ? (
              <QRSection ref={printRef}>
                <QRContainer>
                  <QRCodeSVG
                    value={generateEncryptedQR(selectedTag.epc)}
                    size={200}
                    level="H"
                    includeMargin
                    fgColor="#1E3A8A"
                  />
                  <QRLabel>{selectedTag.epc}</QRLabel>
                </QRContainer>

                <PrintButton onClick={handlePrint}>
                  <span className="material-symbols-outlined">print</span>
                  הדפס QR
                </PrintButton>

                <p style={{ textAlign: 'center', fontSize: theme.typography.fontSize.sm, color: theme.colors.textMuted }}>
                  הדבק את קוד ה-QR על התג או על המוצר
                </p>
              </QRSection>
            ) : (
              <NoSelection>
                <span className="material-symbols-outlined">qr_code_scanner</span>
                <p style={{ fontSize: theme.typography.fontSize.lg, fontWeight: 500 }}>בחר תג מהרשימה</p>
                <p>לאחר בחירת תג, קוד ה-QR יוצג כאן להדפסה</p>
              </NoSelection>
            )}
          </Card>
        </Grid>
      </Container>
    </Layout>
  );
}
