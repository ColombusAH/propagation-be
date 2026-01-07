import styled from 'styled-components';
import { theme } from '@/styles/theme';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: string;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    gradient?: string;
}

const Card = styled.div<{ $gradient?: string }>`
  background: ${props => props.$gradient || theme.colors.surface};
  border-radius: ${theme.borderRadius.xl};
  padding: ${theme.spacing.lg};
  box-shadow: ${theme.shadows.md};
  transition: all ${theme.transitions.base};
  position: relative;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: ${theme.shadows.xl};
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: ${props => props.$gradient ? 'rgba(255, 255, 255, 0.1)' : theme.colors.gray[50]};
    border-radius: 50%;
    transform: translate(30%, -30%);
  }
`;

const IconWrapper = styled.div`
  font-size: ${theme.typography.fontSize['3xl']};
  margin-bottom: ${theme.spacing.sm};
  position: relative;
  z-index: 1;
`;

const Title = styled.h3`
  font-size: ${theme.typography.fontSize.sm};
  font-weight: ${theme.typography.fontWeight.medium};
  color: ${theme.colors.textSecondary};
  margin: 0 0 ${theme.spacing.xs} 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Value = styled.div`
  font-size: ${theme.typography.fontSize['3xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.text};
  margin-bottom: ${theme.spacing.xs};
`;

const Trend = styled.div<{ $isPositive: boolean }>`
  font-size: ${theme.typography.fontSize.sm};
  color: ${props => props.$isPositive ? theme.colors.success : theme.colors.error};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};
  
  &::before {
    content: '${props => props.$isPositive ? '↑' : '↓'}';
  }
`;

/**
 * StatCard - Dashboard statistic card
 * 
 * Displays a key metric with optional trend indicator
 */
export function StatCard({ title, value, icon, trend, gradient }: StatCardProps) {
    return (
        <Card $gradient={gradient}>
            <IconWrapper>{icon}</IconWrapper>
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
