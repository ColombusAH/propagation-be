import styled from 'styled-components';
import { theme } from '@/styles/theme';

interface StatCardProps {
  title: string;
  value: string | number;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  accentColor?: string;
}

const Card = styled.div<{ $accentColor?: string }>`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-left: 4px solid ${props => props.$accentColor || theme.colors.primary};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  transition: all ${theme.transitions.base};
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.$accentColor || theme.colors.primary};
    opacity: 0.02;
    border-radius: ${theme.borderRadius.lg};
    pointer-events: none;
  }
  
  &:hover {
    border-left-width: 6px;
    box-shadow: ${theme.shadows.md};
    transform: translateY(-2px);
  }
`;

const Title = styled.h3`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.textSecondary};
  margin: 0 0 ${theme.spacing.md} 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Value = styled.div`
  font-size: ${theme.typography.fontSize['4xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin-bottom: ${theme.spacing.sm};
`;

const Trend = styled.div<{ $isPositive: boolean }>`
  font-size: ${theme.typography.fontSize.sm};
  color: ${props => props.$isPositive ? theme.colors.success : theme.colors.error};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};
  font-weight: ${theme.typography.fontWeight.semibold};
  
  &::before {
    content: '${props => props.$isPositive ? '↑' : '↓'}';
    font-size: ${theme.typography.fontSize.lg};
  }
`;

/**
 * StatCard - Dashboard statistic card with subtle color accent
 */
export function StatCard({ title, value, trend, accentColor }: StatCardProps) {
  return (
    <Card $accentColor={accentColor}>
      <Title>{title}</Title>
      <Value>{value}</Value>
      {trend && (
        <Trend $isPositive={trend.isPositive}>
          {Math.abs(trend.value)}% מהשבוע שעבר
        </Trend>
      )}
    </Card>
  );
}
