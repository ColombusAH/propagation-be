import styled, { keyframes } from 'styled-components';

interface SpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    color?: string;
}

const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerContainer = styled.div<{ $size: 'sm' | 'md' | 'lg'; $color: string }>`
  display: inline-block;
  width: ${props => {
        switch (props.$size) {
            case 'sm': return '20px';
            case 'lg': return '48px';
            default: return '32px';
        }
    }};
  height: ${props => {
        switch (props.$size) {
            case 'sm': return '20px';
            case 'lg': return '48px';
            default: return '32px';
        }
    }};

  &::after {
    content: '';
    display: block;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: ${props => props.$size === 'sm' ? '2px' : '3px'} solid ${props => props.$color};
    border-color: ${props => props.$color} transparent ${props => props.$color} transparent;
    animation: ${spin} 1.2s linear infinite;
  }
`;

/**
 * Spinner - Animated loading spinner
 * 
 * A simple, customizable loading spinner for indicating loading states.
 * 
 * @param size - Size of the spinner: 'sm' (20px), 'md' (32px), 'lg' (48px)
 * @param color - Color of the spinner (default: theme primary color)
 * 
 * @example
 * ```tsx
 * // Small spinner
 * <Spinner size="sm" />
 * 
 * // Large spinner with custom color
 * <Spinner size="lg" color="#667eea" />
 * ```
 */
export function Spinner({ size = 'md', color = '#667eea' }: SpinnerProps) {
    return <SpinnerContainer $size={size} $color={color} />;
}
