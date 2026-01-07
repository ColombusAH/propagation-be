import styled, { keyframes } from 'styled-components';

interface SkeletonProps {
    width?: string | number;
    height?: string | number;
    variant?: 'text' | 'rectangular' | 'circular';
    className?: string;
}

const shimmer = keyframes`
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
`;

const SkeletonBase = styled.div<{
    $width: string;
    $height: string;
    $variant: 'text' | 'rectangular' | 'circular';
}>`
  display: inline-block;
  width: ${props => props.$width};
  height: ${props => props.$height};
  background: linear-gradient(
    90deg,
    #f0f0f0 0px,
    #f8f8f8 40px,
    #f0f0f0 80px
  );
  background-size: 600px;
  animation: ${shimmer} 1.5s ease-in-out infinite;
  border-radius: ${props => {
        switch (props.$variant) {
            case 'circular': return '50%';
            case 'text': return '4px';
            default: return '8px';
        }
    }};
`;

/**
 * Skeleton - Placeholder loading component
 * 
 * Shows an animated placeholder while content is loading.
 * Useful for lists, cards, and other content that takes time to load.
 * 
 * @param width - Width of the skeleton (default: '100%')
 * @param height - Height of the skeleton (default: '20px')
 * @param variant - Shape variant: 'text', 'rectangular', 'circular'
 * 
 * @example
 * ```tsx
 * // Text line skeleton
 * <Skeleton variant="text" width="200px" />
 * 
 * // Avatar skeleton
 * <Skeleton variant="circular" width="40px" height="40px" />
 * 
 * // Card skeleton
 * <Skeleton variant="rectangular" width="100%" height="120px" />
 * ```
 */
export function Skeleton({
    width = '100%',
    height = '20px',
    variant = 'text',
    className,
}: SkeletonProps) {
    const widthStr = typeof width === 'number' ? `${width}px` : width;
    const heightStr = typeof height === 'number' ? `${height}px` : height;

    return (
        <SkeletonBase
            $width={widthStr}
            $height={heightStr}
            $variant={variant}
            className={className}
        />
    );
}
