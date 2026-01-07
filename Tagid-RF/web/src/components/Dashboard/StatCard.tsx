import styled from 'styled-components';
import { theme } from '@/styles/theme';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const Card = styled.div`
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.xl};
  transition: all ${theme.transitions.base};
  
  &:hover {
    border-color: ${theme.colors.gray[300]};
    box-shadow: ${theme.shadows.sm};
  }
`;

const Title = styled.h3`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
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
  font-weight: ${theme.typography.fontWeight.medium};
  
  &::before {
    content: '${props => props.$isPositive ? '↑' : '↓'}';
  }
`;

/**
 * StatCard - Minimal dashboard statistic card
 * 
 * Clean white design with subtle borders
 */
export function StatCard({ title, value, trend }: StatCardProps) {
  return (
    <Card>
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
