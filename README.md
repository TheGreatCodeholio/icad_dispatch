# iCAD Dispatch

iCAD Dispatch is a Progressive Web Application (PWA) that processes audio inputs from a police scanner application and triggers alerts based on tones found in the audio.

---

## Requirements
- **Linux**: This software is mean to be run on a Linux Server of some sort. I developed it running on a debian based distro. Windows make work in some cases, but is not directly supported.
- **Docker**: Ensure Docker is installed on your system. [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: Required to clone the repository. [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

---

## Deployment Guide

Follow these steps to deploy the application from scratch:

### 1. **Create a Non-root User**
For security and compatibility with the Docker image, create a non-root user on your host system. The user will not have login access to the host.

Run the following commands:
```bash
# Create a group with GID 9911
sudo groupadd -g 9911 icad_dispatch

# Create a user with UID 9911, assign to the group, and disable login
sudo useradd -M -s /usr/sbin/nologin -u 9911 -g icad_dispatch icad_dispatch
```

**Explanation**:
- **`-M`**: Prevents creating a home directory for the user (the user won't own files outside the application scope).
- **`-s /usr/sbin/nologin`**: Sets the shell to `/usr/sbin/nologin`, disabling the user from logging into the system interactively.

---

### 2. **Grant Group Access to Your User**
To allow your regular user to manage files owned by the `icad_dispatch` group (e.g., for logs and configuration files), add your user to the `icad_dispatch` group.

Run the following command:
```bash
# Add your user to the icad_dispatch group
sudo usermod -aG icad_dispatch your_user
```

**Explanation**:
- **`usermod`**: Modifies the properties of an existing user.
- **`-aG`**: Appends the user to the specified group without removing them from existing groups.
- Replace `your_user` with your current username.

After running this command, you may need to log out and log back in for the changes to take effect. Once added to the group, your user will have read and write access to files owned by `icad_dispatch`.

---

### 3. **Clone the Repository**
Choose a directory where you want to deploy the application and clone this repository:
```bash
git clone https://github.com/TheGreatCodeholio/icad_dispatch.git
cd icad_dispatch
```

---

### 4. **Set Up the Directory Structure**
Ensure the directory has the required structure for the application to function correctly. The `.env` file specifies the working path for mounting volumes.

#### Create and Adjust Permissions for Directories:
Run the following commands:
```bash
# Create the required directories
mkdir -p log var

# Change ownership to the non-root docker user
sudo chown -R icad_dispatch:icad_dispatch log var
```

The `log` directory will store logs, and the `var` directory will store a sqlite database and other variables.

---

### 5. **Configure the `.env` File**

Update your `.env` with values appropriate for your environment. The app reads configuration from process environment variables at startup. A good workflow is:

Copy a template to get started.
```bash
   cp .env.example .env
```

Edit `.env` and fill in the fields described below.

---

#### Required / Important Variables

- **Logging**
   - `LOG_LEVEL` — Numeric log level (e.g., 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL).

- **Timezone**
  - `TIMEZONE` — IANA timezone (via Python `zoneinfo`) 
    - Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. 
    - Examples: `America/New_York`, `America/Chicago`, `America/Denver`, `America/Los_Angeles`, `UTC`

- **Base URL**
   - `BASE_URL` — Publicly reachable base URL (scheme + host[:port]) used in links and some redirects.

- **Cookies / Sessions**
   - `SESSION_COOKIE_SECURE` — `True` in production (HTTPS); `False` for local HTTP.
   - `SESSION_COOKIE_DOMAIN` — Hostname used by the browser for the session cookie.
   - `SESSION_COOKIE_NAME` — Cookie name for the app session.
   - `SESSION_COOKIE_PATH` — Cookie path scope (usually `/`).

- **Database**
   - `SQLITE_DATABASE_PATH` — Path to the SQLite database file.

- **Bootstrap Root User (first run)**
   - `ROOT_USERNAME` — Optional; defaults to `root` if omitted. Don't use the default.
   - `ROOT_PASSWORD` — Inline password for bootstrap user. **Change** once logged in for the first time.

---

#### Example `.env` for running on a LAN only server no proxy (nginx).

```env
# ─────────────── Logging ───────────────
LOG_LEVEL=1

# ─────────────── Timezone ───────────────
TIMEZONE=America/New_York

# ─────────────── Base URL ───────────────
BASE_URL=http://192.168.1.104:9911

# ─────────────── Cookies ───────────────
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_DOMAIN=192.168.1.104
SESSION_COOKIE_NAME=icad_transcribe
SESSION_COOKIE_PATH=/

# ─────────────── SQLite ───────────────
SQLITE_DATABASE_PATH=var/icad_transcribe.db

# ─────────────── Root User Bootstrap ───────────────
# Root username (optional, defaults to "root" if omitted)
ROOT_USERNAME=root

# Root password (required on first boot)
ROOT_PASSWORD=changeme123

```

---

#### Using Docker/Compose (env file)

Point your service to the env file: (.env set by default). Compose picks this .env up for container
```yaml
   services:
   icad_dispatch:
     image: thegreatcodeholio/icad_dispatch:latest
     user: "icad_dispatch"
     env_file:
       - .env
# ... other service config (volumes, ports, command, etc.)
```


---

### 6. **Run Docker Compose**
With the environment configured and directories prepared, you can start the application using Docker Compose.

Run the following command:
```bash
docker compose up -d
```

This command will:
1. Pull the necessary images from the repository.
2. Build and start the containers in detached mode (running in the background).
3. Mount the `log` and `etc` directories based on the path you ran the docker compose command in.

---

### 7. **Verify Deployment**

#### Check if Containers Are Running
To list all running containers, use:
```bash
docker ps -a
```

- This command will display a table of running containers, including their **container IDs**, names, and status.

#### Check Container Logs
1. Identify the container name or ID from the output of `docker ps`.
2. View live logs for a specific container:
   ``bash
   docker logs -f <container_id_or_name>
   ``
- Replace `<container_id_or_name>` with the actual container ID or name (e.g., `icad_transcribe`).

#### Example
To view logs for the Flask application:
```bash
docker logs -f icad_transcribe
```

This will show real-time logs to help you verify that the services are starting as expected.

---

## Security Best Practices
1. **Run as Non-root**: The application enforces a non-root user within the container to improve security. Host directories and files in the working path must be read/write by the same non-root user (`icad_dispatch`).

2. **Use Secure Passwords**: If allowing general access from the internet, use a non-standard user name and a strong password.

3. **Restrict Permissions**: Allow only the `icad_dispatch` group and `your_user` access to the application directory and logs:
   ```bash
   sudo chown your_user:icad_dispatch /home/your_user/icad_transcribe
   sudo chmod -R 760 /home/your_user/icad_transcribe
   ```
4. **Use HTTPS**: Ensure the application is accessed via HTTPS in production to secure data in transit. This can be done with NGINX proxy.

---
