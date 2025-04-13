import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider, createRouter } from '@tanstack/react-router'
import { GoogleOAuthProvider } from '@react-oauth/google'
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dropzone/styles.css';
// Import the generated route tree.
import { routeTree } from './routeTree.gen'
import { env } from './config/env'

import './styles.css'
import reportWebVitals from './reportWebVitals.ts'

// Create a new router instance
const router = createRouter({
  routeTree,
  context: {},
  defaultPreload: 'intent',
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,
})

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

// Render the app
const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)

  // Check if Google Client ID is available before rendering the provider
  if (!env.GOOGLE_CLIENT_ID) {
    root.render(
      <StrictMode>
        <div>Error: Google Client ID is not configured. Please set VITE_GOOGLE_CLIENT_ID in your .env file.</div>
      </StrictMode>
    );
  } else {
    root.render(
      <StrictMode>
        <GoogleOAuthProvider clientId={env.GOOGLE_CLIENT_ID}> 
          <RouterProvider router={router} />
        </GoogleOAuthProvider>
      </StrictMode>,
    )
  }
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
