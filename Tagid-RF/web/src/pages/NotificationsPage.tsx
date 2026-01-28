import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useSSE } from '@/hooks/useSSE';

interface NotificationItem {
  id: string;
  type: 'error' | 'warning' | 'info';
  title: string;
  message: string;
  time: string;
  badge: string;
  isRead?: boolean;
}

export function NotificationsPage() {
  const { userRole, token } = useAuth();
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [permissionState, setPermissionState] = useState(Notification.permission);

  // Hook up SSE for real-time updates
  const { status, connect } = useSSE({
    url: '/api/v1/sse/events',
    onTheftAlert: (data) => {
      const isCustomer = userRole === 'CUSTOMER';

      const newNotification: NotificationItem = {
        id: data.alert_id || Date.now().toString(),
        type: isCustomer ? 'warning' : 'error',
        title: isCustomer ? 'תשלום נדרש' : 'התרעת גניבה',
        message: isCustomer
          ? `נראה שיש ברשותך פריט שלא שולם: ${data.product}`
          : `מוצר: ${data.product} | מיקום: ${data.location}`,
        time: new Date().toLocaleTimeString('he-IL'),
        badge: isCustomer ? 'לא שולם' : 'גניבה',
        isRead: false
      };
      setItems(prev => [newNotification, ...prev]);
    }
  });

  // Request permissions on mount
  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission().then(setPermissionState);
    }
  }, []);

  const triggerTest = async () => {
    if (Notification.permission !== 'granted') {
      const result = await Notification.requestPermission();
      setPermissionState(result);
      if (result !== 'granted') return;
    }

    try {
      await fetch('/api/v1/notifications/test-push', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (e) {
      console.error(e);
    }
  };

  // const isStaff = userRole && ['SUPER_ADMIN', 'NETWORK_ADMIN', 'STORE_MANAGER', 'SELLER'].includes(userRole);

  // if (!isStaff) return (
  //   <Layout>
  //     <div className="flex items-center justify-center p-20 text-gray-500">
  //       אין הרשאה לצפייה בדף זה
  //     </div>
  //   </Layout>
  // );

  return (
    <Layout>
      <div className="mx-auto max-w-4xl p-6 space-y-8">

        {/* Header Section */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 to-blue-800 p-8 text-white shadow-xl">
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">התראות פוש</h1>
              <p className="mt-2 text-blue-100 opacity-90">
                ניהול וניטור אירועי אבטחה בזמן אמת
              </p>
              <div className="mt-4 flex items-center gap-2 text-sm">
                <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 bg-black/20 backdrop-blur-sm border border-white/10`}>
                  <span className={`h-2 w-2 rounded-full ${status === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
                  {status === 'connected' ? 'מחובר לשרת' : 'מנותק'}
                </span>

                <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 bg-black/20 backdrop-blur-sm border border-white/10`}>
                  <span className="material-symbols-outlined text-[16px] leading-none">
                    {permissionState === 'granted' ? 'check_circle' : 'unpublished'}
                  </span>
                  {permissionState === 'granted' ? 'התראות פעילות' : 'התראות חסומות'}
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <button
                onClick={triggerTest}
                className="group flex items-center gap-2 rounded-xl bg-white px-5 py-3 font-semibold text-blue-700 shadow-lg transition-all hover:bg-blue-50 active:scale-95"
              >
                <span className="material-symbols-outlined">notifications_active</span>
                <span>שלח פוש לבדיקה</span>
              </button>

              <Link
                to="/notification-settings"
                className="flex items-center justify-center gap-2 rounded-xl bg-white/10 px-5 py-3 font-medium text-white backdrop-blur-md transition-all hover:bg-white/20"
              >
                <span className="material-symbols-outlined">settings</span>
                <span>הגדרות</span>
              </Link>
            </div>
          </div>

          {/* Decorative background circles */}
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-blue-500/30 blur-3xl" />
          <div className="absolute -left-20 -bottom-20 h-64 w-64 rounded-full bg-purple-500/30 blur-3xl" />
        </div>

        {/* Notifications List */}
        <div className="space-y-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50 py-20 text-center">
              <div className="mb-4 rounded-full bg-white p-4 shadow-sm ring-1 ring-gray-200">
                <span className="material-symbols-outlined text-4xl text-gray-400">notifications_off</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900">אין התראות חדשות</h3>
              <p className="mt-1 text-gray-500">לחץ על הכפתור למעלה כדי לבדוק שליחת פוש</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {items.map((item) => (
                <div
                  key={item.id}
                  className={`
                    relative overflow-hidden rounded-xl border border-gray-100 bg-white p-5 shadow-sm transition-all hover:shadow-md
                    ${item.type === 'error' ? 'border-r-4 border-r-red-500' : 'border-r-4 border-r-blue-500'}
                  `}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`
                        flex h-10 w-10 shrink-0 items-center justify-center rounded-full 
                        ${item.type === 'error' ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'}
                      `}>
                        <span className="material-symbols-outlined">
                          {item.type === 'error' ? 'report' : 'info'}
                        </span>
                      </div>

                      <div>
                        <h3 className="font-semibold text-gray-900">{item.title}</h3>
                        <p className="mt-1 text-gray-600">{item.message}</p>

                        <div className="mt-3 flex items-center gap-2">
                          <span className={`
                            inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset
                            ${item.type === 'error'
                              ? 'bg-red-50 text-red-700 ring-red-600/10'
                              : 'bg-blue-50 text-blue-700 ring-blue-700/10'}
                          `}>
                            {item.badge}
                          </span>
                        </div>
                      </div>
                    </div>

                    <span className="text-xs font-medium text-gray-400">{item.time}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
