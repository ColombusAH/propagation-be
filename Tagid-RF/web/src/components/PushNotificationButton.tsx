import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { pushService } from '../services/pushService';
import { useToast } from '../hooks/useToast';
import { useAuth } from '../contexts/AuthContext';

const NotificationButton = styled.button<{ $isSubscribed: boolean }>`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  padding: 10px 15px;
  background-color: ${props => props.$isSubscribed ? '#e0e0e0' : '#007bff'};
  color: ${props => props.$isSubscribed ? '#666' : 'white'};
  border: none;
  border-radius: 5px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  transition: all 0.3s ease;

  &:hover {
    background-color: ${props => props.$isSubscribed ? '#d5d5d5' : '#0056b3'};
  }
`;

export const PushNotificationButton: React.FC = () => {
    const { userId, userRole } = useAuth();
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [loading, setLoading] = useState(false);
    const toast = useToast();

    useEffect(() => {
        // Sync subscription state on mount
        const syncSubscription = async () => {
            if ('serviceWorker' in navigator && 'PushManager' in window) {
                try {
                    const registration = await navigator.serviceWorker.ready;
                    const subscription = await registration.pushManager.getSubscription();

                    if (subscription) {
                        try {
                            // Attempt to re-sync with backend to ensure userId is linked
                            // We can't easily get the 'registration' object inside here without waiting
                            // so we assume if we have a subscription, we try to send it to backend
                            // ACTUALLY: We should just call subscribeUser again, it handles the backend call.
                            // But we need the registration object.
                            await pushService.subscribeUser(registration, userId || undefined);
                            setIsSubscribed(true);
                        } catch (err) {
                            console.error('Backend sync failed, resetting subscription:', err);
                            // If backend sync failed (e.g. 403 or server error), 
                            // we should probably unsubscribe locally so the user can try again cleanly
                            await pushService.unsubscribeUser();
                            setIsSubscribed(false);
                        }
                    }
                } catch (e) {
                    console.error('Error checking subscription:', e);
                }
            }
        };

        if (userId && userRole !== 'CUSTOMER') { // Only sync if we have a user and it's not a customer
            syncSubscription();
        }
    }, [userId, userRole]); // Re-run if userId or role changes

    const handleSubscribe = async () => {
        setLoading(true);
        try {
            const registration = await pushService.registerServiceWorker();
            if (registration) {
                await pushService.subscribeUser(registration, userId || undefined);
                setIsSubscribed(true);
                toast.success('Successfully enabled notifications!');
            }
        } catch (error) {
            console.error(error);
            toast.error('Failed to enable notifications. Please try again.');
            // Force unsubscribe locally if it failed halfway
            await pushService.unsubscribeUser();
            setIsSubscribed(false);
        } finally {
            setLoading(false);
        }
    };

    if (isSubscribed || userRole === 'CUSTOMER') return null; // Hide if already subscribed or user is customer

    return (
        <NotificationButton onClick={handleSubscribe} $isSubscribed={isSubscribed} disabled={loading}>
            {loading ? 'Enabling...' : '🔔 Enable Notifications'}
        </NotificationButton>
    );
};
