import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useTranslation } from '@/hooks/useTranslation';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 900px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
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
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-left: 4px solid ${props => {
    switch (props.$type) {
      case 'success': return theme.colors.success;
      case 'warning': return '#F59E0B';
      case 'error': return theme.colors.error;
      default: return theme.colors.primary;
    }
  }};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  transition: all ${theme.transitions.fast};

  &:hover {
    box-shadow: ${theme.shadows.md};
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
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  background: ${props => {
    switch (props.$type) {
      case 'success': return theme.colors.success;
      case 'warning': return '#F59E0B';
      case 'error': return theme.colors.error;
      default: return theme.colors.primary;
    }
  }};
  color: white;
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
  margin-top: ${theme.spacing.sm};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${theme.spacing['2xl']};
  color: ${theme.colors.textSecondary};
`;

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  time: string;
  badge?: string;
}

// Mock notifications data
const mockNotifications: Notification[] = [
  {
    id: '0',
    type: 'error',
    title: '⚠️ מוצר לא שולם ביציאה',
    message: 'תג RFID: E200-4150-8501-2340 | מוצר: חולצה כחולה XL | מחיר: ₪189 | שער יציאה: כניסה ראשית',
    time: 'עכשיו',
    badge: 'אבטחה',
  },
  {
    id: '1',
    type: 'success',
    title: 'מכירה חדשה הושלמה',
    message: 'עסקה בסך ₪450 בוצעה בהצלחה. לקוח: יוסי כהן',
    time: 'לפני 5 דקות',
    badge: 'מכירה',
  },
  {
    id: '2',
    type: 'warning',
    title: 'מלאי נמוך',
    message: 'המוצר "חלב 3%" מגיע לסף המינימום. נותרו 5 יחידות בלבד',
    time: 'לפני 15 דקות',
    badge: 'מלאי',
  },
  {
    id: '3',
    type: 'info',
    title: 'עדכון מערכת',
    message: 'גרסה חדשה של המערכת זמינה. מומלץ לעדכן בסוף יום העבודה',
    time: 'לפני שעה',
    badge: 'מערכת',
  },
  {
    id: '4',
    type: 'success',
    title: 'יעד יומי הושג',
    message: 'מזל טוב! הגעת ליעד המכירות היומי של ₪10,000',
    time: 'לפני 2 שעות',
    badge: 'הישג',
  },
  {
    id: '5',
    type: 'error',
    title: 'שגיאה בסורק',
    message: 'סורק RFID #2 לא מגיב. נא לבדוק את החיבור',
    time: 'לפני 3 שעות',
    badge: 'חומרה',
  },
];

/**
 * NotificationsPage - In-app notifications for staff
 * Shows system alerts, sales updates, inventory warnings, etc.
 */
export function NotificationsPage() {
  const { userRole } = useAuth();
  const { t } = useTranslation();

  // Only staff should see this page
  const isStaff = userRole && ['CASHIER', 'MANAGER', 'ADMIN'].includes(userRole);

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

        {mockNotifications.length === 0 ? (
          <EmptyState>
            <p style={{ fontSize: theme.typography.fontSize.lg }}>אין התראות חדשות</p>
            <p>כל העדכונים והאלרטים יופיעו כאן</p>
          </EmptyState>
        ) : (
          <NotificationsList>
            {mockNotifications.map((notification) => (
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
