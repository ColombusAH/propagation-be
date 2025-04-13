import { SimpleGrid, Paper, Text, Title, Group, Button } from '@mantine/core';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, Link } from '@tanstack/react-router';

export const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const navigateToSchedules = () => {
    console.log('Navigating to schedules');
    navigate({ to: '/schedules' });
  };

  return (
    <>
      <Title order={2} mb="md">Dashboard</Title>
      
      <Text mb="xl">
        Welcome back, {user?.name}! Here's what's happening today.
      </Text>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }}>
        <DashboardCard title="Users" value="152" />
        <DashboardCard title="Revenue" value="$10,430" />
        <DashboardCard title="Tasks" value="25/48" />
        <DashboardCard title="Projects" value="12" />
      </SimpleGrid>

      {(user?.role === 'ADMIN' || user?.role === 'OWNER') && (
        <div style={{ marginTop: '2rem' }}>
          <Title order={3} mb="md">ניהול מערכת</Title>
          <SimpleGrid cols={{ base: 1, sm: 2 }}>
            <Paper withBorder p="md">
              <Text fw={500} mb="xs">לוחות זמנים</Text>
              <Text c="dimmed" mb="md">נהל את לוחות הזמנים של העובדים</Text>
              <Link to="/schedules">
                <Button variant="light">צפה בלוחות הזמנים</Button>
              </Link>
            </Paper>
            <Paper withBorder p="md">
              <Text fw={500} mb="xs">סטטיסטיקות מערכת</Text>
              <Text c="dimmed">כל המערכות פעילות</Text>
            </Paper>
          </SimpleGrid>
        </div>
      )}
    </>
  );
};

interface DashboardCardProps {
  title: string;
  value: string;
}

const DashboardCard = ({ title, value }: DashboardCardProps) => {
  return (
    <Paper withBorder p="md" radius="md">
      <Group justify="space-between" mb="xs">
        <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
          {title}
        </Text>
      </Group>

      <Group align="flex-end" gap="xs">
        <Text fz="xl" fw={700}>{value}</Text>
      </Group>

      <Text fz="xs" c="dimmed" mt="md">
        <Text component="span" c={value.includes('-') ? 'red' : 'teal'} fw={700}>
          {value.includes('-') ? value : `+${Math.floor(Math.random() * 20) + 1}%`}
        </Text>{' '}
        from last month
      </Text>
    </Paper>
  );
}; 