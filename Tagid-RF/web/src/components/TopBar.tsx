import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import { useTranslation } from '@/hooks/useTranslation';
import { LanguageSwitch } from './LanguageSwitch';

const Header = styled.header`
  background-color: ${theme.colors.primary};
  color: white;
  padding: ${theme.spacing.md};
  box-shadow: ${theme.shadows.md};
  position: sticky;
  top: 0;
  z-index: ${theme.zIndex.header};
`;

const NavContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  gap: ${theme.spacing.sm};
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const NavItem = styled(NavLink)`
  color: white;
  text-decoration: none;
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  position: relative;
  transition: background-color ${theme.transitions.fast};

  &:hover {
    background-color: ${theme.colors.primaryDark};
  }

  &.active {
    background-color: ${theme.colors.primaryDark};
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    padding: ${theme.spacing.sm};
    font-size: ${theme.typography.fontSize.xs};
  }
`;

const Badge = styled.span`
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: ${theme.colors.danger};
  color: white;
  border-radius: ${theme.borderRadius.full};
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: ${theme.typography.fontWeight.bold};
  padding: 0 4px;

  [dir="rtl"] & {
    right: auto;
    left: -4px;
  }
`;

export function TopBar() {
  const cartItemCount = useStore((state) => state.getCartItemCount());
  const { t } = useTranslation();

  return (
    <Header>
      <NavContainer>
        <Nav>
          <NavItem to="/scan">📷 {t('nav.scan')}</NavItem>
          <NavItem to="/catalog">📦 {t('nav.catalog')}</NavItem>
          <NavItem to="/cart">
            🛒 {t('nav.cart')}
            {cartItemCount > 0 && <Badge>{cartItemCount}</Badge>}
          </NavItem>
          <NavItem to="/orders">📋 {t('nav.orders')}</NavItem>
          <NavItem to="/qr-generator">🏷️ {t('nav.qrGenerator')}</NavItem>
          <NavItem to="/containers">🛁 {t('nav.containers')}</NavItem>
          <NavItem to="/tag-mapping">🔐 {t('nav.tagMapping')}</NavItem>
        </Nav>
        <LanguageSwitch />
      </NavContainer>
    </Header>
  );
}


