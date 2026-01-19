import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { useAuth } from '@/contexts/AuthContext';

const SidebarContainer = styled.aside`
  width: 200px;
  min-width: 200px;
  height: calc(100vh - 56px);
  background: ${theme.colors.surface};
  border-left: 1px solid ${theme.colors.border};
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
  border-right: 3px solid transparent;

  &:hover {
    background: ${theme.colors.surfaceHover};
    color: ${theme.colors.text};
  }

  &.active {
    background: ${theme.colors.info};
    color: white;
    border-right-color: ${theme.colors.infoDark};
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

  const isSuperAdmin = userRole === 'SUPER_ADMIN';
  const isNetworkAdmin = userRole === 'NETWORK_ADMIN';
  const isStoreManager = userRole === 'STORE_MANAGER';
  const isSeller = userRole === 'SELLER';

  const isAdmin = isSuperAdmin || isNetworkAdmin;
  const isStaff = isSuperAdmin || isNetworkAdmin || isStoreManager || isSeller;
  const canManageStore = isSuperAdmin || isNetworkAdmin || isStoreManager;

  return (
    <SidebarContainer>
      <Logo>
        <LogoIcon>
          <MaterialIcon name="sensors" />
        </LogoIcon>
        <LogoText>Tagid RF</LogoText>
      </Logo>

      <Section>
        <SectionTitle>ראשי</SectionTitle>
        {isStaff && (
          <NavItem to="/dashboard">
            <MaterialIcon name="space_dashboard" />
            סקירה כללית
          </NavItem>
        )}
        <NavItem to="/catalog">
          <MaterialIcon name="storefront" />
          קטלוג
        </NavItem>
      </Section>

      {(isSeller || !isStaff) && (
        <Section>
          <SectionTitle>קניות</SectionTitle>
          <NavItem to="/customer-cart">
            <MaterialIcon name="shopping_cart" />
            עגלה
          </NavItem>
          <NavItem to="/scan">
            <MaterialIcon name="qr_code_scanner" />
            סריקה
          </NavItem>
          <NavItem to="/orders">
            <MaterialIcon name="package_2" />
            הזמנות
          </NavItem>
        </Section>
      )}

      {canManageStore && (
        <Section>
          <SectionTitle>ניהול תגים</SectionTitle>
          <NavItem to="/tag-scanner">
            <MaterialIcon name="contactless" />
            סריקה
          </NavItem>
          <NavItem to="/tag-linking">
            <MaterialIcon name="link" />
            צימוד
          </NavItem>
        </Section>
      )}

      {canManageStore && (
        <Section>
          <SectionTitle>תפעול</SectionTitle>
          <NavItem to="/bath-setup">
            <MaterialIcon name="shopping_basket" />
            אמבטים
          </NavItem>
          <NavItem to="/exit-gate">
            <MaterialIcon name="door_sensor" />
            שער יציאה
          </NavItem>
          <NavItem to="/transactions">
            <MaterialIcon name="receipt_long" />
            עסקאות ותשלומים
          </NavItem>
        </Section>
      )}

      <Spacer />

      <Section>
        <SectionTitle>הגדרות</SectionTitle>
        <NavItem to="/reader-settings">
          <MaterialIcon name="router" />
          קוראים
        </NavItem>
        <NavItem to="/settings">
          <MaterialIcon name="tune" />
          כללי
        </NavItem>
        {isAdmin && (
          <NavItem to="/users">
            <MaterialIcon name="group" />
            משתמשים
          </NavItem>
        )}
      </Section>
    </SidebarContainer>
  );
}
