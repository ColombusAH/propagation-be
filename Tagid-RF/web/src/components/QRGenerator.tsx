import { useState, useRef } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.lg};
  padding: ${theme.spacing.lg};
`;

const InputContainer = styled.div`
  width: 100%;
  max-width: 400px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${theme.spacing.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const Input = styled.input`
  width: 100%;
  padding: ${theme.spacing.md};
  border: 2px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  transition: border-color ${theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const QRContainer = styled.div`
  background: white;
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.lg};
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const QRWrapper = styled.div`
  padding: ${theme.spacing.md};
  background: white;
`;

const SizeSelector = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  align-items: center;
`;

const SizeButton = styled.button<{ $active: boolean }>`
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border: 1px solid ${props => props.$active ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  background: ${props => props.$active ? theme.colors.primary : 'white'};
  color: ${props => props.$active ? 'white' : theme.colors.text};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    border-color: ${theme.colors.primary};
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  flex-wrap: wrap;
  justify-content: center;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  background: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: background-color ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.primaryDark};
  }

  &:disabled {
    background: ${theme.colors.borderDark};
    cursor: not-allowed;
  }
`;

const Placeholder = styled.div`
  width: 200px;
  height: 200px;
  background: ${theme.colors.surface};
  border: 2px dashed ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${theme.colors.textLight};
  font-size: ${theme.typography.fontSize.sm};
  text-align: center;
  padding: ${theme.spacing.md};
`;

interface QRGeneratorProps {
    initialValue?: string;
    onGenerate?: (value: string) => void;
}

export function QRGenerator({ initialValue = '', onGenerate }: QRGeneratorProps) {
    const { t } = useTranslation();
    const [value, setValue] = useState(initialValue);
    const [size, setSize] = useState<128 | 200 | 256>(200);
    const qrRef = useRef<HTMLDivElement>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue(e.target.value);
    };

    const handleDownload = () => {
        if (!qrRef.current || !value) return;

        const svg = qrRef.current.querySelector('svg');
        if (!svg) return;

        // Create canvas and convert SVG to PNG
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const svgData = new XMLSerializer().serializeToString(svg);
        const img = new Image();

        canvas.width = size;
        canvas.height = size;

        img.onload = () => {
            ctx?.drawImage(img, 0, 0);
            const pngUrl = canvas.toDataURL('image/png');

            const link = document.createElement('a');
            link.download = `qr-${value.substring(0, 20)}.png`;
            link.href = pngUrl;
            link.click();
        };

        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    };

    const handlePrint = () => {
        if (!qrRef.current || !value) return;

        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        const svg = qrRef.current.querySelector('svg');
        if (!svg) return;

        printWindow.document.write(`
      <html>
        <head>
          <title>QR Code - ${value}</title>
          <style>
            body {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              margin: 0;
              font-family: Arial, sans-serif;
            }
            .code { margin-bottom: 20px; font-size: 14px; word-break: break-all; max-width: 300px; text-align: center; }
          </style>
        </head>
        <body>
          ${svg.outerHTML}
          <div class="code">${value}</div>
        </body>
      </html>
    `);
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
    };

    const handleGenerate = () => {
        if (onGenerate && value) {
            onGenerate(value);
        }
    };

    return (
        <Container>
            <InputContainer>
                <Label>{t('qr.inputLabel')}</Label>
                <Input
                    type="text"
                    value={value}
                    onChange={handleInputChange}
                    placeholder={t('qr.inputPlaceholder')}
                />
            </InputContainer>

            <SizeSelector>
                <span>{t('qr.size')}:</span>
                {([128, 200, 256] as const).map((s) => (
                    <SizeButton
                        key={s}
                        $active={size === s}
                        onClick={() => setSize(s)}
                    >
                        {s}px
                    </SizeButton>
                ))}
            </SizeSelector>

            <QRContainer>
                {value ? (
                    <QRWrapper ref={qrRef}>
                        <QRCodeSVG
                            value={value}
                            size={size}
                            level="H"
                            includeMargin
                        />
                    </QRWrapper>
                ) : (
                    <Placeholder>
                        {t('qr.inputPlaceholder')}
                    </Placeholder>
                )}

                <ButtonGroup>
                    <ActionButton onClick={handleDownload} disabled={!value}>
                        📥 {t('qr.download')}
                    </ActionButton>
                    <ActionButton onClick={handlePrint} disabled={!value}>
                        🖨️ {t('qr.print')}
                    </ActionButton>
                    {onGenerate && (
                        <ActionButton onClick={handleGenerate} disabled={!value}>
                            ✓ {t('qr.generate')}
                        </ActionButton>
                    )}
                </ButtonGroup>
            </QRContainer>
        </Container>
    );
}
