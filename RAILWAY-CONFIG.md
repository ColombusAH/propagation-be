# Railway Configuration for Private Networking

## Service Variables Setup

To ensure proper communication between frontend and backend services over Railway's private network, set up these service variables:

### For the Frontend Service (`anybotfe`)

Set these variables in the Railway dashboard for the frontend service:

1. `RAILWAY_SERVICE_ANYBOTBE_INTERNAL_URL` = `http://anybotbe:8002`
   - This tells the frontend how to connect to the backend service

2. `API_URL` = `http://anybotbe:8002` (backup)
   - Used as a fallback if the other connection methods fail

### For the Backend Service (`anybotbe`)

1. `PORT` = `8002`
   - Ensures the backend is listening on the expected port

2. `RAILWAY_HEALTHCHECK_PATH` = `/`
   - Tells Railway which path to check for service health

## Private Networking Notes

1. Railway's private networking is IPv6-only.
2. Services can communicate using:
   - Simple service names: `anybotbe:8002`
   - Full internal DNS: `anybotbe.railway.internal:8002`
   - IPv6 addresses when known

3. The backend is configured to listen on all interfaces (`0.0.0.0`) which binds to both IPv4 and IPv6.

4. Private networking is not available during build phase, only at runtime.

## Troubleshooting

If services cannot communicate:

1. Check the logs to see what connection attempts were made
2. Verify the service variables are set correctly
3. Try restarting both services
4. Ensure no firewall rules are blocking the communication

## Health Check URLs

The backend provides these health endpoints:
- `/` - Root endpoint for basic health checks
- `/health` - Detailed health check 
- `/healthz` - Simple health check for internal services 