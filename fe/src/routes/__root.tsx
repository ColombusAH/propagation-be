import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { createTheme, MantineProvider } from '@mantine/core';

const theme = createTheme({
  /** Put your mantine theme override here */
});


export const Route = createRootRoute({
  component: () => (
    <MantineProvider theme={theme}>
      <Outlet />
      <TanStackRouterDevtools />
    </MantineProvider>
  ),
})
