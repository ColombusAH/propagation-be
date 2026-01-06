import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { QRGenerator } from '@/components/QRGenerator';
import { useTranslation } from '@/hooks/useTranslation';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 800px;
  margin: 0 auto;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.text};
`;

const Description = styled.p`
  text-align: center;
  color: ${theme.colors.textLight};
  margin-bottom: ${theme.spacing.xl};
`;

const TypeSelector = styled.div`
  display: flex;
  justify-content: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
  flex-wrap: wrap;
`;

const TypeButton = styled.button<{ $active: boolean }>`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  border: 2px solid ${props => props.$active ? theme.colors.primary : theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  background: ${props => props.$active ? theme.colors.primary : 'white'};
  color: ${props => props.$active ? 'white' : theme.colors.text};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    border-color: ${theme.colors.primary};
  }
`;

const HistorySection = styled.div`
  margin-top: ${theme.spacing.xl};
  padding: ${theme.spacing.lg};
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.lg};
`;

const HistoryTitle = styled.h3`
  margin-bottom: ${theme.spacing.md};
`;

const HistoryList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${theme.spacing.sm};
`;

const HistoryItem = styled.button`
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  &:hover {
    border-color: ${theme.colors.primary};
  }
`;

const EmptyHistory = styled.p`
  color: ${theme.colors.textLight};
  font-size: ${theme.typography.fontSize.sm};
`;

type QRType = 'custom' | 'product' | 'container';

export function QRGeneratorPage() {
    const { t } = useTranslation();
    const [type, setType] = useState<QRType>('custom');
    const [history, setHistory] = useState<string[]>(() => {
        const saved = localStorage.getItem('qr-history');
        return saved ? JSON.parse(saved) : [];
    });
    const [currentValue, setCurrentValue] = useState('');

    const handleGenerate = (value: string) => {
        if (!value || history.includes(value)) return;

        const newHistory = [value, ...history].slice(0, 10); // Keep last 10
        setHistory(newHistory);
        localStorage.setItem('qr-history', JSON.stringify(newHistory));
    };

    const handleHistoryClick = (value: string) => {
        setCurrentValue(value);
    };

    return (
        <Layout>
            <Container>
                <Title>🏷️ {t('qr.title')}</Title>
                <Description>
                    {t('qr.inputPlaceholder')}
                </Description>

                <TypeSelector>
                    <TypeButton
                        $active={type === 'custom'}
                        onClick={() => setType('custom')}
                    >
                        📝 {t('qr.typeCustom')}
                    </TypeButton>
                    <TypeButton
                        $active={type === 'product'}
                        onClick={() => setType('product')}
                    >
                        📦 {t('qr.typeProduct')}
                    </TypeButton>
                    <TypeButton
                        $active={type === 'container'}
                        onClick={() => setType('container')}
                    >
                        🛁 {t('qr.typeContainer')}
                    </TypeButton>
                </TypeSelector>

                <QRGenerator
                    key={currentValue} // Force re-render when history item clicked
                    initialValue={currentValue}
                    onGenerate={handleGenerate}
                />

                {history.length > 0 && (
                    <HistorySection>
                        <HistoryTitle>📋 Recent QR Codes</HistoryTitle>
                        <HistoryList>
                            {history.map((item, index) => (
                                <HistoryItem
                                    key={index}
                                    onClick={() => handleHistoryClick(item)}
                                    title={item}
                                >
                                    {item}
                                </HistoryItem>
                            ))}
                        </HistoryList>
                    </HistorySection>
                )}

                {history.length === 0 && (
                    <HistorySection>
                        <HistoryTitle>📋 Recent QR Codes</HistoryTitle>
                        <EmptyHistory>No QR codes generated yet.</EmptyHistory>
                    </HistorySection>
                )}
            </Container>
        </Layout>
    );
}
