import { useState } from 'react';
import { SimpleGrid, Paper, Text, Title, Button, Group } from '@mantine/core';
import { useNavigate, Link } from '@tanstack/react-router';
import { useAuth } from '../../contexts/AuthContext';

// מודל פשוט ללוח זמנים
interface Schedule {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  status: string;
}

export const SchedulesList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // מידע לדוגמה - בפרויקט אמיתי זה יגיע מקריאת API
  const [schedules] = useState<Schedule[]>([
    {
      id: '1',
      name: 'שבוע 1 - אוגוסט',
      startDate: '2023-08-01',
      endDate: '2023-08-07',
      status: 'PUBLISHED'
    },
    {
      id: '2',
      name: 'שבוע 2 - אוגוסט',
      startDate: '2023-08-08',
      endDate: '2023-08-14',
      status: 'DRAFT'
    },
    {
      id: '3',
      name: 'שבוע 3 - אוגוסט',
      startDate: '2023-08-15',
      endDate: '2023-08-21',
      status: 'CREATED'
    }
  ]);

  // פונקציה לניווט לדף יצירת לוח זמנים חדש
  const handleCreateNew = () => {
    console.log('Creating new schedule, navigating to /schedules/new');
    navigate({ to: '/createschedules' });
  };

  return (
    <>
      <Group justify="space-between" mb="xl">
        <Title order={2}>לוחות זמנים</Title>
        <Link to="/createschedules">
          <Button>+ צור לוח זמנים חדש</Button>
        </Link>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }}>
        {schedules.map((schedule) => (
          <ScheduleCard key={schedule.id} schedule={schedule} />
        ))}
      </SimpleGrid>
    </>
  );
};

interface ScheduleCardProps {
  schedule: Schedule;
}

const ScheduleCard = ({ schedule }: ScheduleCardProps) => {
  // פונקציה שמחזירה צבע על פי סטטוס
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PUBLISHED': return 'green';
      case 'DRAFT': return 'gray';
      case 'CREATED': return 'blue';
      default: return 'gray';
    }
  };

  // פונקציה שמחזירה תרגום לסטטוס
  const getStatusText = (status: string) => {
    switch (status) {
      case 'PUBLISHED': return 'פורסם';
      case 'DRAFT': return 'טיוטה';
      case 'CREATED': return 'נוצר';
      default: return status;
    }
  };
  
  return (
    <Paper withBorder p="md" radius="md">
      <Group justify="space-between" mb="xs">
        <Text fw={700} size="lg">{schedule.name}</Text>
      </Group>

      <Text c="dimmed" size="sm" mb="md">
        {new Date(schedule.startDate).toLocaleDateString('he-IL')} - {new Date(schedule.endDate).toLocaleDateString('he-IL')}
      </Text>

      <Group>
        <Text size="sm" c={getStatusColor(schedule.status)} fw={500}>
          {getStatusText(schedule.status)}
        </Text>
      </Group>
    </Paper>
  );
}; 