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
  padding: ${theme.spacing.lg} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.lg};
  border-right: 10px solid #1E3A8A;
  color: white;
  animation: ${theme.animations.slideUp};

  h1, p {
    color: white;
  }
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Subtitle = styled.p`
  color: ${theme.colors.textSecondary};
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
          <Title>התראות</Title>
          <Subtitle>עדכונים מהמערכת</Subtitle>
        </Header>

        {notifications.length === 0 ? (
          <EmptyState>
            <p style={{ fontSize: theme.typography.fontSize.lg }}>אין התראות חדשות</p>
            <p>כל העדכונים והאלרטים יופיעו כאן</p>
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
