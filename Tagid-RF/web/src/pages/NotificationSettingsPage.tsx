import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1000px;
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

const Section = styled.section`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.md} 0;
  padding-bottom: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};
`;

const StoreSelector = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.xs};
`;

const Select = styled.select`
  width: 100%;
  max-width: 300px;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: white;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: right;
  padding: ${theme.spacing.md};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.textSecondary};
  border-bottom: 1px solid ${theme.colors.border};

  &:not(:first-child) {
    text-align: center;
    width: 100px;
  }
`;

const Td = styled.td`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};
  
  &:not(:first-child) {
    text-align: center;
  }
`;

const NotificationType = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
`;

const TypeName = styled.span`
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
`;

const TypeDescription = styled.span`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const Toggle = styled.label`
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  cursor: pointer;
`;

const ToggleInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;

  &:checked + span {
    background-color: ${theme.colors.primary};
  }

  &:checked + span:before {
    transform: translateX(20px);
  }
`;

const ToggleSlider = styled.span`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  border-radius: 24px;
  transition: 0.3s;

  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    border-radius: 50%;
    transition: 0.3s;
  }
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: background-color ${theme.transitions.fast};

  &:hover {
    background-color: ${theme.colors.primaryDark};
  }
`;

const InfoBox = styled.div`
  background: ${theme.colors.backgroundAlt};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

interface NotificationPreference {
  type: string;
  name: string;
  description: string;
  push: boolean;
  sms: boolean;
  email: boolean;
}

// Mock stores for CHAIN_ADMIN
const mockStores = [
  { id: 'all', name: 'כל החנויות' },
  { id: '1', name: 'סניף תל אביב' },
  { id: '2', name: 'סניף ירושלים' },
  { id: '3', name: 'סניף חיפה' },
];

// Default notification preferences
const defaultPreferences: NotificationPreference[] = [
  {
    type: 'UNPAID_EXIT',
    name: 'מוצר לא שולם ביציאה',
    description: 'התראה כאשר תג שלא שולם נסרק בשער היציאה - מזהה מוצר ופרטים',
    push: true,
    sms: true,
    email: true,
  },
  {
    type: 'SALE',
    name: 'מכירה חדשה',
    description: 'קבל התראה על כל מכירה שמתבצעת',
    push: true,
    sms: false,
    email: false,
  },
  {
    type: 'LOW_STOCK',
    name: 'מלאי נמוך',
    description: 'התראה כאשר מוצר מגיע לסף המינימום',
    push: true,
    sms: true,
    email: true,
  },
  {
    type: 'GOAL_ACHIEVED',
    name: 'יעד הושג',
    description: 'התראה כאשר מגיעים ליעד מכירות',
    push: true,
    sms: false,
    email: true,
  },
  {
    type: 'SYSTEM_UPDATE',
    name: 'עדכון מערכת',
    description: 'עדכונים על גרסאות חדשות ותחזוקה',
    push: false,
    sms: false,
    email: true,
  },
  {
    type: 'NEW_USER',
    name: 'משתמש חדש',
    description: 'התראה כאשר מוכר חדש מצטרף',
    push: true,
    sms: false,
    email: true,
  },
  {
    type: 'ERROR',
    name: 'שגיאת מערכת',
    description: 'התראה על תקלות חומרה או תוכנה',
    push: true,
    sms: true,
    email: true,
  },
];

/**
 * NotificationSettingsPage - Configure notification preferences
 * Staff can choose what notifications to receive and how (Push/SMS/Email)
 */
export function NotificationSettingsPage() {
  const { userRole } = useAuth();
  const [selectedStore, setSelectedStore] = useState('all');
  const [preferences, setPreferences] = useState<NotificationPreference[]>(defaultPreferences);

  const isChainAdmin = userRole === 'ADMIN'; // CHAIN_ADMIN in new system
  const isStaff = userRole && ['CASHIER', 'MANAGER', 'ADMIN'].includes(userRole);

  if (!isStaff) {
    return (
      <Layout>
        <Container>
          <Title>אין גישה</Title>
          <Subtitle>עמוד זה זמין רק לצוות</Subtitle>
        </Container>
      </Layout>
    );
  }

  const togglePreference = (type: string, channel: 'push' | 'sms' | 'email') => {
    setPreferences(prev => prev.map(pref => {
      if (pref.type === type) {
        return { ...pref, [channel]: !pref[channel] };
      }
      return pref;
    }));
  };

  const handleSave = () => {
    // In real app, this would call the API
    alert('הגדרות נשמרו בהצלחה!');
    console.log('Saved preferences:', { store: selectedStore, preferences });
  };

  return (
    <Layout>
      <Container>
        <Header>
          <Title>הגדרות התראות</Title>
          <Subtitle>בחר על מה לקבל התראה ובאיזה ערוץ</Subtitle>
        </Header>

        <InfoBox>
          <strong>שים לב:</strong> התראות Push דורשות אישור מהדפדפן.
          SMS ואימייל יישלחו לפרטי הקשר שלך בחשבון.
        </InfoBox>

        {/* Store selector - only for CHAIN_ADMIN */}
        {isChainAdmin && (
          <Section>
            <SectionTitle>סינון לפי חנות</SectionTitle>
            <StoreSelector>
              <Label>בחר חנות לקבלת התראות</Label>
              <Select
                value={selectedStore}
                onChange={(e) => setSelectedStore(e.target.value)}
              >
                {mockStores.map(store => (
                  <option key={store.id} value={store.id}>{store.name}</option>
                ))}
              </Select>
            </StoreSelector>
          </Section>
        )}

        {/* Notification preferences table */}
        <Section>
          <SectionTitle>סוגי התראות</SectionTitle>

          <Table>
            <thead>
              <tr>
                <Th>סוג התראה</Th>
                <Th>Push</Th>
                <Th>SMS</Th>
                <Th>אימייל</Th>
              </tr>
            </thead>
            <tbody>
              {preferences.map(pref => (
                <tr key={pref.type}>
                  <Td>
                    <NotificationType>
                      <TypeName>{pref.name}</TypeName>
                      <TypeDescription>{pref.description}</TypeDescription>
                    </NotificationType>
                  </Td>
                  <Td>
                    <Toggle>
                      <ToggleInput
                        type="checkbox"
                        checked={pref.push}
                        onChange={() => togglePreference(pref.type, 'push')}
                      />
                      <ToggleSlider />
                    </Toggle>
                  </Td>
                  <Td>
                    <Toggle>
                      <ToggleInput
                        type="checkbox"
                        checked={pref.sms}
                        onChange={() => togglePreference(pref.type, 'sms')}
                      />
                      <ToggleSlider />
                    </Toggle>
                  </Td>
                  <Td>
                    <Toggle>
                      <ToggleInput
                        type="checkbox"
                        checked={pref.email}
                        onChange={() => togglePreference(pref.type, 'email')}
                      />
                      <ToggleSlider />
                    </Toggle>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Section>

        <Button onClick={handleSave}>
          שמור הגדרות
        </Button>
      </Container>
    </Layout>
  );
}
