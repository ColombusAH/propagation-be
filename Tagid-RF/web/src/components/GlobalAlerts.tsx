import { useWebSocket } from '@/hooks/useWebSocket';
import { useToast } from '@/hooks/useToast';
import { useTranslation } from '@/hooks/useTranslation';

interface TheftAlertData {
    alert_id: string;
    tag_epc: string;
    product: string;
    location?: string;
    timestamp: string;
}

export function GlobalAlerts() {
    const toast = useToast();
    const { t } = useTranslation();

    useWebSocket({
        url: '/ws/rfid',
        onMessage: (message) => {
            if (message.type === 'theft_alert') {
                const data = message.data as TheftAlertData;
                console.log('🚨 Theft Alert received:', data);

                toast.error(`${t('alerts.theftDetected')}! ${data.product} (EPC: ${data.tag_epc})`, {
                    duration: 10000 // Show for 10 seconds
                });

                // You could also play a sound here
                try {
                    const audio = new Audio('/alert.mp3'); // Assuming file exists or fails silently
                    audio.play().catch(() => { });
                } catch (e) {
                    // Ignore audio errors
                }
            }
        }
    });

    return null; // Headless component
}
