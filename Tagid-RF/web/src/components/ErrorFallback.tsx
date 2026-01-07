import { ErrorInfo } from 'react';
import styled from 'styled-components';

interface ErrorFallbackProps {
    error: Error | null;
    errorInfo: ErrorInfo | null;
    onReset?: () => void;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
`;

const ErrorCard = styled.div`
  background: white;
  color: #333;
  border-radius: 12px;
  padding: 3rem;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const ErrorIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 1rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #e53e3e;
`;

const Message = styled.p`
  font-size: 1.1rem;
  margin-bottom: 2rem;
  color: #666;
  line-height: 1.6;
`;

const ErrorDetails = styled.details`
  text-align: left;
  margin: 2rem 0;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
`;

const Summary = styled.summary`
  cursor: pointer;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
  
  &:hover {
    color: #2d3748;
  }
`;

const ErrorText = styled.pre`
  font-size: 0.875rem;
  color: #e53e3e;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 0.75rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  ${props => props.variant === 'primary' ? `
    background: #667eea;
    color: white;
    
    &:hover {
      background: #5568d3;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
  ` : `
    background: #e2e8f0;
    color: #4a5568;
    
    &:hover {
      background: #cbd5e0;
    }
  `}
  
  &:active {
    transform: translateY(0);
  }
`;

/**
 * ErrorFallback - UI shown when ErrorBoundary catches an error
 * 
 * Displays a user-friendly error message with options to:
 * - Reload the page
 * - Go back to home
 * - View error details (for developers)
 */
export function ErrorFallback({ error, errorInfo, onReset }: ErrorFallbackProps) {
    const handleReload = (): void => {
        window.location.reload();
    };

    const handleGoHome = (): void => {
        window.location.href = '/';
    };

    const handleReset = (): void => {
        if (onReset) {
            onReset();
        } else {
            handleReload();
        }
    };

    return (
        <Container>
            <ErrorCard>
                <ErrorIcon>⚠️</ErrorIcon>
                <Title>אופס! משהו השתבש</Title>
                <Message>
                    מצטערים, אירעה שגיאה בלתי צפויה.
                    <br />
                    אנחנו עובדים על לתקן את זה.
                </Message>

                {/* Error details for developers */}
                {(error || errorInfo) && (
                    <ErrorDetails>
                        <Summary>פרטים טכניים (למפתחים)</Summary>
                        {error && (
                            <div>
                                <strong>Error:</strong>
                                <ErrorText>{error.toString()}</ErrorText>
                            </div>
                        )}
                        {errorInfo && errorInfo.componentStack && (
                            <div style={{ marginTop: '1rem' }}>
                                <strong>Component Stack:</strong>
                                <ErrorText>{errorInfo.componentStack}</ErrorText>
                            </div>
                        )}
                    </ErrorDetails>
                )}

                <ButtonGroup>
                    <Button variant="primary" onClick={handleReset}>
                        נסה שוב
                    </Button>
                    <Button variant="secondary" onClick={handleGoHome}>
                        חזור לדף הבית
                    </Button>
                    <Button variant="secondary" onClick={handleReload}>
                        טען מחדש את הדף
                    </Button>
                </ButtonGroup>
            </ErrorCard>
        </Container>
    );
}
