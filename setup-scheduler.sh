#!/bin/bash

# Mojila Signal Scheduler Setup Script
# This script sets up the automated signal generation scheduler

set -e  # Exit on any error

echo "🕐 Setting up Mojila Signal Scheduler..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/update schedule dependency
print_status "Installing scheduler dependencies..."
pip install schedule>=1.2.0

# Create log directory
print_status "Creating log directory..."
mkdir -p logs
touch scheduler.log

# Test scheduler functionality
print_status "Testing scheduler functionality..."
python -c "from scheduler import SignalScheduler; scheduler = SignalScheduler(); scheduler.health_check()" || {
    print_error "Scheduler test failed. Please check your configuration."
    exit 1
}

print_success "Scheduler test passed!"

# Setup options
echo ""
echo "📋 Setup Options:"
echo "================="
echo "1. Run scheduler manually (foreground)"
echo "2. Setup systemd service (Linux)"
echo "3. Setup cron job"
echo "4. Docker deployment"
echo "5. Test run (single scan)"
echo "6. Exit"
echo ""

read -p "Choose an option (1-6): " choice

case $choice in
    1)
        print_status "Starting scheduler in foreground mode..."
        print_warning "Press Ctrl+C to stop the scheduler"
        python scheduler.py
        ;;
    2)
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            print_status "Setting up systemd service..."
            
            # Update service file with current directory
            CURRENT_DIR=$(pwd)
            sed "s|/opt/mojila-signal|$CURRENT_DIR|g" mojila-signal-scheduler.service > /tmp/mojila-signal-scheduler.service
            
            print_status "Service file created. To install:"
            echo "sudo cp /tmp/mojila-signal-scheduler.service /etc/systemd/system/"
            echo "sudo systemctl daemon-reload"
            echo "sudo systemctl enable mojila-signal-scheduler"
            echo "sudo systemctl start mojila-signal-scheduler"
            echo ""
            echo "To check status: sudo systemctl status mojila-signal-scheduler"
            echo "To view logs: sudo journalctl -u mojila-signal-scheduler -f"
        else
            print_warning "Systemd service setup is only available on Linux systems"
        fi
        ;;
    3)
        print_status "Setting up cron job..."
        CURRENT_DIR=$(pwd)
        
        # Create personalized crontab entry
        echo "# Mojila Signal - Hourly scan" > /tmp/mojila-cron
        echo "0 * * * * cd $CURRENT_DIR && source venv/bin/activate && python scheduler.py --once >> $CURRENT_DIR/scheduler.log 2>&1" >> /tmp/mojila-cron
        echo "" >> /tmp/mojila-cron
        
        print_status "Cron job entry created. To install:"
        echo "crontab -l > /tmp/current-cron 2>/dev/null || true"
        echo "cat /tmp/mojila-cron >> /tmp/current-cron"
        echo "crontab /tmp/current-cron"
        echo ""
        echo "To verify: crontab -l"
        echo "To remove: crontab -e (and delete the Mojila Signal lines)"
        ;;
    4)
        print_status "Docker deployment instructions:"
        echo ""
        echo "1. Build and run with Docker Compose:"
        echo "   docker-compose up --build"
        echo ""
        echo "2. Run scheduler only:"
        echo "   docker-compose up mojila-signal"
        echo ""
        echo "3. View logs:"
        echo "   docker-compose logs -f mojila-signal"
        echo ""
        echo "4. Run single scan:"
        echo "   docker-compose exec mojila-signal python scheduler.py --once"
        ;;
    5)
        print_status "Running test scan..."
        python scheduler.py --once
        print_success "Test scan completed! Check scheduler.log for details."
        ;;
    6)
        print_status "Setup completed. Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid option selected"
        exit 1
        ;;
esac

echo ""
print_success "Scheduler setup completed!"
echo ""
echo "📚 Additional Information:"
echo "========================="
echo "• Configuration files: my_portfolio.txt, scan_list.txt, telegram_config.json"
echo "• Log file: scheduler.log"
echo "• Manual run: python scheduler.py --once"
echo "• Health check: python -c 'from scheduler import SignalScheduler; SignalScheduler().health_check()'"
echo "• Database stats: python -c 'from database import SignalDatabase; print(SignalDatabase().get_database_stats())'"
echo ""
echo "For more information, see README-Docker.md"