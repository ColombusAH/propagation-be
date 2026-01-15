import { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { LanguageSwitch } from './LanguageSwitch';
import { useAuth, UserRole } from '@/contexts/AuthContext';

const Header = styled.header`
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  padding: 0 1.5rem;
  height: 56px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid ${theme.colors.border};
  position: sticky;
  top: 0;
  z-index: ${theme.zIndex.header};
`;

const NavContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const PageTitle = styled.h1`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const RoleSwitcher = styled.div`
  position: relative;
`;

const RoleBadge = styled.button`
  font-size: 0.75rem;
  color: ${theme.colors.primary};
  padding: 0.375rem 0.625rem;
  background: rgba(31, 78, 121, 0.08);
  border-radius: ${theme.borderRadius.md};
  border: 1px solid ${theme.colors.primary};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: rgba(31, 78, 121, 0.15);
  }

  .material-symbols-outlined {
    font-size: 14px;
  }
`;

const RoleDropdown = styled.div<{ $open: boolean }>`
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.lg};
  min-width: 180px;
  padding: 4px;
  opacity: ${props => props.$open ? 1 : 0};
  visibility: ${props => props.$open ? 'visible' : 'hidden'};
  transform: ${props => props.$open ? 'translateY(0)' : 'translateY(-8px)'};
  transition: all ${theme.transitions.fast};
  z-index: ${theme.zIndex.dropdown};
`;

const RoleOption = styled.button<{ $active: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  color: ${props => props.$active ? theme.colors.primary : theme.colors.textSecondary};
  background: ${props => props.$active ? 'rgba(31, 78, 121, 0.08)' : 'transparent'};
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-size: 0.875rem;
  cursor: pointer;
  text-align: right;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.surfaceHover};
    color: ${theme.colors.text};
  }

  .material-symbols-outlined {
    font-size: 18px;
  }
`;

const LogoutButton = styled.button`
  padding: 0.375rem 0.625rem;
  background: transparent;
  color: ${theme.colors.textSecondary};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: 0.8rem;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  gap: 0.25rem;

  &:hover {
    background: ${theme.colors.surfaceHover};
    color: ${theme.colors.text};
    border-color: ${theme.colors.borderDark};
  }
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

const roles: { id: UserRole; name: string; icon: string }[] = [
  { id: 'SUPER_ADMIN', name: 'מנהל על', icon: 'shield_person' },
  { id: 'NETWORK_ADMIN', name: 'מנהל רשת', icon: 'hub' },
  { id: 'STORE_MANAGER', name: 'מנהל חנות', icon: 'storefront' },
  { id: 'SELLER', name: 'מוכר', icon: 'badge' },
  { id: 'CUSTOMER', name: 'לקוח', icon: 'person' },
];

export function TopBar() {
  const { userRole, logout, login } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentRole = roles.find(r => r.id === userRole);

  const handleRoleChange = (role: UserRole) => {
    login(role);
    setDropdownOpen(false);
  };

  return (
    <Header>
      <NavContainer>
        <LeftSection>
          <PageTitle>מערכת ניהול RFID</PageTitle>
        </LeftSection>

        <RightSection>
          <RoleSwitcher ref={dropdownRef}>
            <RoleBadge onClick={() => setDropdownOpen(!dropdownOpen)}>
              <MaterialIcon name={currentRole?.icon || 'person'} size={14} />
              {currentRole?.name}
              <MaterialIcon name="expand_more" size={14} />
            </RoleBadge>
            <RoleDropdown $open={dropdownOpen}>
              {roles.map((role) => (
                <RoleOption
                  key={role.id}
                  $active={userRole === role.id}
                  onClick={() => handleRoleChange(role.id)}
                >
                  <MaterialIcon name={role.icon} />
                  {role.name}
                </RoleOption>
              ))}
            </RoleDropdown>
          </RoleSwitcher>
          <LanguageSwitch />
          <LogoutButton onClick={logout}>
            <MaterialIcon name="logout" size={14} /> יציאה
          </LogoutButton>
        </RightSection>
      </NavContainer>
    </Header>
  );
}
