import { useState } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { slideInUp, fadeIn } from '@/styles/animations';
import { useToast } from '@/hooks/useToast';
import { API_BASE_URL } from '@/api/config';

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
  onRegisterSuccess: (email: string) => void;
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

  const validateForm = () => {
    if (!formData.name.trim()) {
      toast.error('נא להזין שם מלא');
      return false;
    }

    // Basic email regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error('נא להזין כתובת אימייל תקינה');
      return false;
    }

    if (formData.password.length < 8) {
      toast.error('הסיסמה חייבת להכיל לפחות 8 תווים');
      return false;
    }

    // Phone validation: allows digits, spaces, dashes, plus sign. Min 9 chars.
    const phoneRegex = /^[\d\+\-\s]{9,20}$/;
    if (!phoneRegex.test(formData.phone)) {
      toast.error('נא להזין מספר טלפון תקין (מינימום 9 ספרות)');
      return false;
    }

    if (!formData.address.trim()) {
      toast.error('נא להזין כתובת');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Prepare payload - convert empty strings to null/undefined where appropriate
      const payload: any = {
        ...formData,
        role: 'CUSTOMER',
      };

      if (!formData.businessId) {
        delete payload.businessId;
      }

      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        toast.success('הרשמה מוצלחת! נא לאמת את המייל.');
        onRegisterSuccess(formData.email);
      } else {
        const err = await response.json();
        console.error('Registration failed:', err);

        const errorMessage = typeof err.detail === 'string' ? err.detail : 'ההרשמה נכשלה - בדוק את הנתונים';

        if (errorMessage.includes("Email already registered")) {
          toast.error('האימייל הזה כבר רשום במערכת');
        } else {
          toast.error(errorMessage);
        }
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
        <Title>הרשמה למערכת - Tagid</Title>
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
            <small style={{
              color: formData.password.length > 0 && formData.password.length < 8 ? '#ff4d4f' : '#666',
              marginTop: '4px',
              display: 'block',
              fontWeight: formData.password.length > 0 && formData.password.length < 8 ? 'bold' : 'normal'
            }}>
              הסיסמה חייבת להכיל לפחות 8 תווים
            </small>
          </InputGroup>

          <InputGroup>
            <Label>טלפון</Label>
            <Input
              name="phone"
              dir="ltr"
              style={{ textAlign: 'right' }}
              placeholder="+972-50-1234567"
              value={formData.phone}
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
            {isLoading ? 'מבצע הרשמה...' : 'הירשם עכשיו'}
          </RegisterButton>
        </Form>

        <LoginLink>
          כבר יש לך חשבון? <button type="button" onClick={onBackToLogin}>התחבר כאן</button>
        </LoginLink>
      </RegisterCard>
    </Container>
  );
}
