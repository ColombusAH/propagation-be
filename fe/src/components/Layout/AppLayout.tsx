import { AppShell, Burger, Button, Group, Loader, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import type { ReactNode } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from '@tanstack/react-router';

interface AppLayoutProps {
  children: ReactNode;
}

export const AppLayout = ({ children }: AppLayoutProps) => {
  const [opened, { toggle }] = useDisclosure();
  const { user, isLoading, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate({ to: '/' });
  };

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', display: 'flex', justifyContent: 'center' }}>
        <Loader size="xl" />
      </div>
    );
  }

  if (!user) {
    // If not logged in, we should redirect to login page
    // This could happen if the user logs out or the session expires
    navigate({ to: '/', replace: true });
    return null;
  }

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Text fw={700}>Admin Dashboard</Text>
          </Group>
          <Group>
            <Text>Welcome, {user.name}</Text>
            <Button variant="light" onClick={handleLogout}>Logout</Button>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Text fw={500} mb="md">Main Navigation</Text>
        {/* Navigation links based on user role */}
        {user.role === 'admin' && (
          <>
            <Button variant="subtle" fullWidth mb="xs" onClick={() => navigate({ to: '/' })}>
              Admin Dashboard
            </Button>
            <Button variant="subtle" fullWidth mb="xs" onClick={() => navigate({ to: '/' })}>
              Manage Users
            </Button>
          </>
        )}
        <Button variant="subtle" fullWidth mb="xs" onClick={() => navigate({ to: '/' })}>
          Dashboard
        </Button>
        <Button variant="subtle" fullWidth mb="xs" onClick={() => navigate({ to: '/' })}>
          My Profile
        </Button>
      </AppShell.Navbar>

      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  );
}; 