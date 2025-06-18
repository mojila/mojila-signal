# Docker Setup for Mojila Signal

This guide explains how to build and run the Mojila Signal project using Docker for easy deployment and consistent environment setup.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

## Quick Start

### 1. Build and Run with Docker Compose (Recommended)

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd mojila-signal

# Create required configuration files
cp my_portfolio.txt.template my_portfolio.txt
cp telegram_config.json.template telegram_config.json

# Edit configuration files with your settings
# ... edit my_portfolio.txt and telegram_config.json ...

# Start both scheduler and web app
docker-compose up -d

# Access the web interface
open http://localhost:5000

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

### 2. Run with Web Interface

```bash
# Start both signal generator and web interface
docker-compose --profile web up --build
```

### 3. Build and Run with Docker Only

```bash
# Build the Docker image
docker build -t mojila-signal .

# Run the container
docker run -d \
  --name mojila-signal-app \
  -v $(pwd)/signals.db:/app/signals.db \
  -v $(pwd)/my_portfolio.txt:/app/my_portfolio.txt:ro \
  -v $(pwd)/scan_list.txt:/app/scan_list.txt:ro \
  -v $(pwd)/telegram_config.json:/app/telegram_config.json:ro \
  -p 5000:5000 \
  mojila-signal
```

## Configuration

### Required Files

Before running, ensure these configuration files exist:

1. **my_portfolio.txt** - Your stock portfolio (copy from template)
   ```bash
   cp my_portfolio.txt.template my_portfolio.txt
   # Edit with your stocks
   ```

2. **scan_list.txt** - Stocks to scan for signals
   ```bash
   # Create or edit scan_list.txt with stock symbols
   echo "AAPL\nMSFT\nGOOGL\nTSLA" > scan_list.txt
   ```

3. **telegram_config.json** - Telegram bot configuration (optional)
   ```bash
   cp telegram_config.json.template telegram_config.json
   # Edit with your Telegram bot credentials
   ```

### Environment Variables

You can customize the container behavior using environment variables:

```bash
# Example with custom environment
docker run -d \
  --name mojila-signal-app \
  -e TZ=America/New_York \
  -e PYTHONPATH=/app \
  -v $(pwd)/signals.db:/app/signals.db \
  mojila-signal
```

## Docker Services

### Main Service (mojila-signal)
- **Purpose**: Runs both the automated signal scheduler and web application
- **Image**: Built from local Dockerfile
- **Ports**: 5000:5000 (Web interface)
- **Restart Policy**: unless-stopped
- **Health Check**: Validates web application health every 2 minutes
- **Command**: `python main.py`
- **Volumes**: Database and config files

### Web Interface Service (mojila-web)
- **Purpose**: Provides web-based dashboard
- **Port**: 8080 (mapped from container port 5000)
- **Command**: `python app.py`
- **Profile**: `web` (optional service)

## Common Commands

### View Logs
```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f mojila-signal
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Rebuild After Changes
```bash
# Rebuild and restart
docker-compose up --build --force-recreate
```

### Execute Commands in Container
```bash
# Run examples
docker-compose exec mojila-signal python examples.py

# Check database
docker-compose exec mojila-signal python check_db.py

# Interactive shell
docker-compose exec mojila-signal bash
```

## Data Persistence

### Database
The SQLite database (`signals.db`) is mounted as a volume to persist signal data between container restarts.

### Configuration Files
Configuration files are mounted as read-only volumes to allow easy updates without rebuilding the image.

## Troubleshooting

### Container Won't Start
1. Check if required config files exist
2. Verify Docker and Docker Compose versions
3. Check logs: `docker-compose logs mojila-signal`

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod 644 *.txt *.json
```

### Health Check Failures
```bash
# Check container health
docker-compose ps

# Run health check manually
docker-compose exec mojila-signal python test_installation.py
```

### Port Conflicts
If ports 5000 or 8080 are already in use, modify the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8081:5000"  # Change 8080 to 8081
```

## Development

### Development Mode
For development, you can mount the source code as a volume:

```bash
# Add to docker-compose.yml volumes section
volumes:
  - .:/app
  - ./signals.db:/app/signals.db
```

### Debugging
```bash
# Run container interactively
docker run -it --rm mojila-signal bash

# Run specific commands
docker run --rm mojila-signal python test_installation.py
```

## Security Notes

- Configuration files are mounted as read-only
- No sensitive data is included in the Docker image
- Use environment variables for sensitive configuration
- The container runs as non-root user (Python default)

## Performance

- Multi-stage builds for smaller image size
- Efficient layer caching with requirements.txt
- Health checks for container monitoring
- Proper signal handling for graceful shutdowns

For more information about the project itself, see the main [README.md](README.md).