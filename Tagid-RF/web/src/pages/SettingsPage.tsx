import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useStore } from '@/store';
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

const Section = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin: 0 0 ${theme.spacing.lg} 0;
  padding-bottom: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};
`;

const SettingRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${theme.spacing.md} 0;
  
  &:not(:last-child) {
    border-bottom: 1px solid ${theme.colors.borderLight};
  }
`;

const SettingInfo = styled.div`
  flex: 1;
`;

const SettingLabel = styled.div`
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.text};
  margin-bottom: ${theme.spacing.xs};
`;

const SettingDescription = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
`;

const ToggleSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
`;

const ToggleInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;

  &:checked + span {
    background-color: ${theme.colors.success};
  }

  &:checked + span:before {
    transform: translateX(24px);
  }
`;

const ToggleSlider = styled.span`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${theme.colors.gray[300]};
  transition: ${theme.transitions.base};
  border-radius: ${theme.borderRadius.full};

  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: ${theme.transitions.base};
    border-radius: ${theme.borderRadius.full};
  }
`;

const Select = styled.select`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  background: white;
  min-width: 150px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }
`;

const Button = styled.button`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  background: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.medium};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${theme.colors.primaryDark};
  }
`;

const RoleBadge = styled.span<{ $role: string }>`
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  background: ${props => {
    switch (props.$role) {
      case 'ADMIN': return theme.colors.error;
      case 'MANAGER': return theme.colors.primary;
      case 'CASHIER': return theme.colors.success;
      default: return theme.colors.gray[600];
    }
  }};
  color: white;
  border-radius: ${theme.borderRadius.sm};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
`;

/**
 * SettingsPage - User preferences and system settings
 * 
 * Role-based settings:
 * - All: Language, Theme, Notifications
 * - Cashier+: Receipt settings
 * - Manager+: Report preferences
 * - Admin: System configuration
 */
export function SettingsPage() {
  const { userRole } = useAuth();

  // Connect to store for language and currency
  const locale = useStore((state) => state.locale);
  const currency = useStore((state) => state.currency);
  const toggleLocale = useStore((state) => state.toggleLocale);
  const setCurrency = useStore((state) => state.setCurrency);

  // Local settings
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [autoReceipt, setAutoReceipt] = useState(true);
  const [reportFormat, setReportFormat] = useState('pdf');

  const canSeeReceiptSettings = userRole && ['CASHIER', 'MANAGER', 'ADMIN'].includes(userRole);
  const canSeeReportSettings = userRole && ['MANAGER', 'ADMIN'].includes(userRole);
  const canSeeSystemSettings = userRole === 'ADMIN';

  const handleSave = () => {
    alert('הגדרות נשמרו בהצלחה!');
  };

  return (
    <Layout>
      <Container>
        <Header>
          <Title>הגדרות</Title>
          <Subtitle>נהל את ההעדפות והאפשרויות שלך</Subtitle>
        </Header>

        {/* General Settings - All Users */}
        <Section>
          <SectionTitle>הגדרות כלליות</SectionTitle>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>שפה</SettingLabel>
              <SettingDescription>בחר את שפת הממשק (עברית ⇄ English)</SettingDescription>
            </SettingInfo>
            <Select value={locale} onChange={() => toggleLocale()}>
              <option value="he">עברית</option>
              <option value="en">English</option>
            </Select>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>מטבע</SettingLabel>
              <SettingDescription>בחר את המטבע המועדף</SettingDescription>
            </SettingInfo>
            <Select value={currency} onChange={(e) => setCurrency(e.target.value as any)}>
              <option value="ILS">₪ שקל</option>
              <option value="USD">$ דולר</option>
              <option value="EUR">€ יורו</option>
            </Select>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>מצב כהה</SettingLabel>
              <SettingDescription>החלף בין מצב בהיר לכהה</SettingDescription>
            </SettingInfo>
            <ToggleSwitch>
              <ToggleInput
                type="checkbox"
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
              />
              <ToggleSlider />
            </ToggleSwitch>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>התראות</SettingLabel>
              <SettingDescription>קבל התראות על פעילות חשובה</SettingDescription>
            </SettingInfo>
            <ToggleSwitch>
              <ToggleInput
                type="checkbox"
                checked={notifications}
                onChange={(e) => setNotifications(e.target.checked)}
              />
              <ToggleSlider />
            </ToggleSwitch>
          </SettingRow>
        </Section>

        {/* Receipt Settings - Cashier+ */}
        {canSeeReceiptSettings && (
          <Section>
            <SectionTitle>הגדרות קבלות</SectionTitle>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>הדפסה אוטומטית</SettingLabel>
                <SettingDescription>הדפס קבלה אוטומטית לאחר כל עסקה</SettingDescription>
              </SettingInfo>
              <ToggleSwitch>
                <ToggleInput
                  type="checkbox"
                  checked={autoReceipt}
                  onChange={(e) => setAutoReceipt(e.target.checked)}
                />
                <ToggleSlider />
              </ToggleSwitch>
            </SettingRow>
          </Section>
        )}

        {/* Report Settings - Manager+ */}
        {canSeeReportSettings && (
          <Section>
            <SectionTitle>הגדרות דוחות</SectionTitle>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>פורמט דוח</SettingLabel>
                <SettingDescription>בחר פורמט ברירת מחדל לייצוא דוחות</SettingDescription>
              </SettingInfo>
              <Select value={reportFormat} onChange={(e) => setReportFormat(e.target.value)}>
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="csv">CSV</option>
              </Select>
            </SettingRow>
          </Section>
        )}

        {/* System Settings - Admin Only */}
        {canSeeSystemSettings && (
          <Section>
            <SectionTitle>הגדרות מערכת</SectionTitle>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>ניהול משתמשים</SettingLabel>
                <SettingDescription>הוסף, ערוך או הסר משתמשים מהמערכת</SettingDescription>
              </SettingInfo>
              <Button onClick={() => alert('ניהול משתמשים (בפיתוח)')}>
                נהל משתמשים
              </Button>
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>גיבוי מערכת</SettingLabel>
                <SettingDescription>צור גיבוי של כל נתוני המערכת</SettingDescription>
              </SettingInfo>
              <Button onClick={() => alert('גיבוי מערכת (בפיתוח)')}>
                צור גיבוי
              </Button>
            </SettingRow>
          </Section>
        )}

        {/* Account Info */}
        <Section>
          <SectionTitle>פרטי חשבון</SectionTitle>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>תפקיד נוכחי</SettingLabel>
              <SettingDescription>רמת ההרשאה שלך במערכת</SettingDescription>
            </SettingInfo>
            <RoleBadge $role={userRole || 'CUSTOMER'}>
              {userRole === 'ADMIN' ? 'מנהל מערכת' :
                userRole === 'MANAGER' ? 'מנהל' :
                  userRole === 'CASHIER' ? 'קופאי' : 'לקוח'}
            </RoleBadge>
          </SettingRow>
        </Section>

        <Button onClick={handleSave} style={{ width: '100%', padding: theme.spacing.md }}>
          שמור הגדרות
        </Button>
      </Container>
    </Layout>
  );
}
