import { useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';
import { useWebSocket } from '@/hooks/useWebSocket';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 900px;
  margin: 0 auto;
  min-height: calc(100vh - 64px);
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
  color: white;
  position: relative;
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
  border: 1px solid rgba(255, 255, 255, 0.3);

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }
`;

const NotificationsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const NotificationCard = styled.div<{ $type: string }>`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-right: 6px solid ${props =>
    props.$type === 'error' ? theme.colors.error :
      props.$type === 'warning' ? theme.colors.warning :
        theme.colors.primary
  };
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 100px 20px;
  background: white;
  border-radius: 24px;
  border: 1px dashed ${theme.colors.border};
  color: ${theme.colors.textSecondary};
`;

/**
 * NotificationsPage - In-app notifications for staff
 */
export function NotificationsPage() {
  const { userRole, token } = useAuth();
  const [items, setItems] = useState<any[]>([]);

  useWebSocket({
    url: '/ws/rfid',
    onMessage: (msg) => {
      if (msg.type === 'theft_alert') {
        setItems(prev => [{
          id: Date.now().toString(),
          type: 'error',
          title: '🚨 התרעת גניבה!',
          message: `מוצר: ${msg.data.product} זוהה ביציאה ללא תשלום`,
          time: new Date().toLocaleTimeString('he-IL'),
          badge: msg.data.location || 'שער ראשי'
        }, ...prev]);
      }
    }
  });

  const triggerTest = async () => {
    try {
      await fetch('/api/v1/notifications/test-push', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (e) {
      console.error(e);
    }
  };

  const isStaff = userRole && ['SUPER_ADMIN', 'NETWORK_ADMIN', 'STORE_MANAGER', 'SELLER'].includes(userRole);

  if (!isStaff) return <Layout><Container><EmptyState>אין הרשאה</EmptyState></Container></Layout>;

  return (
    <Layout>
      <Container>
        <Header>
          <div>
            <h1 style={{ margin: 0 }}>התראות פוש</h1>
            <p style={{ margin: 0, opacity: 0.8 }}>ניהול בזמן אמת של אירועי חנות</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={triggerTest} style={{
              background: 'white',
              color: '#2563EB',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '12px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}>
              שלח פוש לבדיקה
            </button>
            <SettingsButton to="/notification-settings">הגדרות</SettingsButton>
          </div>
        </Header>

        {items.length === 0 ? (
          <EmptyState>
            <span className="material-symbols-outlined" style={{ fontSize: '48px', marginBottom: '12px' }}>notifications_off</span>
            <p>אין התראות חדשות. לחץ על הכפתור למעלה כדי לבדוק שליחת פוש.</p>
          </EmptyState>
        ) : (
          <NotificationsList>
            {items.map((item) => (
              <NotificationCard key={item.id} $type={item.type}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <h3 style={{ margin: 0 }}>{item.title}</h3>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>{item.time}</span>
                </div>
                <p style={{ margin: 0, color: '#475569' }}>{item.message}</p>
                <div style={{ marginTop: '8px' }}>
                  <span style={{
                    fontSize: '10px',
                    background: item.type === 'error' ? '#FEE2E2' : '#E0F2FE',
                    color: item.type === 'error' ? '#991B1B' : '#0369A1',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontWeight: 'bold'
                  }}>{item.badge}</span>
                </div>
              </NotificationCard>
            ))}
          </NotificationsList>
        )}
      </Container>
    </Layout>
  );
}
