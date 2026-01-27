import { useState } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { useToast } from '@/hooks/useToast';
import { UserRole } from '@/contexts/AuthContext';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${theme.colors.backgroundAlt};
  padding: ${theme.spacing.xl};
`;

const Card = styled.div`
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing['3xl']};
  box-shadow: ${theme.shadows.xl};
  max-width: 400px;
  width: 100%;
  border: 1px solid ${theme.colors.border};
  text-align: center;
`;

const Title = styled.h2`
  color: ${theme.colors.primary};
  margin-bottom: ${theme.spacing.md};
`;

const Subtitle = styled.p`
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.xl};
`;

const CodeInput = styled.input`
  width: 100%;
  padding: ${theme.spacing.lg};
  font-size: 24px;
  text-align: center;
  letter-spacing: 8px;
  border: 2px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  margin-bottom: ${theme.spacing.xl};
  background: ${theme.colors.background};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primaryLight}40;
  }
`;

const VerifyButton = styled.button`
  width: 100%;
  padding: ${theme.spacing.md};
  background: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.lg};
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: ${theme.colors.primaryDark};
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

interface VerificationPageProps {
    email: string;
    onVerified: (role: UserRole, token: string) => void;
    onCancel: () => void;
}

export function VerificationPage({ email, onVerified, onCancel }: VerificationPageProps) {
    const [code, setCode] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const toast = useToast();

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        if (code.length < 6) {
            toast.error('נא להזין קוד תקין בן 6 ספרות');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/auth/verify-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, code }),
            });

            if (response.ok) {
                const data = await response.json();
                toast.success('האימייל אומת בהצלחה!');
                onVerified(data.role as UserRole, data.token);
            } else {
                const err = await response.json();
                toast.error(err.detail || 'קוד שגוי או שפג תוקפו');
            }
        } catch (error) {
            toast.error('שגיאת תקשורת');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container>
            <Card>
                <span className="material-symbols-outlined" style={{ fontSize: 48, color: theme.colors.primary }}>mark_email_read</span>
                <Title>אימות אימייל</Title>
                <Subtitle>
                    שלחנו קוד אימות לכתובת:
                    <br />
                    <strong>{email}</strong>
                </Subtitle>

                <form onSubmit={handleVerify}>
                    <CodeInput
                        value={code}
                        onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                        placeholder="000000"
                        autoFocus
                    />
                    <VerifyButton type="submit" disabled={isLoading || code.length < 6}>
                        {isLoading ? 'מאמת...' : 'אמת חשבון'}
                    </VerifyButton>
                </form>

                <button
                    type="button"
                    onClick={onCancel}
                    style={{
                        marginTop: theme.spacing.md,
                        background: 'none',
                        border: 'none',
                        color: theme.colors.textMuted,
                        cursor: 'pointer'
                    }}
                >
                    חזור לדף הכניסה
                </button>
            </Card>
        </Container>
    );
}
