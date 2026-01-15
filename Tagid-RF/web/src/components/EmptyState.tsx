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
  padding: ${theme.spacing['3xl']} ${theme.spacing.xl};
  text-align: center;
  min-height: 280px;
  background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.lg};
`;

const IconWrapper = styled.div`
  margin-bottom: ${theme.spacing.lg};
  color: ${theme.colors.gray[500]};
  opacity: 0.8;
`;

const Title = styled.h2`
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.semibold};
  color: ${theme.colors.text};
  margin-bottom: ${theme.spacing.sm};
`;

const Message = styled.p`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.textSecondary};
  margin-bottom: ${theme.spacing.lg};
  max-width: 360px;
  line-height: ${theme.typography.lineHeight.relaxed};
`;

const ActionContainer = styled.div`
  margin-top: ${theme.spacing.sm};
`;

export function EmptyState({ icon, title, message, action }: EmptyStateProps) {
  return (
    <Container>
      {icon && (
        <IconWrapper>
          <span className="material-symbols-outlined" style={{ fontSize: 56 }}>{icon}</span>
        </IconWrapper>
      )}
      <Title>{title}</Title>
      {message && <Message>{message}</Message>}
      {action && <ActionContainer>{action}</ActionContainer>}
    </Container>
  );
}
