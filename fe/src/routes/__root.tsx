import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { createTheme, MantineProvider } from '@mantine/core';
import { AuthProvider } from '../contexts/AuthContext';

const theme = createTheme({
  /** Put your mantine theme override here */
});


export const Route = createRootRoute({
  component: () => (
    <MantineProvider theme={theme}>
      <AuthProvider>
        <Outlet />
        <TanStackRouterDevtools />
      </AuthProvider>
    </MantineProvider>
  ),
})
