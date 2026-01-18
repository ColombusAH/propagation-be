import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '@/styles/theme';
import { useAuth } from '@/contexts/AuthContext';

const SidebarContainer = styled.aside`
  width: 220px;
  min-width: 220px;
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
  margin-bottom: ${theme.spacing.md};
`;

const SectionTitle = styled.div`
  font-size: 11px;
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.textMuted};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  margin-bottom: 2px;
`;

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  padding: 10px ${theme.spacing.md};
  color: ${theme.colors.textSecondary};
  text-decoration: none;
  font-size: ${theme.typography.fontSize.sm};
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
    font-size: 20px;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  padding: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.sm};
  border-bottom: 1px solid ${theme.colors.border};
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: ${theme.colors.primary};
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
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
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
        <LogoText>מערכת RFID</LogoText>
      </Logo>

      <Section>
        <SectionTitle>ראשי</SectionTitle>
        {isStaff && (
          <NavItem to="/dashboard">
            <MaterialIcon name="dashboard" />
            לוח בקרה
          </NavItem>
        )}
        <NavItem to="/catalog">
          <MaterialIcon name="inventory_2" />
          קטלוג
        </NavItem>
        {(isSeller || isStoreManager || !isAdmin) && (
          <NavItem to="/scan">
            <MaterialIcon name="qr_code_scanner" />
            סריקה
          </NavItem>
        )}
        {!isAdmin && (
          <NavItem to="/cart">
            <MaterialIcon name="shopping_cart" />
            עגלה
          </NavItem>
        )}
        {!isAdmin && (
          <NavItem to="/orders">
            <MaterialIcon name="receipt_long" />
            הזמנות
          </NavItem>
        )}
      </Section>

      {canManageStore && (
        <Section>
          <SectionTitle>חיישנים</SectionTitle>
          <NavItem to="/tag-mapping">
            <MaterialIcon name="sell" />
            סנכרון תגים
          </NavItem>
          <NavItem to="/reader-settings">
            <MaterialIcon name="sensors" />
            הגדרות קורא
          </NavItem>
        </Section>
      )}

      {canManageStore && (
        <Section>
          <SectionTitle>ניהול</SectionTitle>
          {isStoreManager && (
            <NavItem to="/store-bi">
              <MaterialIcon name="analytics" />
              דוחות וניתוחים
            </NavItem>
          )}
          <NavItem to="/transactions">
            <MaterialIcon name="receipt_long" />
            עסקאות
          </NavItem>
          <NavItem to="/payments">
            <MaterialIcon name="payments" />
            תשלומים
          </NavItem>
          {isStaff && (
            <NavItem to="/notifications">
              <MaterialIcon name="notifications" />
              התראות
            </NavItem>
          )}
          {isAdmin && (
            <NavItem to="/users">
              <MaterialIcon name="group" />
              משתמשים
            </NavItem>
          )}
          {isAdmin && (
            <NavItem to="/stores">
              <MaterialIcon name="store" />
              סניפים
            </NavItem>
          )}
        </Section>
      )}

      <Section>
        <SectionTitle>הגדרות</SectionTitle>
        <NavItem to="/settings">
          <MaterialIcon name="tune" />
          הגדרות כלליות
        </NavItem>
      </Section>
    </SidebarContainer>
  );
}
