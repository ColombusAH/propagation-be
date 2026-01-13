import { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';
import { LanguageSwitch } from './LanguageSwitch';
import { useAuth } from '@/contexts/AuthContext';

const Header = styled.header`
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  padding: 0.75rem 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  border-bottom: 1px solid ${theme.colors.border};
  position: sticky;
  top: 0;
  z-index: ${theme.zIndex.header};
`;

const NavContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  gap: 1rem;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const NavItem = styled(NavLink)`
  color: ${theme.colors.textSecondary};
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.4rem;

  &:hover {
    color: ${theme.colors.primary};
    background: ${theme.colors.backgroundAlt};
  }

  &.active {
    color: ${theme.colors.primary};
    background: ${theme.colors.backgroundAlt};
    font-weight: 600;
  }
`;

const DropdownContainer = styled.div`
  position: relative;
`;

const DropdownTrigger = styled.button<{ $active?: boolean }>`
  color: ${props => props.$active ? theme.colors.primary : theme.colors.textSecondary};
  background: ${props => props.$active ? theme.colors.backgroundAlt : 'transparent'};
  border: none;
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.4rem;

  &:hover {
    color: ${theme.colors.primary};
    background: ${theme.colors.backgroundAlt};
  }
`;

const DropdownMenu = styled.div<{ $open: boolean }>`
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  min-width: 180px;
  padding: 0.5rem;
  opacity: ${props => props.$open ? 1 : 0};
  visibility: ${props => props.$open ? 'visible' : 'hidden'};
  transform: ${props => props.$open ? 'translateY(0)' : 'translateY(-10px)'};
  transition: all 0.2s ease;
  z-index: 100;
`;

const DropdownItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  color: ${theme.colors.text};
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.15s;

  &:hover {
    background: ${theme.colors.backgroundAlt};
    color: ${theme.colors.primary};
  }

  &.active {
    background: ${theme.colors.primary}15;
    color: ${theme.colors.primary};
    font-weight: 500;
  }
`;

const Divider = styled.div`
  height: 1px;
  background: ${theme.colors.border};
  margin: 0.5rem 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
`;

const LogoutButton = styled.button`
  padding: 0.5rem 0.75rem;
  background: transparent;
  color: ${theme.colors.textSecondary};
  border: 1px solid ${theme.colors.border};
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${theme.colors.backgroundAlt};
    color: ${theme.colors.text};
  }
`;

// Dropdown component
function Dropdown({
  label,
  icon,
  items,
  activePaths
}: {
  label: string;
  icon: string;
  items: { path: string; label: string; icon: string }[];
  activePaths: string[];
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const isActive = activePaths.some(path => window.location.pathname.startsWith(path));

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <DropdownContainer ref={ref}>
      <DropdownTrigger
        $active={isActive}
        onClick={() => setOpen(!open)}
      >
        {icon} {label} ▾
      </DropdownTrigger>
      <DropdownMenu $open={open}>
        {items.map((item, index) => (
          <DropdownItem
            key={item.path}
            to={item.path}
            onClick={() => setOpen(false)}
          >
            {item.icon} {item.label}
          </DropdownItem>
        ))}
      </DropdownMenu>
    </DropdownContainer>
  );
}

export function TopBar() {
  const { t } = useTranslation();
  const { userRole, logout } = useAuth();

  const isAdmin = userRole === 'ADMIN';
  const isManager = userRole === 'MANAGER';
  const isCashier = userRole === 'CASHIER';
  const isStaff = ['CASHIER', 'MANAGER', 'ADMIN'].includes(userRole || '');

  // RFID dropdown items
  const rfidItems = [
    { path: '/tag-mapping', label: 'סנכרון תגים', icon: '🏷️' },
    { path: '/reader-settings', label: 'הגדרות קורא', icon: '📡' },
  ];

  // Management dropdown items (role-based)
  const managementItems = [
    ...(isStaff ? [{ path: '/dashboard', label: 'דשבורד מכירות', icon: '📊' }] : []),
    ...(isStaff ? [{ path: '/transactions', label: 'עסקאות', icon: '💰' }] : []),
    ...((isAdmin || isManager) ? [{ path: '/payments', label: 'תשלומים', icon: '🏦' }] : []),
    ...(isStaff ? [{ path: '/notifications', label: 'התראות', icon: '🔔' }] : []),
    ...((isAdmin || isManager) ? [{ path: '/users', label: 'משתמשים', icon: '👥' }] : []),
    ...(isAdmin ? [{ path: '/stores', label: 'חנויות', icon: '🏪' }] : []),
  ];

  return (
    <Header>
      <NavContainer>
        <Nav>
          {/* Scan */}
          <NavItem to="/scan">
            📷 {t('nav.scan')}
          </NavItem>

          {/* Catalog */}
          <NavItem to="/catalog">
            🛒 {t('nav.catalog')}
          </NavItem>

          {/* RFID Dropdown - staff only */}
          {isStaff && (
            <Dropdown
              label="RFID"
              icon="📡"
              items={rfidItems}
              activePaths={['/tag-mapping', '/reader-settings']}
            />
          )}

          {/* Management Dropdown - staff only */}
          {isStaff && managementItems.length > 0 && (
            <Dropdown
              label="ניהול"
              icon="⚙️"
              items={managementItems}
              activePaths={['/transactions', '/notifications', '/users', '/stores']}
            />
          )}

          {/* Settings */}
          <NavItem to="/settings">
            ⚙️ {t('settings.title')}
          </NavItem>
        </Nav>

        <RightSection>
          <LanguageSwitch />
          <LogoutButton onClick={logout}>
            🚪 התנתק
          </LogoutButton>
        </RightSection>
      </NavContainer>
    </Header>
  );
}
