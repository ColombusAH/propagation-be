import { useState } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { slideInUp, fadeIn } from '@/styles/animations';

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
  text-align: center;
  width: 64px;
  height: 64px;
  margin: 0 auto ${theme.spacing.lg};
  background: ${theme.colors.primaryGradient};
  border-radius: ${theme.borderRadius.xl};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: white;
  animation: ${fadeIn} 0.8s ease-out;
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

const RoleGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
`;

const RoleCard = styled.button<{ $selected: boolean; $color: string }>`
  background: ${props => props.$selected ? props.$color : theme.colors.backgroundAlt};
  color: ${props => props.$selected ? 'white' : theme.colors.text};
  border: 2px solid ${props => props.$selected ? props.$color : theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.lg};
  cursor: pointer;
  transition: all ${theme.transitions.base};
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${theme.spacing.sm};
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: ${theme.shadows.lg};
    border-color: ${props => props.$color};
  }
  
  &:active {
    transform: translateY(-2px);
  }
`;

const RoleIcon = styled.div`
  font-size: ${theme.typography.fontSize['3xl']};
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

const LoginButton = styled.button<{ $disabled: boolean }>`
  width: 100%;
  padding: ${theme.spacing.lg};
  background: ${props => props.$disabled ? theme.colors.gray[300] : theme.colors.primaryGradient};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.xl};
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  cursor: ${props => props.$disabled ? 'not-allowed' : 'pointer'};
  transition: all ${theme.transitions.base};
  box-shadow: ${props => props.$disabled ? 'none' : theme.shadows.primaryMd};
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.primaryLg};
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const roles = [
  {
    id: 'CUSTOMER',
    name: 'לקוח',
    icon: 'C',
    description: 'קניות ועגלה',
    color: '#6B7280', // Gray
  },
  {
    id: 'CASHIER',
    name: 'קופאי',
    icon: 'K',
    description: 'סריקה ותשלום',
    color: '#059669', // Green
  },
  {
    id: 'MANAGER',
    name: 'מנהל',
    icon: 'M',
    description: 'דוחות וניהול',
    color: '#4F46E5', // Blue
  },
  {
    id: 'ADMIN',
    name: 'מנהל מערכת',
    icon: 'A',
    description: 'הרשאות מלאות',
    color: '#DC2626', // Red
  },
];

interface LoginPageProps {
  onLogin: (role: string) => void;
}

/**
 * LoginPage - Role selection and login
 * 
 * Allows users to select their role and login to the system
 */
export function LoginPage({ onLogin }: LoginPageProps) {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  const handleLogin = () => {
    if (selectedRole) {
      onLogin(selectedRole);
    }
  };

  return (
    <Container>
      <LoginCard>
        <Logo>R</Logo>
        <Title>מערכת RFID</Title>
        <Subtitle>בחר את התפקיד שלך להתחברות</Subtitle>

        <RoleGrid>
          {roles.map(role => (
            <RoleCard
              key={role.id}
              $selected={selectedRole === role.id}
              $color={role.color}
              onClick={() => setSelectedRole(role.id)}
            >
              <RoleIcon>{role.icon}</RoleIcon>
              <RoleName>{role.name}</RoleName>
              <RoleDescription>{role.description}</RoleDescription>
            </RoleCard>
          ))}
        </RoleGrid>

        <LoginButton
          $disabled={!selectedRole}
          disabled={!selectedRole}
          onClick={handleLogin}
        >
          {selectedRole ? `התחבר כ${roles.find(r => r.id === selectedRole)?.name}` : 'בחר תפקיד'}
        </LoginButton>
      </LoginCard>
    </Container>
  );
}
