import { useState } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { slideInUp, fadeIn } from '@/styles/animations';
import { useToast } from '@/hooks/useToast';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${theme.colors.backgroundAlt};
  padding: ${theme.spacing.xl};
`;

const RegisterCard = styled.div`
  background: ${theme.colors.surface};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing['3xl']};
  box-shadow: ${theme.shadows.xl};
  max-width: 500px;
  width: 100%;
  animation: ${slideInUp} 0.5s ease-out;
  border: 1px solid ${theme.colors.border};
`;

const Logo = styled.div`
  width: 64px;
  height: 64px;
  margin: 0 auto ${theme.spacing.lg};
  background: ${theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: ${fadeIn} 0.8s ease-out;
  box-shadow: ${theme.shadows.primaryMd};
  
  .material-symbols-outlined {
    font-size: 32px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
  }
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  text-align: center;
  margin: 0 0 ${theme.spacing.sm} 0;
  color: ${theme.colors.text};
`;

const Subtitle = styled.p`
  text-align: center;
  color: ${theme.colors.textSecondary};
  margin: 0 0 ${theme.spacing.xl} 0;
  font-size: ${theme.typography.fontSize.base};
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const Label = styled.label`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const Input = styled.input`
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: ${theme.shadows.focus};
  }
`;

const RegisterButton = styled.button<{ $disabled?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background: ${props => props.$disabled ? theme.colors.gray[400] : theme.colors.primary};
  color: ${theme.colors.textInverse};
  border: 1px solid ${props => props.$disabled ? theme.colors.gray[400] : theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  transition: all ${theme.transitions.base};
  box-shadow: ${props => props.$disabled ? 'none' : theme.shadows.primarySm};
  
  &:hover:not(:disabled) {
    background: ${theme.colors.primaryDark};
    border-color: ${theme.colors.primaryDark};
    box-shadow: ${theme.shadows.primaryMd};
  }
`;

const LoginLink = styled.div`
  text-align: center;
  margin-top: ${theme.spacing.lg};
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  
  button {
    background: none;
    border: none;
    color: ${theme.colors.primary};
    font-weight: ${theme.typography.fontWeight.semibold};
    cursor: pointer;
    padding: 0 4px;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

interface RegisterPageProps {
    onBackToLogin: () => void;
    onRegisterSuccess: () => void;
}

export function RegisterPage({ onBackToLogin, onRegisterSuccess }: RegisterPageProps) {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        phone: '',
        address: '',
        businessId: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const toast = useToast();

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...formData, role: 'CUSTOMER' }),
            });

            if (response.ok) {
                toast.success('ההרשמה הצליחה! אנא התחבר.');
                onRegisterSuccess();
            } else {
                const err = await response.json();
                toast.error(err.detail || 'ההרשמה נכשלה');
            }
        } catch (err) {
            toast.error('שגיאת תקשורת');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container>
            <RegisterCard>
                <Logo><span className="material-symbols-outlined">person_add</span></Logo>
                <Title>הרשמה למערכת</Title>
                <Subtitle>צור חשבון חדש כדי להתחיל</Subtitle>

                <Form onSubmit={handleSubmit}>
                    <InputGroup>
                        <Label>שם מלא</Label>
                        <Input
                            name="name"
                            placeholder="ישראל ישראלי"
                            value={formData.name}
                            onChange={handleInputChange}
                            required
                        />
                    </InputGroup>

                    <InputGroup>
                        <Label>אימייל</Label>
                        <Input
                            name="email"
                            type="email"
                            placeholder="name@example.com"
                            value={formData.email}
                            onChange={handleInputChange}
                            required
                        />
                    </InputGroup>

                    <InputGroup>
                        <Label>סיסמה (מינימום 8 תווים)</Label>
                        <Input
                            name="password"
                            type="password"
                            placeholder="••••••••"
                            value={formData.password}
                            onChange={handleInputChange}
                            required
                            minLength={8}
                        />
                    </InputGroup>

                    <InputGroup>
                        <Label>טלפון</Label>
                        <Input
                            name="phone"
                            placeholder="+972-50-1234567"
                            value={formData.phone}
                            onChange={handleInputChange}
                            required
                        />
                    </InputGroup>

                    <InputGroup>
                        <Label>ח.פ / ת.ז</Label>
                        <Input
                            name="businessId"
                            placeholder="123456789"
                            value={formData.businessId}
                            onChange={handleInputChange}
                            required
                        />
                    </InputGroup>

                    <InputGroup>
                        <Label>כתובת</Label>
                        <Input
                            name="address"
                            placeholder="רחוב הרצל 1, תל אביב"
                            value={formData.address}
                            onChange={handleInputChange}
                            required
                        />
                    </InputGroup>

                    <RegisterButton type="submit" disabled={isLoading}>
                        {isLoading ? 'רשם...' : 'הירשם עכשיו'}
                    </RegisterButton>
                </Form>

                <LoginLink>
                    כבר יש לך חשבון? <button type="button" onClick={onBackToLogin}>התחבר כאן</button>
                </LoginLink>
            </RegisterCard>
        </Container>
    );
}
