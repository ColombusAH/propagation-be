import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 900px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: calc(100vh - 64px);
  animation: ${theme.animations.fadeIn};
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.lg};
  border-right: 10px solid #1E3A8A;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: ${theme.spacing.lg};
  color: white;
  animation: ${theme.animations.slideUp};
  position: relative;
  overflow: hidden;

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${theme.spacing.md};
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 86c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm66-3c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm-46-45c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zm20-17c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
    opacity: 0.2;
  }

  h1, p {
    color: white;
    position: relative;
    z-index: 1;
  }
`;

const HeaderContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const SettingsButton = styled(Link)`
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 12px 24px;
  border-radius: ${theme.borderRadius.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  text-decoration: none;
  transition: all ${theme.transitions.base};
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  z-index: 2;
  font-size: ${theme.typography.fontSize.base};
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    border-color: rgba(255, 255, 255, 0.5);
  }

  &:active {
    transform: translateY(-1px) scale(1);
  }

  .material-symbols-outlined {
    font-size: 24px;
    font-variation-settings: 'FILL' 1, 'wght' 600, 'GRAD' 0, 'opsz' 24;
  }
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  margin: 0;
  line-height: 1.2;
`;

const Subtitle = styled.p`
  margin: 0;
`;

const NotificationsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const NotificationCard = styled.div<{ $type: 'info' | 'warning' | 'success' | 'error' }>`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-right: 6px solid ${props => {
    switch (props.$type) {
      case 'success': return theme.colors.success;
      case 'warning': return theme.colors.warning;
      case 'error': return theme.colors.error;
      default: return theme.colors.primary;
    }
  }};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.sm};
  animation: ${theme.animations.slideUp};

  &:hover {
    transform: translateX(-8px);
    box-shadow: ${theme.shadows.md};
    background: ${theme.colors.surfaceHover};
  }
`;

const NotificationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: ${theme.spacing.sm};
`;

const NotificationTitle = styled.h3`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0;
`;

const NotificationTime = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const NotificationMessage = styled.p`
  color: ${theme.colors.textSecondary};
  margin: 0;
  line-height: 1.6;
`;

const Badge = styled.span<{ $type: 'info' | 'warning' | 'success' | 'error' }>`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  background: ${props => {
    switch (props.$type) {
      case 'success': return theme.colors.successLight;
      case 'warning': return theme.colors.warningLight;
      case 'error': return theme.colors.errorLight;
      default: return theme.colors.infoLight;
    }
  }};
  color: ${props => {
    switch (props.$type) {
      case 'success': return theme.colors.successDark;
      case 'warning': return theme.colors.warningDark;
      case 'error': return theme.colors.errorDark;
      default: return theme.colors.infoDark;
    }
  }};
  border: 1px solid currentColor;
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.bold};
  margin-top: ${theme.spacing.sm};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['4xl']} ${theme.spacing.xl};
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.xl};
  color: ${theme.colors.textSecondary};
  box-shadow: ${theme.shadows.sm};
  animation: ${theme.animations.fadeIn};
`;

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  time: string;
  badge?: string;
}

const notifications: Notification[] = [];

/**
 * NotificationsPage - In-app notifications for staff
 * Shows system alerts, sales updates, inventory warnings, etc.
 */
export function NotificationsPage() {
  const { userRole } = useAuth();

  const isStaff = userRole && ['SUPER_ADMIN', 'NETWORK_ADMIN', 'STORE_MANAGER', 'SELLER'].includes(userRole);

  if (!isStaff) {
    return (
      <Layout>
        <Container>
          <EmptyState>
            <h2>אין גישה</h2>
            <p>עמוד זה זמין רק לצוות</p>
          </EmptyState>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container>
        <Header>
          <HeaderContent>
            <Title>התראות</Title>
            <Subtitle>עדכונים מהמערכת</Subtitle>
          </HeaderContent>
          <SettingsButton to="/notification-settings">
            <span className="material-symbols-outlined">tune</span>
            הגדרות התראות
          </SettingsButton>
        </Header>

        {notifications.length === 0 ? (
          <EmptyState>
            <p style={{ fontSize: theme.typography.fontSize.lg }}>אין התראות חדשות</p>
            <p>כל העדכונים יופיעו כאן</p>
          </EmptyState>
        ) : (
          <NotificationsList>
            {notifications.map((notification) => (
              <NotificationCard key={notification.id} $type={notification.type}>
                <NotificationHeader>
                  <NotificationTitle>{notification.title}</NotificationTitle>
                  <NotificationTime>{notification.time}</NotificationTime>
                </NotificationHeader>
                <NotificationMessage>{notification.message}</NotificationMessage>
                {notification.badge && (
                  <Badge $type={notification.type}>{notification.badge}</Badge>
                )}
              </NotificationCard>
            ))}
          </NotificationsList>
        )}
      </Container>
    </Layout>
  );
}
