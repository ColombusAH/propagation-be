# Railway Deployment Guide

This guide details how to deploy the **Tagid-RF** project to Railway and establish communication with the physical RFID M-200 Reader.

## Prerequisites

*   GitHub Account connected to [Railway](https://railway.app)
*   [Tailscale](https://tailscale.com) account (for secure device communication)

---

## Part 1: Deploying the Services

### 1. Database (PostgreSQL)
1.  In Railway, create a new **PostgreSQL** service.
2.  Note the `DATABASE_URL` from the *Variables* tab.

### 2. Backend Service (`Tagid-RF/be`)
1.  **New > GitHub Repo**. Select your repository.
2.  **Settings > General > Root Directory**: Set to `Tagid-RF/be`.
3.  **Variables**:
    *   `DATABASE_URL`: (Paste from Postgres service)
    *   `PORT`: `8002` (Optional, Railway sets this, but code looks for it)
    *   `RFID_READER_IP`: The **Tailscale IP** of your reader (or the gateway machine).
    *   `RFID_READER_PORT`: `4001` (Default)
    *   `TAILSCALE_AUTH_KEY`: Your Tailscale Auth Key (authkey_...).
4.  **Networking**: Railway will generate a public domain (e.g., `be-production.up.railway.app`).

### 3. Frontend Service (`Tagid-RF/web`)
1.  **New > GitHub Repo** (Same repo).
2.  **Settings > General > Root Directory**: Set to `Tagid-RF/web`.
3.  **Variables**:
    *   `VITE_API_URL`: The URL of your Backend service (e.g., `https://be-production.up.railway.app`).
4.  **Networking**: Generate a public domain.

### 4. Deploy
*   Railway will automatically build and deploy both services.

---

## Part 2: Connecting the RFID Reader (Crucial)

Since the Backend runs in the Cloud and the RFID Reader is on a Local Network (behind a NAT), they cannot talk strictly over the public internet without help. **We recommend using Tailscale** to create a secure private network.

### Why Tailscale?
*   **Backend -> Reader**: Allows the Cloud Backend to connect to the Reader's local IP (Active Control).
*   **Reader -> Backend**: Allows the Reader to push data to the Cloud Backend's TCP Listener (Passive Mode).

### Step-by-Step Setup

#### A. Configure Railway for Tailscale
1.  In your Railway Backend Service, navigate to **Settings**.
2.  Add the **Tailscale Auth Key** as a variable: `TAILSCALE_AUTH_KEY`.
3.  Ensure your `Dockerfile` or Entrypoint installs and starts Tailscale.
    *   *Note*: The current `Dockerfile` in `be/` does not include Tailscale installation commands. You may need to add them or use a Railway Tailscale Template.
    *   **Quick Fix**: In Railway settings for the Backend, change the Start Command to:
        ```bash
        curl -fsSL https://tailscale.com/install.sh | sh && tailscale up --authkey=$TAILSCALE_AUTH_KEY && /app/scripts/railway-entrypoint-python.sh
        ```
        *(Or verify if using a base image with Tailscale is preferred)*.

#### B. Configure the Store Network (Subnet Router)
Since you cannot install Tailscale *on* the M-200 Reader directly:
1.  Run Tailscale on a **PC/Raspberry Pi** on the *same local network* as the Reader.
2.  Enable **Subnet Routing** to expose the Reader's IP (e.g., `192.168.1.100`) to the Tailscale network.
    ```bash
    tailscale up --advertise-routes=192.168.1.0/24
    ```
3.  In the Tailscale Admin Console, **approve** the subnet routes.

#### C. Final Configuration
1.  **Backend Env Var**: Update `RFID_READER_IP` in Railway to the **Local LAN IP** of the reader (e.g., `192.168.1.100`). Tailscale handles the routing!
2.  **Reader Configuration**:
    *   If the Reader pushes data (Server Mode), configure the Reader's "Destination IP" to the **Tailscale IP** of the Railway Backend (find this in Tailscale Console).
    *   Destination Port: `2022` (default listener port).

---

## Troubleshooting

*   **Reader not connecting**: Check Tailscale logs in Railway to ensure it's "Connected".
*   **No tags appearing**: Verify the Reader's destination IP matches the Railway instance's Tailscale IP.
*   **Active Control fails**: Ensure Subnet Routing is active and approved in Tailscale console.
