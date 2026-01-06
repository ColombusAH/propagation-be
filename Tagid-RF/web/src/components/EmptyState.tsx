import { ReactNode } from 'react';
import styled from 'styled-components';
import { theme } from '@/styles/theme';

interface EmptyStateProps {
  icon?: string;
  title: string;
  message?: string;
  action?: ReactNode;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.xxl};
  text-align: center;
  min-height: 300px;
`;

const Icon = styled.div`
  font-size: 64px;
  margin-bottom: ${theme.spacing.lg};
  opacity: 0.5;
`;

const Title = styled.h2`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin-bottom: ${theme.spacing.sm};
`;

const Message = styled.p`
  font-size: ${theme.typography.fontSize.base};
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.lg};
  max-width: 400px;
`;

const ActionContainer = styled.div`
  margin-top: ${theme.spacing.md};
`;

export function EmptyState({ icon, title, message, action }: EmptyStateProps) {
  return (
    <Container>
      {icon && <Icon>{icon}</Icon>}
      <Title>{title}</Title>
      {message && <Message>{message}</Message>}
      {action && <ActionContainer>{action}</ActionContainer>}
    </Container>
  );
}

