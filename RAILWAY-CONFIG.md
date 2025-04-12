# Railway Configuration for Private Networking

## Important Findings

From our testing, we've discovered:

1. **DNS Resolution Works**: Railway correctly resolves `anybotbe.railway.internal` to an IPv6 address
2. **Connection Issues**: Despite DNS resolution, direct connections between services are not working properly
3. **IPv6 Address Changes**: The IPv6 address may change between deployments

## Service Variables Setup

To ensure proper communication between frontend and backend services over Railway's private network:

### For the Frontend Service (`anybotfe`)

1. **Service Variables to Add**:
   - `RAILWAY_SERVICE_ANYBOTBE_INTERNAL_URL` = `http://anybotbe:8002`
   - `API_URL` = `http://anybotbe:8002` (backup)

2. **Ports and Networking**:
   - Frontend should listen on port 8080
   - `RAILWAY_PRIVATE_NETWORK=true` is set in the Dockerfile

### For the Backend Service (`anybotbe`)

1. **Service Variables to Add**:
   - `PORT` = `8002`
   - `RAILWAY_HEALTHCHECK_PATH` = `/`

2. **Ports and Networking**:
   - Backend listens on port 8002
   - Using 0.0.0.0 to bind to all interfaces (both IPv4 and IPv6)
   - `RAILWAY_PRIVATE_NETWORK=true` is set in the Dockerfile

## Manual Testing

If you suspect networking issues, try these commands from within the frontend container:

```bash
# Test DNS resolution
getent hosts anybotbe.railway.internal

# Try direct connection to backend 
curl -v http://anybotbe:8002/health

# Try connection with resolved IPv6 (replace with actual IP)
curl -v -g "http://[fd12:22b0:4b1c:0:1000:6:43f:d884]:8002/health"
```

## Troubleshooting Tips

1. **Check Service Names**: Ensure service names match exactly as defined in Railway

2. **Manual Network Testing**:
   - Check frontend logs for DNS resolution results
   - View `/env` endpoint in the frontend for debugging info
   - Check backend logs for connection attempts

3. **Check for Firewalls**:
   - Railway may have internal firewall rules
   - Try reaching out to Railway support if issues persist

4. **Service Restart**:
   - Sometimes restarting both services resolves networking issues

## Railway Feature Information

Based on Railway documentation:

1. Private networking is IPv6-only
2. Private networking is not available during build phase
3. Applications need to bind to IPv6 addresses to receive traffic
4. Internal service communication is available via:
   - Service name (e.g., `anybotbe:8002`)
   - Full DNS name (e.g., `anybotbe.railway.internal:8002`)
   - IPv6 addresses (but these can change between deployments)

## Health Check URLs

The backend provides these health endpoints:
- `/` - Root endpoint for basic health checks
- `/health` - Detailed health check 
- `/healthz` - Simple health check for internal services 