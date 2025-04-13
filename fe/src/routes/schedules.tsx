import { createFileRoute } from '@tanstack/react-router';
import { AppLayout } from '../components/Layout/AppLayout';
import { SchedulesList } from '../components/Schedules/SchedulesList';

export const Route = createFileRoute('/schedules')({
  component: SchedulesRoute,
});

function SchedulesRoute() {
  console.log('Schedules Route rendered');
  return (
    <AppLayout>
      <SchedulesList />
    </AppLayout>
  );
} 