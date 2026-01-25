import { useState } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { slideInUp, fadeIn } from '@/styles/animations';
import { UserRole } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/useToast';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${theme.colors.backgroundAlt};
  padding: ${theme.spacing.xl};
`;

const LoginCard = styled.div`
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

const TabContainer = styled.div`
  display: flex;
  margin-bottom: ${theme.spacing.lg};
  border-bottom: 2px solid ${theme.colors.border};
`;

const TabButton = styled.button<{ $active: boolean }>`
  flex: 1;
  padding: ${theme.spacing.md};
  background: none;
  border: none;
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${props => props.$active ? theme.typography.fontWeight.bold : theme.typography.fontWeight.normal};
  color: ${props => props.$active ? theme.colors.primary : theme.colors.textMuted};
  border-bottom: 2px solid ${props => props.$active ? theme.colors.primary : 'transparent'};
  margin-bottom: -2px;
  cursor: pointer;
  transition: all 0.2s;
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

const ErrorMessage = styled.div`
  color: ${theme.colors.error};
  font-size: ${theme.typography.fontSize.sm};
  text-align: center;
  margin-top: ${theme.spacing.sm};
`;

const RoleGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
  
  & > *:last-child:nth-child(odd) {
    grid-column: 1 / -1;
  }
`;

const RoleCard = styled.button<{ $selected: boolean }>`
  background: ${props => props.$selected ? theme.colors.surfaceElevated : theme.colors.surface};
  color: ${theme.colors.text};
  border: 1px solid ${props => props.$selected ? theme.colors.borderDark : theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  cursor: pointer;
  transition: all ${theme.transitions.base};
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.xs};
  box-shadow: ${props => props.$selected ? theme.shadows.md : theme.shadows.sm};
  
  &:hover {
    background: ${theme.colors.surfaceElevated};
    border-color: ${theme.colors.borderDark};
    box-shadow: ${theme.shadows.md};
  }
  
  &:active {
    box-shadow: ${theme.shadows.sm};
  }
`;

const RoleIcon = styled.span`
  font-size: 28px;
  line-height: 1;
  color: ${theme.colors.primary};
`;

const RoleName = styled.div`
  font-weight: ${theme.typography.fontWeight.semibold};
  font-size: ${theme.typography.fontSize.lg};
`;

const RoleDescription = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  opacity: 0.9;
  text-align: center;
`;

const LoginButton = styled.button<{ $disabled?: boolean }>`
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
  
  &:active:not(:disabled) {
    box-shadow: ${theme.shadows.sm};
  }
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: ${theme.spacing.lg} 0;
  
  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${theme.colors.border};
  }
  
  span {
    padding: 0 ${theme.spacing.md};
    color: ${theme.colors.textMuted};
    font-size: ${theme.typography.fontSize.sm};
  }
`;

const GoogleButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: ${theme.spacing.md};
  background: white;
  color: #3c4043;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all ${theme.transitions.base};
  
  &:hover {
    background: #f8f9fa;
    border-color: #dadce0;
    box-shadow: ${theme.shadows.sm};
  }
  
  img {
    width: 20px;
    height: 20px;
  }
`;

const RegisterLink = styled.div`
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

const roles: { id: UserRole; name: string; icon: string; description: string }[] = [
  {
    id: 'SUPER_ADMIN',
    name: 'מנהל על',
    icon: 'admin_panel_settings',
    description: 'הרשאות מלאות + רשתות',
  },
  {
    id: 'NETWORK_ADMIN',
    name: 'מנהל רשת',
    icon: 'hub',
    description: 'ניהול רשת חנויות',
  },
  {
    id: 'STORE_MANAGER',
    name: 'מנהל חנות',
    icon: 'store',
    description: 'ניהול חנות בודדת',
  },
  {
    id: 'SELLER',
    name: 'מוכר',
    icon: 'point_of_sale',
    description: 'סריקה ותשלום',
  },
  {
    id: 'CUSTOMER',
    name: 'לקוח',
    icon: 'person',
    description: 'קניות באפליקציה',
  },
];

interface LoginPageProps {
  onLogin: (role: UserRole, token?: string) => void;
  onToggleRegister: () => void;
}

/**
 * LoginPage - Role selection and login
 * 
 * Allows users to select their role and login to the system
 */
export function LoginPage({ onLogin, onToggleRegister }: LoginPageProps) {
  const [activeTab, setActiveTab] = useState<'standard' | 'dev'>('standard');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // const { t } = useTranslation(); // Use when translations allow
  const toast = useToast();

  const handleStandardLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const role = data.role as UserRole; // Ensure BE returns correct role string
        onLogin(role, data.token);
        toast.success(`ברוך הבא! הותחברת כ - ${role} `);
      } else {
        const err = await response.json();
        setError(err.detail || 'התחברות נכשלה');
      }
    } catch (err) {
      setError('שגיאת תקשורת');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDevLogin = async () => {
    if (selectedRole) {
      setIsLoading(true);
      try {
        const response = await fetch('/api/v1/auth/dev-login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ role: selectedRole }),
        });

        if (response.ok) {
          const data = await response.json();
          onLogin(selectedRole, data.token);
        } else {
          console.error('API login failed');
          // Fallback to demo login if API fails (useful for UI only testing)
          onLogin(selectedRole);
        }
      } catch (error) {
        console.error('Connection error during login:', error);
        onLogin(selectedRole);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <Container>
      <LoginCard>
        <Logo><span className="material-symbols-outlined">nfc</span></Logo>
        <Title>מערכת RFID</Title>
        <Subtitle>התחברות למערכת הניהול</Subtitle>

        <TabContainer>
          <TabButton
            $active={activeTab === 'standard'}
            onClick={() => setActiveTab('standard')}
          >
            התחברות רגילה
          </TabButton>
          <TabButton
            $active={activeTab === 'dev'}
            onClick={() => setActiveTab('dev')}
          >
            מצב פיתוח
          </TabButton>
        </TabContainer>

        {activeTab === 'standard' ? (
          <Form onSubmit={handleStandardLogin}>
            <InputGroup>
              <Label>אימייל</Label>
              <Input
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </InputGroup>

            <InputGroup>
              <Label>סיסמה</Label>
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </InputGroup>

            {error && <ErrorMessage>{error}</ErrorMessage>}

            <LoginButton type="submit" disabled={isLoading}>
              {isLoading ? 'מתחבר...' : 'התחבר'}
            </LoginButton>

            <Divider>
              <span>או</span>
            </Divider>

            <GoogleButton type="button" onClick={() => toast.info('התחברות עם גוגל בפיתוח...')}>
              <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" />
              התחבר עם Google
            </GoogleButton>

            <RegisterLink>
              אין לך חשבון? <button type="button" onClick={onToggleRegister}>הירשם כאן</button>
            </RegisterLink>
          </Form>
        ) : (
          <>
            <RoleGrid>
              {roles.map(role => (
                <RoleCard
                  key={role.id}
                  $selected={selectedRole === role.id}
                  onClick={() => setSelectedRole(role.id)}
                >
                  <RoleIcon className="material-symbols-outlined">{role.icon}</RoleIcon>
                  <RoleName>{role.name}</RoleName>
                  <RoleDescription>{role.description}</RoleDescription>
                </RoleCard>
              ))}
            </RoleGrid>

            <LoginButton
              $disabled={!selectedRole || isLoading}
              disabled={!selectedRole || isLoading}
              onClick={handleDevLogin}
            >
              {isLoading ? 'טוען...' : (selectedRole ? `התחבר כ${roles.find(r => r.id === selectedRole)?.name} ` : 'בחר תפקיד')}
            </LoginButton>
          </>
        )}
      </LoginCard>
    </Container>
  );
}
