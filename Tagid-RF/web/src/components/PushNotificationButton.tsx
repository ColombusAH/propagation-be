import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { pushService } from '../services/pushService';
import { useToast } from '../hooks/useToast';

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
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [loading, setLoading] = useState(false);
    const toast = useToast();

    useEffect(() => {
        // Check if already subscribed
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            navigator.serviceWorker.ready.then(registration => {
                registration.pushManager.getSubscription().then(subscription => {
                    if (subscription) {
                        setIsSubscribed(true);
                    }
                });
            });
        }
    }, []);

    const handleSubscribe = async () => {
        setLoading(true);
        try {
            const registration = await pushService.registerServiceWorker();
            if (registration) {
                await pushService.subscribeUser(registration);
                setIsSubscribed(true);
                toast.success('Successfully enabled notifications!');
            }
        } catch (error) {
            console.error(error);
            toast.error('Failed to enable notifications. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (isSubscribed) return null; // Hide if already subscribed

    return (
        <NotificationButton onClick={handleSubscribe} $isSubscribed={isSubscribed} disabled={loading}>
            {loading ? 'Enabling...' : '🔔 Enable Notifications'}
        </NotificationButton>
    );
};
