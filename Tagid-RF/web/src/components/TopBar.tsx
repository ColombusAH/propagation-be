import { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { LanguageSwitch } from './LanguageSwitch';
import { useAuth, UserRole } from '@/contexts/AuthContext';
import { useTranslation } from '@/hooks/useTranslation';

const Header = styled.header`
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  padding: 0 1.5rem;
  height: 56px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid ${props => props.theme.colors.border};
  position: sticky;
  top: 0;
  z-index: ${props => props.theme.zIndex.header};
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
  gap: ${props => props.theme.spacing.md};
`;

const PageTitle = styled.h1`
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
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
  color: ${props => props.theme.colors.primary};
  padding: 0.375rem 0.625rem;
  background: rgba(31, 78, 121, 0.08);
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.primary};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: all ${props => props.theme.transitions.fast};

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
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.lg};
  min-width: 180px;
  padding: 4px;
  opacity: ${props => props.$open ? 1 : 0};
  visibility: ${props => props.$open ? 'visible' : 'hidden'};
  transform: ${props => props.$open ? 'translateY(0)' : 'translateY(-8px)'};
  transition: all ${props => props.theme.transitions.fast};
  z-index: ${props => props.theme.zIndex.dropdown};
`;

const RoleOption = styled.button<{ $active: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  color: ${props => props.$active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  background: ${props => props.$active ? 'rgba(31, 78, 121, 0.08)' : 'transparent'};
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  cursor: pointer;
  text-align: start;
  transition: all ${props => props.theme.transitions.fast};

  &:hover {
    background: ${props => props.theme.colors.surfaceHover};
    color: ${props => props.theme.colors.text};
  }

  .material-symbols-outlined {
    font-size: 18px;
  }
`;

const LogoutButton = styled.button`
  padding: 0.375rem 0.625rem;
  background: transparent;
  color: ${props => props.theme.colors.textSecondary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.8rem;
  cursor: pointer;
  transition: all ${props => props.theme.transitions.fast};
  display: flex;
  align-items: center;
  gap: 0.25rem;

  &:hover {
    background: ${props => props.theme.colors.surfaceHover};
    color: ${props => props.theme.colors.text};
    border-color: ${props => props.theme.colors.borderDark};
  }
`;

const MaterialIcon = ({ name, size = 18 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size }}>{name}</span>
);

export function TopBar() {
  const { userRole, logout, login } = useAuth();
  const { t } = useTranslation();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const roles: { id: UserRole; name: string; icon: string }[] = [
    { id: 'SUPER_ADMIN', name: t('roles.superAdmin'), icon: 'shield_person' },
    { id: 'NETWORK_ADMIN', name: t('roles.networkAdmin'), icon: 'hub' },
    { id: 'STORE_MANAGER', name: t('roles.storeManager'), icon: 'storefront' },
    { id: 'SELLER', name: t('roles.seller'), icon: 'badge' },
    { id: 'CUSTOMER', name: t('roles.customer'), icon: 'person' },
  ];

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
          <PageTitle>{t('app.title')}</PageTitle>
          <span style={{
            background: 'rgba(31, 78, 121, 0.08)',
            color: '#1f4e79',
            fontSize: '0.65rem',
            padding: '0.1rem 0.4rem',
            border: '1px solid rgba(31, 78, 121, 0.2)',
            borderRadius: '4px',
            marginLeft: '0.75rem',
            fontWeight: 600
          }}>v1.0.7</span>
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
            <MaterialIcon name="logout" size={14} /> {t('app.logout')}
          </LogoutButton>
        </RightSection>
      </NavContainer>
    </Header>
  );
}
