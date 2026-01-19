import { useState } from 'react';
import styled from 'styled-components';
import { QRCodeSVG } from 'qrcode.react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
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

const ReadersList = styled.div`
  max-height: 400px;
  overflow-y: auto;
`;

const ReaderItem = styled.div<{ $selected?: boolean; $isBath?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${theme.spacing.md};
  border: 2px solid ${props => props.$selected ? theme.colors.primary : props.$isBath ? theme.colors.success : theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  background: ${props => props.$selected ? `${theme.colors.primary}10` : props.$isBath ? `${theme.colors.success}05` : 'white'};

  &:hover {
    border-color: ${theme.colors.primary};
    background: ${theme.colors.primary}05;
  }
`;

const ReaderInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ReaderName = styled.span`
  font-size: ${theme.typography.fontSize.base};
  color: ${theme.colors.text};
  font-weight: ${theme.typography.fontWeight.semibold};
`;

const ReaderMeta = styled.span`
  font-size: ${theme.typography.fontSize.xs};
  color: ${theme.colors.textMuted};
`;

const ReaderStatus = styled.span<{ $isBath?: boolean }>`
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  background: ${props => props.$isBath ? `${theme.colors.primary}20` : theme.colors.gray[100]};
  color: ${props => props.$isBath ? theme.colors.primary : theme.colors.textMuted};
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

const SaveButton = styled.button`
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

  &:hover {
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

const QRSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.lg};
  margin-top: ${theme.spacing.xl};
  padding-top: ${theme.spacing.xl};
  border-top: 1px solid ${theme.colors.border};
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

const InfoBox = styled.div`
  background: ${theme.colors.infoLight};
  border: 1px solid ${theme.colors.info};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.infoDark};
  display: flex;
  align-items: flex-start;
  gap: ${theme.spacing.sm};

  .material-symbols-outlined {
    font-size: 20px;
    flex-shrink: 0;
  }
`;

interface Reader {
    id: string;
    name: string;
    ip: string;
    port: number;
    type: 'gate' | 'bath' | 'handheld';
    bathName?: string;
    bathQrCode?: string;
}

export function BathSetupPage() {
    const { userRole } = useAuth();
    const [readers, setReaders] = useState<Reader[]>([]);
    const [selectedReader, setSelectedReader] = useState<Reader | null>(null);
    const [bathName, setBathName] = useState('');

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

    const handleSelectReader = (reader: Reader) => {
        setSelectedReader(reader);
        setBathName(reader.bathName || '');
    };

    const generateBathQR = (): string => {
        const timestamp = Date.now();
        const bathId = selectedReader?.id || 'unknown';
        return `BATH-${bathId}-${timestamp.toString(36).toUpperCase()}`;
    };

    const handleSave = () => {
        if (!selectedReader || !bathName.trim()) return;

        const qrCode = generateBathQR();

        setReaders(prev => prev.map(r =>
            r.id === selectedReader.id
                ? {
                    ...r,
                    type: 'bath' as const,
                    bathName: bathName.trim(),
                    bathQrCode: qrCode,
                }
                : r
        ));

        setSelectedReader(prev => prev ? {
            ...prev,
            type: 'bath',
            bathName: bathName.trim(),
            bathQrCode: qrCode,
        } : null);
    };

    const handlePrint = () => {
        if (!selectedReader?.bathQrCode) return;

        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        printWindow.document.write(`
      <!DOCTYPE html>
      <html dir="rtl" lang="he">
      <head>
        <title>QR Code - ${selectedReader.bathName}</title>
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
            border: 3px solid #2563EB;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            background: white;
          }
          .title {
            font-size: 24px;
            font-weight: bold;
            color: #2563EB;
            margin-bottom: 20px;
          }
          .subtitle {
            font-size: 14px;
            color: #666;
            margin-top: 15px;
          }
          @media print {
            body { margin: 0; }
          }
        </style>
      </head>
      <body>
        <div class="qr-container">
          <div class="title">${selectedReader.bathName}</div>
          <svg id="qr"></svg>
          <div class="subtitle">סרוק כדי להתחיל קניות</div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
        <script>
          QRCode.toDataURL('${selectedReader.bathQrCode}', { width: 250 }, function(err, url) {
            const img = document.createElement('img');
            img.src = url;
            img.style.width = '250px';
            document.getElementById('qr').replaceWith(img);
            setTimeout(() => window.print(), 500);
          });
        </script>
      </body>
      </html>
    `);
        printWindow.document.close();
    };

    const getReaderTypeLabel = (type: string) => {
        switch (type) {
            case 'gate': return 'שער יציאה';
            case 'bath': return 'אמבט קניות';
            case 'handheld': return 'נייד';
            default: return type;
        }
    };

    return (
        <Layout>
            <Container>
                <Header>
                    <Title>הגדרת אמבט קניות</Title>
                    <Subtitle>הגדר קורא RFID כאמבט קניות וקבל QR לזיהוי</Subtitle>
                </Header>

                <Grid>
                    <Card>
                        <CardTitle>
                            <span className="material-symbols-outlined">router</span>
                            קוראים זמינים
                        </CardTitle>

                        <InfoBox>
                            <span className="material-symbols-outlined">info</span>
                            <span>
                                אמבט קניות הוא קורא RFID שמשמש לסריקה אוטומטית של מוצרים בזמן שהלקוח מניח אותם בסל.
                                בחר קורא והגדר אותו כאמבט.
                            </span>
                        </InfoBox>

                        <ReadersList>
                            {readers.length === 0 ? (
                                <EmptyState>
                                    <span className="material-symbols-outlined">wifi_off</span>
                                    <p>לא נמצאו קוראים</p>
                                    <p style={{ fontSize: theme.typography.fontSize.sm }}>הוסף קוראים בהגדרות המערכת</p>
                                </EmptyState>
                            ) : (
                                readers.map(reader => (
                                    <ReaderItem
                                        key={reader.id}
                                        $selected={selectedReader?.id === reader.id}
                                        $isBath={reader.type === 'bath'}
                                        onClick={() => handleSelectReader(reader)}
                                    >
                                        <ReaderInfo>
                                            <ReaderName>{reader.name}</ReaderName>
                                            <ReaderMeta>
                                                {reader.ip}:{reader.port}
                                                {reader.bathName && ` | ${reader.bathName}`}
                                            </ReaderMeta>
                                        </ReaderInfo>
                                        <ReaderStatus $isBath={reader.type === 'bath'}>
                                            {getReaderTypeLabel(reader.type)}
                                        </ReaderStatus>
                                    </ReaderItem>
                                ))
                            )}
                        </ReadersList>
                    </Card>

                    <Card>
                        <CardTitle>
                            <span className="material-symbols-outlined">shopping_basket</span>
                            הגדרות אמבט
                        </CardTitle>

                        {selectedReader ? (
                            <>
                                <div style={{
                                    background: `${theme.colors.primary}10`,
                                    padding: theme.spacing.md,
                                    borderRadius: theme.borderRadius.lg,
                                    marginBottom: theme.spacing.lg,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: theme.spacing.sm,
                                }}>
                                    <span className="material-symbols-outlined" style={{ color: theme.colors.primary }}>router</span>
                                    <span style={{ fontWeight: 500 }}>{selectedReader.name}</span>
                                    <span style={{ color: theme.colors.textMuted, fontSize: theme.typography.fontSize.sm }}>
                                        ({selectedReader.ip})
                                    </span>
                                </div>

                                <FormGroup>
                                    <Label>שם האמבט *</Label>
                                    <Input
                                        type="text"
                                        placeholder='לדוגמה: אמבט קופה 1'
                                        value={bathName}
                                        onChange={(e) => setBathName(e.target.value)}
                                    />
                                </FormGroup>

                                <SaveButton
                                    onClick={handleSave}
                                    disabled={!bathName.trim()}
                                >
                                    <span className="material-symbols-outlined">save</span>
                                    הגדר כאמבט קניות
                                </SaveButton>

                                {selectedReader.bathQrCode && (
                                    <QRSection>
                                        <QRContainer>
                                            <QRCodeSVG
                                                value={selectedReader.bathQrCode}
                                                size={200}
                                                level="H"
                                                includeMargin
                                                fgColor="#1E40AF"
                                            />
                                            <QRLabel>{selectedReader.bathName}</QRLabel>
                                        </QRContainer>

                                        <PrintButton onClick={handlePrint}>
                                            <span className="material-symbols-outlined">print</span>
                                            הדפס QR לאמבט
                                        </PrintButton>

                                        <p style={{ textAlign: 'center', fontSize: theme.typography.fontSize.sm, color: theme.colors.textMuted }}>
                                            הדבק את קוד ה-QR ליד האמבט כדי שלקוחות יוכלו לסרוק ולהתחיל קניות
                                        </p>
                                    </QRSection>
                                )}
                            </>
                        ) : (
                            <NoSelection>
                                <span className="material-symbols-outlined">shopping_basket</span>
                                <p style={{ fontSize: theme.typography.fontSize.lg, fontWeight: 500 }}>בחר קורא מהרשימה</p>
                                <p>לאחר בחירת קורא, תוכל להגדיר אותו כאמבט קניות</p>
                            </NoSelection>
                        )}
                    </Card>
                </Grid>
            </Container>
        </Layout>
    );
}
