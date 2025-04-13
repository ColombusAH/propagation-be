import { SimpleGrid, Paper, Text, Title, Group } from '@mantine/core';
import { useAuth } from '../../contexts/AuthContext';

export const Dashboard = () => {
  const { user } = useAuth();

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

      {user?.role === 'admin' && (
        <div style={{ marginTop: '2rem' }}>
          <Title order={3} mb="md">Admin Statistics</Title>
          <SimpleGrid cols={{ base: 1, sm: 2 }}>
            <Paper withBorder p="md">
              <Text fw={500} mb="xs">System Status</Text>
              <Text c="dimmed">All systems operational</Text>
            </Paper>
            <Paper withBorder p="md">
              <Text fw={500} mb="xs">Recent Activities</Text>
              <Text c="dimmed">5 new users registered today</Text>
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