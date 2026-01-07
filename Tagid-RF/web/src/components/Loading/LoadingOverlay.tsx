import styled from 'styled-components';
import { Spinner } from './Spinner';

interface LoadingOverlayProps {
    message?: string;
    fullScreen?: boolean;
}

const Overlay = styled.div<{ $fullScreen: boolean }>`
  position: ${props => props.$fullScreen ? 'fixed' : 'absolute'};
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  z-index: ${props => props.$fullScreen ? 9999 : 10};
  gap: 1rem;
`;

const Message = styled.p`
  font-size: 1rem;
  color: #4a5568;
  margin: 0;
  font-weight: 500;
`;

/**
 * LoadingOverlay - Full-screen or container loading overlay
 * 
 * Shows a loading spinner with optional message over content.
 * Can be used for full-screen loading or within a specific container.
 * 
 * @param message - Optional loading message to display
 * @param fullScreen - If true, covers entire viewport (default: false)
 * 
 * @example
 * ```tsx
 * // Full-screen loading
 * <LoadingOverlay message="טוען נתונים..." fullScreen />
 * 
 * // Container loading (requires parent with position: relative)
 * <div style={{ position: 'relative', height: '400px' }}>
 *   <LoadingOverlay message="טוען..." />
 * </div>
 * ```
 */
export function LoadingOverlay({ message, fullScreen = false }: LoadingOverlayProps) {
    return (
        <Overlay $fullScreen={fullScreen}>
            <Spinner size="lg" />
            {message && <Message>{message}</Message>}
        </Overlay>
    );
}
