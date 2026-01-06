import { ReactNode } from 'react';
import styled from 'styled-components';
import { TopBar } from './TopBar';
import { theme } from '@/styles/theme';

interface LayoutProps {
  children: ReactNode;
  showNav?: boolean;
}

const LayoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${theme.colors.background};
`;

const Main = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-bottom: ${theme.spacing.md};
`;

export function Layout({ children, showNav = true }: LayoutProps) {
  return (
    <LayoutContainer>
      {showNav && <TopBar />}
      <Main>{children}</Main>
    </LayoutContainer>
  );
}

