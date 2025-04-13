import { createFileRoute } from '@tanstack/react-router';
import { AppLayout } from '../components/Layout/AppLayout';
import { NewSchedule } from '../components/Schedules/NewSchedule';

export const Route = createFileRoute('/createschedules')({
  component: NewScheduleRoute,
});

function NewScheduleRoute() {
  console.log('New Schedule Route rendered');
  return (
    <AppLayout>
      <NewSchedule />
    </AppLayout>
  );
} 