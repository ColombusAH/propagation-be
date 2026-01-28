import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { useAuth } from '@/contexts/AuthContext';
import { useTranslation } from '@/hooks/useTranslation';

interface SidebarContainerProps {
  $isRTL: boolean;
}

const SidebarContainer = styled.aside<SidebarContainerProps>`
  width: 200px;
  min-width: 200px;
  height: calc(100vh - 56px);
  background: ${theme.colors.surface};
  border-left: ${props => props.$isRTL ? `1px solid ${theme.colors.border}` : 'none'};
  border-right: ${props => !props.$isRTL ? `1px solid ${theme.colors.border}` : 'none'};
  padding: ${theme.spacing.sm} 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 56px;
  overflow-y: auto;
  box-shadow: ${theme.shadows.sm};

  @media (max-width: ${theme.breakpoints.mobile}) {
    display: none;
  }
`;

const Section = styled.div`
  margin-bottom: ${theme.spacing.xs};
`;

const SectionTitle = styled.div`
  font-size: 10px;
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.textMuted};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: ${theme.spacing.sm} ${theme.spacing.md} ${theme.spacing.xs};
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  padding: 9px ${theme.spacing.md};
  color: ${theme.colors.textSecondary};
  text-decoration: none;
  font-size: 13px;
  font-weight: ${theme.typography.fontWeight.medium};
  transition: all ${theme.transitions.fast};
  border-inline-start: 3px solid transparent;

  &:hover {
    background: ${theme.colors.surfaceHover};
    color: ${theme.colors.text};
  }

  &.active {
    background: ${theme.colors.info};
    color: white;
    border-inline-start-color: ${theme.colors.infoDark};
    font-weight: ${theme.typography.fontWeight.semibold};
    
    .material-symbols-outlined {
      color: white;
    }
  }

  .material-symbols-outlined {
    font-size: 18px;
    width: 22px;
    text-align: center;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  padding: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xs};
  border-bottom: 1px solid ${theme.colors.border};
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.primaryDark} 100%);
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${theme.colors.textInverse};

  .material-symbols-outlined {
    font-size: 18px;
  }
`;

const LogoText = styled.div`
  font-size: 14px;
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
`;

const Spacer = styled.div`
  flex: 1;
`;

const MaterialIcon = ({ name }: { name: string }) => (
  <span className="material-symbols-outlined">{name}</span>
);

export function Sidebar() {
  const { userRole } = useAuth();
  const { t, isRTL } = useTranslation();

  const isSuperAdmin = userRole === 'SUPER_ADMIN';
  const isNetworkAdmin = userRole === 'NETWORK_ADMIN';
  const isStoreManager = userRole === 'STORE_MANAGER';
  const isSeller = userRole === 'SELLER';

  const isAdmin = isSuperAdmin || isNetworkAdmin;
  const isStaff = isSuperAdmin || isNetworkAdmin || isStoreManager || isSeller;
  const canManageStore = isSuperAdmin || isNetworkAdmin || isStoreManager;

  return (
    <SidebarContainer $isRTL={isRTL}>
      <Logo>
        <LogoIcon>
          <MaterialIcon name="sensors" />
        </LogoIcon>
        <LogoText>{t('app.name')}</LogoText>
      </Logo>

      <Section>
        <SectionTitle>{t('nav.main')}</SectionTitle>
        {isStaff && (
          <NavItem to="/dashboard">
            <MaterialIcon name="space_dashboard" />
            {t('nav.dashboard')}
          </NavItem>
        )}
        <NavItem to="/catalog">
          <MaterialIcon name="storefront" />
          {t('nav.catalog')}
        </NavItem>
      </Section>

      {(isSeller || !isStaff) && (
        <Section>
          <SectionTitle>{t('nav.shopping')}</SectionTitle>
          <NavItem to="/customer-cart">
            <MaterialIcon name="shopping_cart" />
            {t('nav.cart')}
          </NavItem>
          <NavItem to="/scan">
            <MaterialIcon name="qr_code_scanner" />
            {t('nav.scan')}
          </NavItem>
          <NavItem to="/orders">
            <MaterialIcon name="package_2" />
            {t('nav.orders')}
          </NavItem>
        </Section>
      )}

      {canManageStore && (
        <Section>
          <SectionTitle>{t('nav.tagManagement')}</SectionTitle>
          <NavItem to="/tag-mapping">
            <MaterialIcon name="inventory_2" />
            {t('nav.tagMapping')}
          </NavItem>
          <NavItem to="/tag-scanner">
            <MaterialIcon name="contactless" />
            {t('nav.tagScanner')}
          </NavItem>

        </Section>
      )}

      {canManageStore && (
        <Section>
          <SectionTitle>{t('nav.operations')}</SectionTitle>
          <NavItem to="/bath-setup">
            <MaterialIcon name="shopping_basket" />
            {t('nav.bathSetup')}
          </NavItem>
          <NavItem to="/exit-gate">
            <MaterialIcon name="door_sensor" />
            {t('nav.exitGate')}
          </NavItem>
          <NavItem to="/transactions">
            <MaterialIcon name="receipt_long" />
            {t('nav.transactions')}
          </NavItem>
        </Section>
      )}

      <Spacer />

      <Section>
        <SectionTitle>{t('nav.settings')}</SectionTitle>
        {canManageStore && (
          <NavItem to="/reader-settings">
            <MaterialIcon name="router" />
            {t('nav.readers')}
          </NavItem>
        )}
        <NavItem to="/settings">
          <MaterialIcon name="tune" />
          {t('nav.general')}
        </NavItem>
        <NavItem to="/notification-settings">
          <MaterialIcon name="notifications_active" />
          {t('nav.notifications')}
        </NavItem>
        {isAdmin && (
          <NavItem to="/users">
            <MaterialIcon name="group" />
            {t('nav.users')}
          </NavItem>
        )}
      </Section>
    </SidebarContainer>
  );
}
