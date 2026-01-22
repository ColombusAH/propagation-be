import { useState } from 'react';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useStore } from '@/store';
import { useTranslation } from '@/hooks/useTranslation';
import { theme } from '@/styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  max-width: 900px;
  margin: 0 auto;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: calc(100vh - 64px);
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

const Section = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
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
  gap: ${theme.spacing.lg};
  
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
  line-height: 1.4;
`;

const ToggleSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
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
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);

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
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
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
    transform: translateX(24px);
  }
`;

const Select = styled.select`
  padding: 6px ${theme.spacing.md};
  padding-left: 2rem;
  border: 1px solid ${theme.colors.primary};
  border-radius: ${theme.borderRadius.md};
  font-size: 0.9rem;
  font-weight: ${theme.typography.fontWeight.bold};
  background: white;
  min-width: 160px;
  color: ${theme.colors.primary};
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='%232563EB'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left 0.5rem center;
  transition: all ${theme.transitions.fast};
  
  option {
    color: ${theme.colors.primary};
  }

  &:hover {
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}15;
  }
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}25;
  }
`;

const Button = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 6px ${theme.spacing.md};
  background: ${theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: 0.9rem;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${theme.colors.primaryDark};
  }
`;

const Input = styled.input`
  padding: 6px ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: 0.9rem;
  background: white;
  min-width: 200px;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    border-color: ${theme.colors.primary};
  }
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px ${theme.colors.primary}20;
  }
  
  &::placeholder {
    color: ${theme.colors.textSecondary};
  }
`;

const LogoUpload = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const LogoPreview = styled.div`
  width: 60px;
  height: 60px;
  border: 2px dashed ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${theme.colors.gray[50]};
  overflow: hidden;
  
  img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }
`;

const UploadButton = styled.label`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  background: ${theme.colors.gray[100]};
  color: ${theme.colors.text};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${theme.colors.gray[200]};
  }
  
  input {
    display: none;
  }
`;

const SubsectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  padding: ${theme.spacing.md} 0;
  margin-top: ${theme.spacing.md};
  border-top: 1px solid ${theme.colors.border};
  color: ${theme.colors.textSecondary};
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const SecurityBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: ${theme.colors.success}15;
  color: ${theme.colors.success};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
  font-weight: ${theme.typography.fontWeight.medium};
`;


const ProfileCompletionCard = styled.div`
  background: linear-gradient(135deg, ${theme.colors.primary}08, ${theme.colors.primary}03);
  border: 1px solid ${theme.colors.primary}20;
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.lg};
`;

const ProfileCompletionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.md};
`;

const ProfileCompletionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
`;

const ProfileCompletionPercent = styled.div<{ $complete: boolean }>`
  font-size: ${theme.typography.fontSize.lg};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${props => props.$complete ? theme.colors.success : theme.colors.primary};
`;

const ProgressBarContainer = styled.div`
  height: 8px;
  background: ${theme.colors.gray[200]};
  border-radius: ${theme.borderRadius.full};
  overflow: hidden;
`;

const ProgressBarFill = styled.div<{ $percent: number }>`
  height: 100%;
  width: ${props => props.$percent}%;
  background: ${props => props.$percent === 100
    ? theme.colors.success
    : `linear-gradient(90deg, ${theme.colors.primary}, ${theme.colors.primary}CC)`};
  border-radius: ${theme.borderRadius.full};
  transition: width 0.5s ease;
`;

const MissingFields = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${theme.spacing.xs};
  margin-top: ${theme.spacing.md};
`;

const MissingFieldTag = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: ${theme.colors.gray[100]};
  color: ${theme.colors.textSecondary};
  border-radius: ${theme.borderRadius.full};
  font-size: ${theme.typography.fontSize.xs};
`;


const DeleteLogoButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: ${theme.colors.error}15;
  color: ${theme.colors.error};
  border: none;
  border-radius: ${theme.borderRadius.full};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  
  &:hover {
    background: ${theme.colors.error}25;
  }
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
  const { userRole, token } = useAuth();
  const { t } = useTranslation();

  // Connect to store for language and currency
  const locale = useStore((state) => state.locale);
  const currency = useStore((state) => state.currency);
  const toggleLocale = useStore((state) => state.toggleLocale);
  const setCurrency = useStore((state) => state.setCurrency);

  // Local settings
  const darkMode = useStore((state) => state.darkMode);
  const toggleDarkMode = useStore((state) => state.toggleDarkMode);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [smsNotifications, setSmsNotifications] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [autoReceipt, setAutoReceipt] = useState(true);
  const [reportFormat, setReportFormat] = useState('pdf');

  // Network settings (NETWORK_ADMIN+)
  const [networkName, setNetworkName] = useState('');
  const [networkLogo, setNetworkLogo] = useState<string | null>(null);
  const [bankName, setBankName] = useState('');
  const [bankBranch, setBankBranch] = useState('');
  const [bankAccount, setBankAccount] = useState('');
  const [businessId, setBusinessId] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [networkAddress, setNetworkAddress] = useState('');
  const [networkWebsite, setNetworkWebsite] = useState('');

  const canSeeNetworkSettings = userRole === 'SUPER_ADMIN' || userRole === 'NETWORK_ADMIN';
  const canSeeReceiptSettings = userRole && ['SELLER', 'STORE_MANAGER', 'NETWORK_ADMIN', 'SUPER_ADMIN'].includes(userRole);
  const canSeeReportSettings = userRole && ['STORE_MANAGER', 'NETWORK_ADMIN', 'SUPER_ADMIN'].includes(userRole);
  const canSeeSystemSettings = userRole === 'SUPER_ADMIN' || userRole === 'NETWORK_ADMIN';

  // Function to update notification settings in backend
  const handleNotificationToggle = async (
    channel: 'push' | 'sms' | 'email',
    newValue: boolean
  ) => {
    // Update local state first for immediate UI feedback
    if (channel === 'push') setPushNotifications(newValue);
    if (channel === 'sms') setSmsNotifications(newValue);
    if (channel === 'email') setEmailNotifications(newValue);

    if (!token) {
      console.warn('No token, cannot persist notification setting');
      return;
    }

    try {
      const res = await fetch('/api/v1/notifications/settings', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          [channel]: newValue,
        }),
      });
      if (!res.ok) {
        console.error(`Failed to save ${channel} setting: ${res.status}`);
      } else {
        console.log(`${channel} setting saved successfully`);
      }
    } catch (err) {
      console.error(`Error saving ${channel} setting:`, err);
    }
  };

  const handleSave = () => {
    alert(t('settings.settingsSaved'));
  };

  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setNetworkLogo(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const networkFields = [
    { name: t('settings.networkName'), value: networkName, required: true },
    { name: t('settings.networkLogo'), value: networkLogo, required: true },
    { name: t('settings.businessId'), value: businessId, required: true },
    { name: t('settings.phone'), value: contactPhone, required: true },
    { name: t('settings.email'), value: contactEmail, required: true },
    { name: t('settings.address'), value: networkAddress, required: false },
    { name: t('settings.website'), value: networkWebsite, required: false },
    { name: t('settings.bankName'), value: bankName, required: true },
    { name: t('settings.bankBranch'), value: bankBranch, required: true },
    { name: t('settings.bankAccount'), value: bankAccount, required: true },
  ];

  const filledFields = networkFields.filter(f => f.value).length;
  const totalFields = networkFields.length;
  const completionPercent = Math.round((filledFields / totalFields) * 100);
  const missingRequiredFields = networkFields.filter(f => f.required && !f.value);

  return (
    <Layout>
      <Container>
        <Header>
          <Title>{t('settings.title')}</Title>
          <Subtitle>{t('settings.subtitle')}</Subtitle>
        </Header>

        {/* General Settings - All Users */}
        <Section>
          <SectionTitle>{t('settings.general')}</SectionTitle>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('settings.language')}</SettingLabel>
              <SettingDescription>{t('settings.languageDesc')}</SettingDescription>
            </SettingInfo>
            <Select value={locale} onChange={() => toggleLocale()}>
              <option value="he">{t('language.he')}</option>
              <option value="en">{t('language.en')}</option>
            </Select>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('settings.currency')}</SettingLabel>
              <SettingDescription>{t('settings.currencyDesc')}</SettingDescription>
            </SettingInfo>
            <Select value={currency} onChange={(e) => setCurrency(e.target.value as any)} style={{ direction: 'ltr', textAlign: 'right' }}>
              <option value="ILS">{t('currency.ils')}</option>
              <option value="USD">{t('currency.usd')}</option>
              <option value="EUR">{t('currency.eur')}</option>
            </Select>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('settings.notificationsPush')}</SettingLabel>
              <SettingDescription>{t('settings.notificationsPushDesc')}</SettingDescription>
            </SettingInfo>
            <ToggleSwitch>
              <ToggleInput
                type="checkbox"
                checked={pushNotifications}
                onChange={(e) => handleNotificationToggle('push', e.target.checked)}
              />
              <ToggleSlider />
            </ToggleSwitch>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('settings.notificationsSms')}</SettingLabel>
              <SettingDescription>{t('settings.notificationsSmsDesc')}</SettingDescription>
            </SettingInfo>
            <ToggleSwitch>
              <ToggleInput
                type="checkbox"
                checked={smsNotifications}
                onChange={(e) => handleNotificationToggle('sms', e.target.checked)}
              />
              <ToggleSlider />
            </ToggleSwitch>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('settings.notificationsEmail')}</SettingLabel>
              <SettingDescription>{t('settings.notificationsEmailDesc')}</SettingDescription>
            </SettingInfo>
            <ToggleSwitch>
              <ToggleInput
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => handleNotificationToggle('email', e.target.checked)}
              />
              <ToggleSlider />
            </ToggleSwitch>
          </SettingRow>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('settings.darkMode')}</SettingLabel>
              <SettingDescription>{t('settings.darkModeDesc')}</SettingDescription>
            </SettingInfo>
            <ToggleSwitch>
              <ToggleInput
                type="checkbox"
                checked={darkMode}
                onChange={() => toggleDarkMode()}
              />
              <ToggleSlider />
            </ToggleSwitch>
          </SettingRow>
        </Section>

        {/* Network Settings - Network Admin+ */}
        {canSeeNetworkSettings && (
          <Section>
            <SectionTitle>{t('settings.networkDetails')}</SectionTitle>

            <ProfileCompletionCard>
              <ProfileCompletionHeader>
                <ProfileCompletionTitle>
                  <span className="material-symbols-outlined" style={{ fontSize: '20px', color: theme.colors.primary }}>task_alt</span>
                  {t('settings.networkProfileCompletion')}
                </ProfileCompletionTitle>
                <ProfileCompletionPercent $complete={completionPercent === 100}>
                  {completionPercent}%
                </ProfileCompletionPercent>
              </ProfileCompletionHeader>
              <ProgressBarContainer>
                <ProgressBarFill $percent={completionPercent} />
              </ProgressBarContainer>
              {missingRequiredFields.length > 0 && (
                <MissingFields>
                  <span style={{ fontSize: theme.typography.fontSize.xs, color: theme.colors.textSecondary }}>{t('settings.missingFields')}</span>
                  {missingRequiredFields.map(f => (
                    <MissingFieldTag key={f.name}>
                      <span className="material-symbols-outlined" style={{ fontSize: '12px' }}>circle</span>
                      {f.name}
                    </MissingFieldTag>
                  ))}
                </MissingFields>
              )}
            </ProfileCompletionCard>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.networkName')}</SettingLabel>
                <SettingDescription>{t('settings.networkNameDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="text"
                value={networkName}
                onChange={(e) => setNetworkName(e.target.value)}
                placeholder={t('settings.networkNamePlaceholder')}
              />
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.networkLogo')}</SettingLabel>
                <SettingDescription>{t('settings.networkLogoDesc')}</SettingDescription>
              </SettingInfo>
              <LogoUpload>
                <LogoPreview>
                  {networkLogo ? (
                    <img src={networkLogo} alt={t('settings.networkLogo')} />
                  ) : (
                    <span className="material-symbols-outlined" style={{ color: theme.colors.gray[400], fontSize: '24px' }}>image</span>
                  )}
                </LogoPreview>
                <UploadButton>
                  <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>upload</span>
                  {t('settings.uploadLogo')}
                  <input type="file" accept="image/*" onChange={handleLogoUpload} />
                </UploadButton>
                {networkLogo && (
                  <DeleteLogoButton onClick={() => setNetworkLogo(null)} title={t('settings.deleteLogo')}>
                    <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>close</span>
                  </DeleteLogoButton>
                )}
              </LogoUpload>
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.businessId')}</SettingLabel>
                <SettingDescription>{t('settings.businessIdDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="text"
                value={businessId}
                onChange={(e) => setBusinessId(e.target.value.replace(/\D/g, '').slice(0, 9))}
                placeholder={t('settings.businessIdPlaceholder')}
                style={{ minWidth: '160px', textAlign: 'center', letterSpacing: '1px' }}
                maxLength={9}
              />
            </SettingRow>

            <SubsectionHeader>
              <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>contact_phone</span>
              {t('settings.contactDetails')}
            </SubsectionHeader>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.phone')}</SettingLabel>
                <SettingDescription>{t('settings.phoneDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="tel"
                value={contactPhone}
                onChange={(e) => setContactPhone(e.target.value.replace(/[^\d-]/g, ''))}
                placeholder={t('settings.phonePlaceholder')}
                style={{ minWidth: '180px', direction: 'ltr', textAlign: 'right' }}
              />
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.email')}</SettingLabel>
                <SettingDescription>{t('settings.emailDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="email"
                value={contactEmail}
                onChange={(e) => setContactEmail(e.target.value)}
                placeholder={t('settings.emailPlaceholder')}
                style={{ minWidth: '220px', direction: 'ltr', textAlign: 'right' }}
              />
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.address')}</SettingLabel>
                <SettingDescription>{t('settings.addressDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="text"
                value={networkAddress}
                onChange={(e) => setNetworkAddress(e.target.value)}
                placeholder={t('settings.addressPlaceholder')}
                style={{ minWidth: '250px' }}
              />
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.website')}</SettingLabel>
                <SettingDescription>{t('settings.websiteDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="url"
                value={networkWebsite}
                onChange={(e) => setNetworkWebsite(e.target.value)}
                placeholder={t('settings.websitePlaceholder')}
                style={{ minWidth: '250px', direction: 'ltr', textAlign: 'right' }}
              />
            </SettingRow>

            <SubsectionHeader>
              <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>account_balance</span>
              {t('settings.bankDetails')}
              <SecurityBadge>
                <span className="material-symbols-outlined" style={{ fontSize: '12px' }}>lock</span>
                מאובטח
              </SecurityBadge>
            </SubsectionHeader>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.bankName')}</SettingLabel>
                <SettingDescription>{t('settings.bankNameDesc')}</SettingDescription>
              </SettingInfo>
              <Select
                value={bankName}
                onChange={(e) => setBankName(e.target.value)}
                style={{ minWidth: '200px' }}
              >
                <option value="">{t('settings.bankPlaceholder')}</option>
                <option value="leumi">{t('banks.leumi')}</option>
                <option value="hapoalim">{t('banks.hapoalim')}</option>
                <option value="discount">{t('banks.discount')}</option>
                <option value="mizrahi">{t('banks.mizrahi')}</option>
                <option value="fibi">{t('banks.fibi')}</option>
                <option value="mercantile">{t('banks.mercantile')}</option>
                <option value="otsar">{t('banks.otsar')}</option>
                <option value="igud">{t('banks.igud')}</option>
                <option value="yahav">{t('banks.yahav')}</option>
                <option value="massad">{t('banks.massad')}</option>
              </Select>
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.bankBranch')}</SettingLabel>
                <SettingDescription>{t('settings.bankBranchDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="text"
                value={bankBranch}
                onChange={(e) => setBankBranch(e.target.value.replace(/\D/g, '').slice(0, 3))}
                placeholder="000"
                style={{ minWidth: '120px', textAlign: 'center', letterSpacing: '2px' }}
                maxLength={3}
              />
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.bankAccount')}</SettingLabel>
                <SettingDescription>{t('settings.bankAccountDesc')}</SettingDescription>
              </SettingInfo>
              <Input
                type="text"
                value={bankAccount}
                onChange={(e) => setBankAccount(e.target.value.replace(/\D/g, '').slice(0, 9))}
                placeholder="000000000"
                style={{ minWidth: '180px', textAlign: 'center', letterSpacing: '1px' }}
                maxLength={9}
              />
            </SettingRow>
          </Section>
        )}

        {/* Receipt Settings - Cashier+ */}
        {canSeeReceiptSettings && (
          <Section>
            <SectionTitle>{t('settings.receipts')}</SectionTitle>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.autoPrint')}</SettingLabel>
                <SettingDescription>{t('settings.autoPrintDesc')}</SettingDescription>
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
            <SectionTitle>{t('settings.system')}</SectionTitle>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.userManagement')}</SettingLabel>
                <SettingDescription>{t('settings.userManagementDesc')}</SettingDescription>
              </SettingInfo>
              <Button onClick={() => alert(t('settings.userManagement') + ' (in development)')}>
                {t('settings.manageUsers')}
              </Button>
            </SettingRow>

            <SettingRow>
              <SettingInfo>
                <SettingLabel>{t('settings.backup')}</SettingLabel>
                <SettingDescription>{t('settings.backupDesc')}</SettingDescription>
              </SettingInfo>
              <Button onClick={() => alert(t('settings.backup') + ' (in development)')}>
                {t('settings.createBackup')}
              </Button>
            </SettingRow>
          </Section>
        )}

        {/* Account Info */}
        <Section>
          <SectionTitle>{t('settings.account')}</SectionTitle>

          <SettingRow>
            <SettingInfo>
              <SettingLabel>{t('dashboard.logout')}</SettingLabel>
              <SettingDescription>התנתק מהחשבון שלך</SettingDescription>
            </SettingInfo>
            <Button onClick={() => {
              if (confirm('האם אתה בטוח שברצונך להתנתק?')) {
                window.location.href = '/';
              }
            }}>
              {t('dashboard.logout')}
            </Button>
          </SettingRow>
        </Section>

        <Button onClick={handleSave} style={{ width: '100%', padding: theme.spacing.md }}>
          {t('settings.saveSettings')}
        </Button>
      </Container>
    </Layout>
  );
}
