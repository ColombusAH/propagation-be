import { Title, Paper, Button, Group, TextInput } from '@mantine/core';
import { useNavigate } from '@tanstack/react-router';

export const NewSchedule = () => {
  const navigate = useNavigate();
  
  // פונקציה לחזרה לדף לוחות הזמנים
  const handleBack = () => {
    navigate({ to: '/schedules' });
  };

  console.log('new schedule');

  return (
    <>
      <Group justify="space-between" mb="xl">
        <Title order={2}>צור לוח זמנים חדש</Title>
      </Group>

      <Paper withBorder p="xl" radius="md">
        <TextInput
          label="שם לוח הזמנים"
          placeholder="הכנס שם ללוח הזמנים"
          mb="md"
          required
        />
        
        <Group justify="flex-end" mt="xl">
          <Button variant="default" onClick={handleBack}>ביטול</Button>
          <Button>שמור</Button>
        </Group>
      </Paper>
    </>
  );
}; 