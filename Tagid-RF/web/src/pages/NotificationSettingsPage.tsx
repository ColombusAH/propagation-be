import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 1000px;
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

const Section = styled.section`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
  animation: ${theme.animations.slideUp};
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
  max-width: 220px;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  padding-left: 2.5rem;
  border: 1px solid ${theme.colors.primary};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  background: white;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='%232563EB'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left 0.75rem center;
  transition: all ${theme.transitions.fast};

  &:hover {
    box-shadow: 0 0 0 3px ${theme.colors.primary}15;
  }

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}25;
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
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.textSecondary};
  border-bottom: 2px solid ${theme.colors.border};

  &:not(:first-child) {
    text-align: center;
    width: 100px;
  }
`;

const Td = styled.td`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.borderLight};
  
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
    box-shadow: 0 0 10px ${theme.colors.primary}40;
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
  background-color: ${theme.colors.gray[300]};
  border-radius: 24px;
  transition: 0.3s;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);

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
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
`;

const Button = styled.button`
  background-color: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  font-size: ${theme.typography.fontSize.base};
  cursor: pointer;
  transition: all ${theme.transitions.base};
  box-shadow: ${theme.shadows.sm};

  &:hover {
    background-color: ${theme.colors.primaryDark};
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.md};
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const InfoBox = styled.div`
  background: white;
  border: 1px solid ${theme.colors.border};
  border-right: 4px solid ${theme.colors.info};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  box-shadow: ${theme.shadows.sm};
  animation: ${theme.animations.slideUp};
`;

interface NotificationPreference {
  type: string;
  name: string;
  description: string;
  push: boolean;
  sms: boolean;
  email: boolean;
  customTitle?: string;
  customBody?: string;
}

const storesList = [
  { id: 'all', name: 'כל החנויות' },
];

const EditModal = styled.div<{ isOpen: boolean }>`
  display: ${props => props.isOpen ? 'flex' : 'none'};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${theme.colors.overlay};
  z-index: ${theme.zIndex.modal};
  align-items: center;
  justify-content: center;
  animation: ${theme.animations.fadeIn};
`;

const ModalContent = styled.div`
  background: ${theme.colors.surface};
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.xl};
  width: 100%;
  max-width: 500px;
  box-shadow: ${theme.shadows.lg};
  border: 1px solid ${theme.colors.border};
`;

const FormGroup = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Input = styled.input`
  width: 100%;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  &:focus {
    border-color: ${theme.colors.primary};
    outline: none;
    box-shadow: 0 0 0 2px ${theme.colors.primary}20;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  min-height: 100px;
  resize: vertical;
  &:focus {
    border-color: ${theme.colors.primary};
    outline: none;
    box-shadow: 0 0 0 2px ${theme.colors.primary}20;
  }
`;

const ModalActions = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  justify-content: flex-end;
  margin-top: ${theme.spacing.xl};
`;

const GhostButton = styled.button`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.md};
  color: ${theme.colors.textSecondary};
  font-weight: ${theme.typography.fontWeight.medium};
  &:hover {
    background: ${theme.colors.gray[100]};
  }
`;

const EditButton = styled.button`
  padding: 4px;
  color: ${theme.colors.primary};
  border-radius: ${theme.borderRadius.sm};
  display: flex;
  align-items: center;
  justify-content: center;
  &:hover {
    background: ${theme.colors.primary}10;
  }
`;

const TypeHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

// Default notification preferences
const defaultPreferences: NotificationPreference[] = [
  {
    type: 'UNPAID_EXIT',
    name: 'מוצר לא שולם ביציאה',
    description: 'התראה כאשר תג שלא שולם נסרק בשער היציאה - מזהה מוצר ופרטים',
    push: true,
    sms: true,
    email: true,
    customTitle: '⚠️ התראת אבטחה',
    customBody: 'מוצר [PRODUCT] יצא ללא תשלום מסניף [STORE]',
  },
  {
    type: 'SALE',
    name: 'מכירה חדשה',
    description: 'קבל התראה על כל מכירה שמתבצעת',
    push: true,
    sms: false,
    email: false,
    customTitle: '💰 מכירה חדשה',
    customBody: 'נמכר [PRODUCT] בסכום של [AMOUNT]',
  },
  {
    type: 'LOW_STOCK',
    name: 'מלאי נמוך',
    description: 'התראה כאשר מוצר מגיע לסף המינימום',
    push: true,
    sms: true,
    email: true,
    customTitle: '📦 מלאי נמוך',
    customBody: 'המלאי עבור [PRODUCT] עומד להיגמר',
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

const BulkActions = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.md};
`;

const SecondaryButton = styled.button`
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border: 1px solid ${theme.colors.primary};
  color: ${theme.colors.primary};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.semibold};
  background: white;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${theme.colors.primary}10;
  }
`;

/**
 * NotificationSettingsPage - Configure notification preferences
 * Staff can choose what notifications to receive and how (Push/SMS/Email)
 */
interface Employee {
  id: number;
  name: string;
  role: string;
  enabled: boolean;
}

export function NotificationSettingsPage() {
  const { userRole } = useAuth();
  const [selectedStore, setSelectedStore] = useState('all');
  const [preferences, setPreferences] = useState<NotificationPreference[]>(defaultPreferences);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [showUserSelect, setShowUserSelect] = useState(false);
  const [showStoreSelect, setShowStoreSelect] = useState(false);
  const [editingPref, setEditingPref] = useState<NotificationPreference | null>(null);
  const [tempTitle, setTempTitle] = useState('');
  const [tempBody, setTempBody] = useState('');

  // Mock data for selection (In real app, fetch from store/API)
  const availableUsers = [
    { id: 101, name: 'יוסי כהן', role: 'מוכר' },
    { id: 102, name: 'מיכל לוי', role: 'מוכרת' },
    { id: 103, name: 'אבירון לוי', role: 'מוכר' },
  ];

  const availableStores = [
    { id: 'store-1', name: 'סניף תל אביב' },
    { id: 'store-2', name: 'סניף ירושלים' },
    { id: 'store-3', name: 'סניף חיפה' },
  ];

  const isChainAdmin = userRole === 'SUPER_ADMIN' || userRole === 'NETWORK_ADMIN';
  const isStaff = userRole && ['SUPER_ADMIN', 'NETWORK_ADMIN', 'STORE_MANAGER', 'SELLER'].includes(userRole);

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

  const addEmployee = (user: { id: number; name: string; role: string }) => {
    if (!employees.find(e => e.id === user.id)) {
      setEmployees([...employees, { ...user, enabled: true }]);
    }
    setShowUserSelect(false);
  };

  const addStore = (store: { id: string; name: string }) => {
    // Logic for adding store to notifications
    console.log('Added store to notifications:', store);
    setShowStoreSelect(false);
  };

  const openEditModal = (pref: NotificationPreference) => {
    setEditingPref(pref);
    setTempTitle(pref.customTitle || '');
    setTempBody(pref.customBody || '');
  };

  const saveCustomMessage = () => {
    if (editingPref) {
      setPreferences(prev => prev.map(p =>
        p.type === editingPref.type
          ? { ...p, customTitle: tempTitle, customBody: tempBody }
          : p
      ));
      setEditingPref(null);
    }
  };

  const togglePreference = (type: string, channel: 'push' | 'sms' | 'email') => {
    setPreferences(prev => prev.map(pref => {
      if (pref.type === type) {
        return { ...pref, [channel]: !pref[channel] };
      }
      return pref;
    }));
    // Log the change for visual confirmation in demo
    console.log(`Updated ${type} notification channel ${channel}`);
  };

  const handleBulkPreferences = (enabled: boolean) => {
    setPreferences(preferences.map(pref => ({
      ...pref,
      push: enabled,
      sms: enabled,
      email: enabled
    })));
  };

  const handleBulkEmployee = (enable: boolean) => {
    setEmployees(prev => prev.map(emp => ({ ...emp, enabled: enable })));
  };

  const toggleEmployee = (id: number) => {
    setEmployees(prev => prev.map(emp =>
      emp.id === id ? { ...emp, enabled: !emp.enabled } : emp
    ));
  };

  const handleSave = () => {
    // In real app, this would call the API
    if (Notification.permission !== 'granted') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          console.log('Push notifications enabled');
        }
      });
    }
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
                {storesList.map(store => (
                  <option key={store.id} value={store.id}>{store.name}</option>
                ))}
              </Select>
            </StoreSelector>
          </Section>
        )}

        {/* User alerts management - for STORE_MANAGER+ */}
        {(isChainAdmin || userRole === 'STORE_MANAGER') && (
          <Section>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
              <div>
                <SectionTitle style={{ marginBottom: '4px' }}>ניהול עובדים מקבלי התראות</SectionTitle>
                <Subtitle>בחר אילו עובדים יקבלו התראות פוש ומייל עבור החנות שלהם</Subtitle>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                {isChainAdmin && (
                  <Button onClick={() => setShowStoreSelect(true)} style={{ padding: '8px 16px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>add_business</span>
                    <span>הוסף חנות</span>
                  </Button>
                )}
                <Button onClick={() => setShowUserSelect(true)} style={{ padding: '8px 16px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>person_add</span>
                  <span>הוסף עובד</span>
                </Button>
              </div>
            </div>

            <BulkActions>
              <SecondaryButton onClick={() => handleBulkEmployee(true)}>בחר הכל</SecondaryButton>
              <SecondaryButton onClick={() => handleBulkEmployee(false)}>בטל הכל</SecondaryButton>
            </BulkActions>

            <Table>
              <thead>
                <tr>
                  <Th>שם העובד</Th>
                  <Th>תפקיד</Th>
                  <Th>קבלת התראות</Th>
                </tr>
              </thead>
              <tbody>
                {employees.map(emp => (
                  <tr key={emp.id}>
                    <Td>{emp.name}</Td>
                    <Td>{emp.role}</Td>
                    <Td>
                      <Toggle>
                        <ToggleInput
                          type="checkbox"
                          checked={emp.enabled}
                          onChange={() => toggleEmployee(emp.id)}
                        />
                        <ToggleSlider />
                      </Toggle>
                    </Td>
                  </tr>
                ))}
                {employees.length === 0 && (
                  <tr>
                    <Td colSpan={3} style={{ textAlign: 'center', padding: '2rem', color: theme.colors.textMuted }}>
                      טרם נבחרו עובדים לקבלת התראות. לחץ על "הוסף עובד" כדי להתחיל.
                    </Td>
                  </tr>
                )}
              </tbody>
            </Table>
          </Section>
        )}

        {/* User Selection Modal */}
        <EditModal isOpen={showUserSelect}>
          <ModalContent>
            <SectionTitle style={{ border: 'none' }}>בחר עובד להוספה</SectionTitle>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
              {availableUsers.map(user => (
                <div
                  key={user.id}
                  onClick={() => addEmployee(user)}
                  style={{
                    padding: '12px',
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div style={{ fontWeight: '500' }}>{user.name}</div>
                  <div style={{ fontSize: '12px', color: theme.colors.textMuted }}>{user.role}</div>
                </div>
              ))}
            </div>
            <ModalActions>
              <GhostButton onClick={() => setShowUserSelect(false)}>ביטול</GhostButton>
            </ModalActions>
          </ModalContent>
        </EditModal>

        {/* Store Selection Modal */}
        <EditModal isOpen={showStoreSelect}>
          <ModalContent>
            <SectionTitle style={{ border: 'none' }}>בחר חנות להוספה</SectionTitle>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px' }}>
              {availableStores.map(store => (
                <div
                  key={store.id}
                  onClick={() => addStore(store)}
                  style={{
                    padding: '12px',
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ fontWeight: '500' }}>{store.name}</div>
                </div>
              ))}
            </div>
            <ModalActions>
              <GhostButton onClick={() => setShowStoreSelect(false)}>ביטול</GhostButton>
            </ModalActions>
          </ModalContent>
        </EditModal>

        {/* Notification preferences table */}
        <Section>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
            <SectionTitle style={{ margin: 0, border: 'none', padding: 0 }}>סוגי התראות</SectionTitle>
            <BulkActions style={{ margin: 0 }}>
              <SecondaryButton onClick={() => handleBulkPreferences(true)}>בחר הכל</SecondaryButton>
              <SecondaryButton onClick={() => handleBulkPreferences(false)}>בטל הכל</SecondaryButton>
            </BulkActions>
          </div>

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
                      <TypeHeader>
                        <TypeName>{pref.name}</TypeName>
                        <EditButton onClick={() => openEditModal(pref)} title="ערוך תוכן">
                          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>edit</span>
                        </EditButton>
                      </TypeHeader>
                      <TypeDescription>{pref.description}</TypeDescription>
                      {(pref.customTitle || pref.customBody) && (
                        <div style={{ marginTop: '8px', fontSize: '12px', color: theme.colors.primary, fontStyle: 'italic' }}>
                          תוכן מותאם אישית הוגדר
                        </div>
                      )}
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

        <EditModal isOpen={!!editingPref}>
          <ModalContent>
            <SectionTitle style={{ border: 'none' }}>עריכת תוכן התראה: {editingPref?.name}</SectionTitle>
            <Subtitle style={{ marginBottom: theme.spacing.lg }}>
              השתמש בתגיות כמו [PRODUCT], [STORE], [AMOUNT] שישתנו אוטומטית.
            </Subtitle>

            <FormGroup>
              <Label>כותרת ההתראה</Label>
              <Input
                value={tempTitle}
                onChange={(e) => setTempTitle(e.target.value)}
                placeholder="לדוגמה: ⚠️ התראת אבטחה"
              />
            </FormGroup>

            <FormGroup>
              <Label>תוכן ההודעה</Label>
              <TextArea
                value={tempBody}
                onChange={(e) => setTempBody(e.target.value)}
                placeholder="לדוגמה: מוצר [PRODUCT] יצא ללא תשלום מסניף [STORE]"
              />
            </FormGroup>

            <ModalActions>
              <GhostButton onClick={() => setEditingPref(null)}>ביטול</GhostButton>
              <Button onClick={saveCustomMessage}>שמור תוכן</Button>
            </ModalActions>
          </ModalContent>
        </EditModal>
      </Container>
    </Layout>
  );
}
