import { createFileRoute } from '@tanstack/react-router'
import { Dashboard } from '../components/Dashboard/Dashboard'
import { AppLayout } from '../components/Layout/AppLayout'
import { LoginPage } from '../components/Auth/LoginPage'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/')({
  component: HomeRoute,
})

function HomeRoute() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  );
}
