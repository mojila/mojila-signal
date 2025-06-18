# Mojila Signal - Automated Scheduler

This document explains how to set up and use the automated signal generation scheduler for the Mojila Signal project.

## Overview

The scheduler automatically runs market scans at regular intervals and saves signals to the database. It provides multiple deployment options including standalone Python service, systemd service, cron jobs, and Docker containers.

## Features

- **Hourly Signal Scans**: Automatically generates buy/sell signals every hour
- **Database Management**: Cleans up old signals to maintain performance
- **Health Monitoring**: Regular health checks with logging
- **Multiple Deployment Options**: Python service, systemd, cron, Docker
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Error Handling**: Robust error handling with automatic retries

## Quick Start

### 1. Install Dependencies

```bash
# Install the schedule library
pip install schedule>=1.2.0

# Or install all requirements
pip install -r requirements.txt
```

### 2. Test Single Scan

```bash
# Run a single signal scan
python scheduler.py --once
```

### 3. Start Continuous Scheduler

```bash
# Run the scheduler (will run continuously)
python scheduler.py
```

## Deployment Options

### Option 1: Python Service (Recommended for Development)

```bash
# Run in foreground
python scheduler.py

# Run in background (Linux/macOS)
nohup python scheduler.py > scheduler.log 2>&1 &
```

### Option 2: Docker (Recommended for Production)

```bash
# Using Docker Compose
docker-compose up --build

# View logs
docker-compose logs -f mojila-signal

# Run single scan
docker-compose exec mojila-signal python scheduler.py --once
```

### Option 3: Systemd Service (Linux)

```bash
# Setup using the provided script
./setup-scheduler.sh

# Or manually:
sudo cp mojila-signal-scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mojila-signal-scheduler
sudo systemctl start mojila-signal-scheduler

# Check status
sudo systemctl status mojila-signal-scheduler

# View logs
sudo journalctl -u mojila-signal-scheduler -f
```

### Option 4: Cron Job

```bash
# Edit crontab
crontab -e

# Add hourly scan (update path as needed)
0 * * * * cd /path/to/mojila-signal && source venv/bin/activate && python scheduler.py --once >> /var/log/mojila-signal.log 2>&1

# Alternative: Market hours only (9 AM - 4 PM, Mon-Fri)
0 9-16 * * 1-5 cd /path/to/mojila-signal && source venv/bin/activate && python scheduler.py --once >> /var/log/mojila-signal.log 2>&1
```

## Configuration

### Schedule Settings

The default schedule can be modified in `scheduler.py`:

```python
# Current settings:
schedule.every().hour.at(":00").do(self.run_signal_scan)  # Hourly scans
schedule.every().day.at("02:00").do(self.cleanup_old_signals)  # Daily cleanup
schedule.every(6).hours.do(self.health_check)  # Health checks
```

### Environment Variables

- `TZ`: Timezone (default: UTC)
- `PYTHONPATH`: Python path for imports
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Required Files

Ensure these files exist before running:

1. **scan_list.txt** - List of stock symbols to scan
2. **my_portfolio.txt** - Your portfolio (optional)
3. **telegram_config.json** - Telegram notifications (optional)

## Monitoring and Logs

### Log Files

- **scheduler.log** - Main scheduler logs
- **Console output** - Real-time status updates

### Log Levels

- `INFO`: Normal operations, scan results
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors requiring attention

### Health Checks

```bash
# Manual health check
python -c "from scheduler import SignalScheduler; SignalScheduler().health_check()"

# Database statistics
python -c "from database import SignalDatabase; print(SignalDatabase().get_database_stats())"
```

## Scheduled Tasks

### 1. Signal Scans (Hourly)

- **Frequency**: Every hour at :00 minutes
- **Function**: Scans all symbols in scan_list.txt
- **Output**: Buy/sell signals saved to database
- **Logging**: Detailed scan results and timing

### 2. Database Cleanup (Daily)

- **Frequency**: Daily at 2:00 AM
- **Function**: Removes signals older than 30 days
- **Purpose**: Maintains database performance
- **Logging**: Number of records cleaned up

### 3. Health Checks (Every 6 Hours)

- **Frequency**: Every 6 hours
- **Function**: Verifies system components
- **Checks**: Database connectivity, scan list loading
- **Logging**: Health status and any issues

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error
```bash
# Install missing dependencies
pip install -r requirements.txt
```

#### 2. Permission Denied
```bash
# Fix file permissions
chmod +x scheduler.py setup-scheduler.sh
```

#### 3. Database Lock Error
```bash
# Check if another process is using the database
ps aux | grep python
# Kill conflicting processes if needed
```

#### 4. No Signals Generated
- Check scan_list.txt exists and contains valid symbols
- Verify internet connection for stock data
- Check logs for specific error messages

### Debug Mode

```bash
# Run with verbose logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from scheduler import SignalScheduler
SignalScheduler().run_signal_scan()
"
```

### Log Analysis

```bash
# View recent logs
tail -f scheduler.log

# Search for errors
grep ERROR scheduler.log

# Count successful scans
grep "Scan completed" scheduler.log | wc -l
```

## Performance Optimization

### Database Optimization

- Automatic cleanup removes old signals
- Database size monitoring in health checks
- Efficient queries with proper indexing

### Memory Management

- Minimal memory footprint
- Garbage collection after each scan
- No persistent data caching

### Network Optimization

- Batch API requests where possible
- Retry logic for failed requests
- Timeout handling for slow responses

## Security Considerations

### File Permissions

```bash
# Secure configuration files
chmod 600 telegram_config.json
chmod 644 scan_list.txt my_portfolio.txt
```

### Service Security

- Run as non-root user
- Limit file system access
- No network exposure (scheduler only)

### Log Security

- No sensitive data in logs
- Regular log rotation
- Secure log file permissions

## Integration

### With Web Interface

```bash
# Run both scheduler and web interface
docker-compose --profile web up
```

### With Telegram Notifications

- Configure telegram_config.json
- Notifications sent automatically with signals
- Error notifications for critical issues

### With External Systems

- Database can be accessed by external tools
- REST API available through web interface
- Export capabilities for signal data

## Advanced Configuration

### Custom Schedules

Modify `scheduler.py` for custom timing:

```python
# Every 30 minutes
schedule.every(30).minutes.do(self.run_signal_scan)

# Weekdays only
schedule.every().monday.at("09:00").do(self.run_signal_scan)
schedule.every().tuesday.at("09:00").do(self.run_signal_scan)
# ... etc

# Market hours only (example)
for hour in range(9, 17):  # 9 AM to 4 PM
    schedule.every().day.at(f"{hour:02d}:00").do(self.run_signal_scan)
```

### Multiple Symbol Lists

```python
# Scan different lists at different times
schedule.every().hour.at(":00").do(lambda: self.scan_custom_list("high_priority.txt"))
schedule.every(2).hours.at(":30").do(lambda: self.scan_custom_list("watchlist.txt"))
```

## Support

For issues or questions:

1. Check the logs first: `tail -f scheduler.log`
2. Run health check: `python -c "from scheduler import SignalScheduler; SignalScheduler().health_check()"`
3. Test single scan: `python scheduler.py --once`
4. Review configuration files
5. Check system resources (disk space, memory)

For more information, see the main [README.md](README.md) and [README-Docker.md](README-Docker.md).