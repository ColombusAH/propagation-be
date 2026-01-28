import { useState } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { Link } from 'react-router-dom';

interface NotificationChannelState {
  push: boolean;
  whatsapp: boolean;
  email: boolean;
}

interface NotificationScenario {
  id: string;
  label: string;
  description: string;
  icon: string;
  color: string;
  channels: NotificationChannelState;
}

export function NotificationSettingsPage() {
  const { userRole } = useAuth();
  const [notificationPermission, setNotificationPermission] = useState(Notification.permission);

  // הגדרת התרחישים והברירות מחדל שלהם
  const [scenarios, setScenarios] = useState<NotificationScenario[]>([
    {
      id: 'THEFT_ALERT',
      label: 'התרעת גניבה',
      description: 'זיהוי יציאת פריט שלא שולם משער החרמות',
      icon: 'gpp_bad', // Security Alert Icon
      color: 'text-red-600 bg-red-50',
      channels: { push: true, whatsapp: true, email: false }
    },
    {
      id: 'DEVICE_OFFLINE',
      label: 'תקלת חומרה',
      description: 'ניתוק תקשורת עם קורא RFID או בקר שער',
      icon: 'router', // Hardware Icon
      color: 'text-orange-600 bg-orange-50',
      channels: { push: true, whatsapp: false, email: true }
    },
    {
      id: 'LOW_STOCK',
      label: 'מלאי נמוך',
      description: 'התראה כאשר כמות מוצר יורדת מתחת למינימום',
      icon: 'inventory_2', // Inventory Icon
      color: 'text-blue-600 bg-blue-50',
      channels: { push: false, whatsapp: false, email: true }
    },
    {
      id: 'HIGH_VALUE_TX',
      label: 'רכישה חריגה',
      description: 'ביצוע עסקה מעל ₪5,000 או ביטול עסקה גדולה',
      icon: 'payments', // Payment Icon
      color: 'text-purple-600 bg-purple-50',
      channels: { push: true, whatsapp: false, email: false }
    },
    {
      id: 'DAILY_SUMMARY',
      label: 'סיכום יומי',
      description: 'דוח ביצועים, מכירות וחריגות שנשלח בסוף יום',
      icon: 'analytics', // Analytics Icon
      color: 'text-gray-600 bg-gray-50',
      channels: { push: false, whatsapp: false, email: true }
    }
  ]);

  const toggleChannel = (scenarioId: string, channel: keyof NotificationChannelState) => {
    setScenarios(current =>
      current.map(scenario => {
        if (scenario.id === scenarioId) {
          // אם מפעילים Push, נבדוק הרשאות
          if (channel === 'push' && !scenario.channels.push && notificationPermission !== 'granted') {
            Notification.requestPermission().then(setNotificationPermission);
          }

          return {
            ...scenario,
            channels: {
              ...scenario.channels,
              [channel]: !scenario.channels[channel]
            }
          };
        }
        return scenario;
      })
    );
  };

  const saveSettings = () => {
    // כאן תהיה קריאה לשרת לשמירת ההגדרות
    console.log('Saving settings:', scenarios);
    alert('ההגדרות נשמרו בהצלחה');
  };

  return (
    <Layout>
      <div className="mx-auto max-w-4xl p-6">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/notifications" className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-gray-600 transition-colors hover:bg-gray-200">
              <span className="material-symbols-outlined">arrow_forward</span>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">הגדרות התראות מתקדמות</h1>
              <p className="text-gray-500">קבע אילו עדכונים תקבל ובאילו ערוצים</p>
            </div>
          </div>
          <button
            onClick={saveSettings}
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 font-medium text-white shadow-sm transition-all hover:bg-blue-700 active:scale-95"
          >
            <span className="material-symbols-outlined text-[20px]">save</span>
            שמור שינויים
          </button>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden">
          {/* Table Header */}
          <div className="grid grid-cols-12 border-b border-gray-200 bg-gray-50/50 p-4 text-sm font-medium text-gray-500">
            <div className="col-span-5">סוג התראה</div>
            <div className="col-span-7 grid grid-cols-3 gap-4 text-center">
              <div className="flex items-center justify-center gap-2">
                <span className="material-symbols-outlined text-[18px]">notifications_active</span>
                <span>פוש</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <span className="material-symbols-outlined text-[18px]">chat</span>
                <span>וואטסאפ</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <span className="material-symbols-outlined text-[18px]">mail</span>
                <span>אימייל</span>
              </div>
            </div>
          </div>

          {/* Scenarios List */}
          <div className="divide-y divide-gray-100">
            {scenarios.map((scenario) => (
              <div key={scenario.id} className="grid grid-cols-12 items-center p-4 transition-colors hover:bg-gray-50/30">
                {/* Scenario Info */}
                <div className="col-span-5 flex items-start gap-4 pr-2">
                  <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${scenario.color}`}>
                    <span className="material-symbols-outlined">{scenario.icon}</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{scenario.label}</h3>
                    <p className="text-sm text-gray-500 leading-tight mt-1">{scenario.description}</p>
                  </div>
                </div>

                {/* Channels Toggles */}
                <div className="col-span-7 grid grid-cols-3 gap-4">
                  {/* Push Toggle */}
                  <div className="flex justify-center">
                    <button
                      onClick={() => toggleChannel(scenario.id, 'push')}
                      className={`
                        relative h-8 w-14 cursor-pointer rounded-full transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-blue-100
                        ${scenario.channels.push ? 'bg-blue-600 shadow-inner' : 'bg-gray-200'}
                      `}
                    >
                      <span
                        className={`
                          absolute top-1 left-1 h-6 w-6 transform rounded-full bg-white shadow-md transition-transform duration-300
                          ${scenario.channels.push ? 'translate-x-6' : 'translate-x-0'}
                        `}
                      />
                    </button>
                  </div>

                  {/* WhatsApp Toggle */}
                  <div className="flex justify-center">
                    <button
                      onClick={() => toggleChannel(scenario.id, 'whatsapp')}
                      className={`
                        relative h-8 w-14 cursor-pointer rounded-full transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-green-100
                        ${scenario.channels.whatsapp ? 'bg-green-500 shadow-inner' : 'bg-gray-200'}
                      `}
                    >
                      <span
                        className={`
                          absolute top-1 left-1 h-6 w-6 transform rounded-full bg-white shadow-md transition-transform duration-300
                          ${scenario.channels.whatsapp ? 'translate-x-6' : 'translate-x-0'}
                        `}
                      />
                    </button>
                  </div>

                  {/* Email Toggle */}
                  <div className="flex justify-center">
                    <button
                      onClick={() => toggleChannel(scenario.id, 'email')}
                      className={`
                        relative h-8 w-14 cursor-pointer rounded-full transition-all duration-300 ease-in-out focus:outline-none focus:ring-4 focus:ring-gray-100
                        ${scenario.channels.email ? 'bg-indigo-500 shadow-inner' : 'bg-gray-200'}
                      `}
                    >
                      <span
                        className={`
                          absolute top-1 left-1 h-6 w-6 transform rounded-full bg-white shadow-md transition-transform duration-300
                          ${scenario.channels.email ? 'translate-x-6' : 'translate-x-0'}
                        `}
                      />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Global Permission Warning */}
        {notificationPermission !== 'granted' && (
          <div className="mt-6 flex items-center justify-between rounded-xl border border-yellow-200 bg-yellow-50 p-4 text-yellow-800">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined">warning</span>
              <div>
                <p className="font-medium">התראות דפדפן חסומות</p>
                <p className="text-sm">כדי לקבל התראות פוש, עליך לאשר קבלת התראות בדפדפן.</p>
              </div>
            </div>
            <button
              onClick={() => Notification.requestPermission().then(setNotificationPermission)}
              className="rounded-lg bg-yellow-600 px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-yellow-700"
            >
              אפשר התראות
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
