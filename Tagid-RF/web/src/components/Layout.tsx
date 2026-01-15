import { ReactNode } from 'react';
import styled from 'styled-components';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';
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

const ContentWrapper = styled.div`
  display: flex;
  flex: 1;
`;

const Main = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: ${theme.spacing.lg};
  max-width: calc(100% - 240px);
  
  @media (max-width: ${theme.breakpoints.tablet}) {
    max-width: 100%;
    padding: ${theme.spacing.md};
  }
`;

export function Layout({ children, showNav = true }: LayoutProps) {
  return (
    <LayoutContainer>
      {showNav && <TopBar />}
      <ContentWrapper>
        {showNav && <Sidebar />}
        <Main>{children}</Main>
      </ContentWrapper>
    </LayoutContainer>
  );
}
