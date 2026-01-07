import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';
import { LanguageSwitch } from './LanguageSwitch';

const Header = styled.header`
  background: ${theme.colors.surface};
  color: ${theme.colors.text};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  box-shadow: ${theme.shadows.sm};
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
  gap: ${theme.spacing.lg};
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  
  @media (max-width: ${theme.breakpoints.tablet}) {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
`;

const NavItem = styled(NavLink)`
  color: ${theme.colors.textSecondary};
  text-decoration: none;
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  position: relative;
  transition: all ${theme.transitions.fast};
  white-space: nowrap;

  &:hover {
    color: ${theme.colors.primary};
    background: ${theme.colors.backgroundAlt};
  }

  &.active {
    color: ${theme.colors.primary};
    background: ${theme.colors.backgroundAlt};
    font-weight: ${theme.typography.fontWeight.semibold};
    
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: ${theme.spacing.md};
      right: ${theme.spacing.md};
      height: 2px;
      background: ${theme.colors.primary};
    }
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    padding: ${theme.spacing.sm};
    font-size: ${theme.typography.fontSize.xs};
  }
`;

const Badge = styled.span`
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: ${theme.colors.error};
  color: white;
  border-radius: ${theme.borderRadius.full};
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  padding: 0 4px;

  [dir="rtl"] & {
    right: auto;
    left: 4px;
  }
`;

export function TopBar() {
  const cartItemCount = useStore((state) => state.getCartItemCount());
  const { t } = useTranslation();

  return (
    <Header>
      <NavContainer>
        <Nav>
          <NavItem to="/dashboard">דשבורד</NavItem>
          <NavItem to="/scan">{t('nav.scan')}</NavItem>
          <NavItem to="/catalog">{t('nav.catalog')}</NavItem>
          <NavItem to="/cart">
            {t('nav.cart')}
            {cartItemCount > 0 && <Badge>{cartItemCount}</Badge>}
          </NavItem>
          <NavItem to="/orders">{t('nav.orders')}</NavItem>
          <NavItem to="/tag-mapping">תגיות</NavItem>
        </Nav>
        <LanguageSwitch />
      </NavContainer>
    </Header>
  );
}


