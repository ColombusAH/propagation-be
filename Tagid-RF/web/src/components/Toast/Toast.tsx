import { useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { Toast as ToastType } from './types';

interface ToastProps {
    toast: ToastType;
    onClose: () => void;
}

const slideIn = keyframes`
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

const slideOut = keyframes`
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(400px);
    opacity: 0;
  }
`;

const ToastWrapper = styled.div<{ $type: ToastType['type'] }>`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  margin-bottom: 0.75rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 500px;
  animation: ${slideIn} 0.3s ease-out;
  background: ${props => {
        switch (props.$type) {
            case 'success': return '#10b981';
            case 'error': return '#ef4444';
            case 'warning': return '#f59e0b';
            case 'info': return '#3b82f6';
            default: return '#6b7280';
        }
    }};
  color: white;
  cursor: pointer;
  
  &:hover {
    opacity: 0.9;
  }
`;

const Icon = styled.span`
  font-size: 1.25rem;
  flex-shrink: 0;
`;

const Message = styled.p`
  margin: 0;
  flex: 1;
  font-size: 0.9375rem;
  line-height: 1.4;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 1;
  }
`;

const getIcon = (type: ToastType['type']): string => {
    switch (type) {
        case 'success': return '✓';
        case 'error': return '✕';
        case 'warning': return '⚠';
        case 'info': return 'ℹ';
        default: return '•';
    }
};

/**
 * Toast - Individual toast notification component
 * 
 * Displays a single toast notification with auto-dismiss.
 */
export function Toast({ toast, onClose }: ToastProps) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, toast.duration || 3000);

        return () => clearTimeout(timer);
    }, [toast.duration, onClose]);

    return (
        <ToastWrapper $type={toast.type} onClick={onClose}>
            <Icon>{getIcon(toast.type)}</Icon>
            <Message>{toast.message}</Message>
            <CloseButton onClick={onClose} aria-label="Close">
                ×
            </CloseButton>
        </ToastWrapper>
    );
}
