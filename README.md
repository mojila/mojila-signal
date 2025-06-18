# Mojila Signal - Enhanced Stock Market Signal Generator

A Python-based stock market signal generator that provides buy/sell recommendations for US stocks using RSI (Relative Strength Index) and MACD (Moving Average Convergence Divergence) technical indicators.

## Features

- **RSI-based Signal Generation**: Uses 14-period RSI with customizable thresholds
- **MACD Analysis**: 12-day EMA, 26-day EMA MACD Line, and 9-day Signal Line
- **Enhanced Signal Precision**: Combines RSI and MACD for more accurate signals
- **Position Categories**: Golden Cross, Dead Cross, Up Trend, Down Trend classifications
- **Buy Signal**: RSI ≤ 30 (Oversold) or MACD bullish crossover
- **Sell Signal**: RSI ≥ 70 (Overbought) or MACD bearish crossover OR upcoming calendar events
- **Strong Signals**: Enhanced BUY/SELL signals when RSI and MACD confirm each other
- **Calendar Event Detection**: Automatic SELL signal when ex-dividend or earnings date is tomorrow
- **Hold Signal**: RSI between 30-70 with no strong MACD signals
- **Multiple Stock Analysis**: Analyze multiple stocks simultaneously
- **Configurable Parameters**: Customize RSI and MACD periods and thresholds
- **Error Handling**: Robust error handling with retry mechanisms

## Signal Logic

The enhanced signal generator uses the following logic combining RSI and MACD:

### Basic Signals
- **BUY**: When RSI ≤ 30 (stock is oversold) or MACD bullish crossover
- **SELL**: When RSI ≥ 70 (stock is overbought) or MACD bearish crossover OR calendar events
- **HOLD**: When RSI is between 30-70 with no strong MACD signals

### Enhanced Signals
- **STRONG_BUY**: RSI ≤ 30 + MACD Golden Cross confirmation
- **STRONG_SELL**: RSI ≥ 70 + MACD Dead Cross confirmation

### MACD Position Categories
- **Golden Cross**: MACD > Signal Line, both above zero
- **Dead Cross**: MACD < Signal Line, both below zero
- **Up Trend**: MACD & Signal above zero line
- **Down Trend**: MACD & Signal below zero line

### Calendar Events

The system automatically checks for upcoming calendar events and triggers SELL signals when:
- **Ex-dividend date** is tomorrow (stock typically drops by dividend amount on ex-date)
- **Earnings report date** is tomorrow (increased volatility expected)

This feature helps traders avoid potential price drops or volatility around these events.

## Installation

### Option 1: Docker (Recommended)

1. Clone this repository:
```bash
git clone <repository-url>
cd mojila-signal
```

2. Build and run with Docker:
```bash
# Quick start
docker-compose up --build

# Or use the build script
./docker-build.sh
```

3. For web interface:
```bash
docker-compose --profile web up --build
```

See [README-Docker.md](README-Docker.md) for detailed Docker instructions.

### Option 2: Local Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd mojila-signal
```

2. Run the setup script:
```bash
bash setup.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Test the installation:
```bash
python test_installation.py
```

## Usage

### Basic Usage

Run the main script to analyze popular US stocks:

```bash
python main.py
```

### Custom Portfolio

You can create a `my_portfolio.txt` file to specify which stocks to analyze instead of using the default list.

### Creating Your Portfolio File

1. Create a file named `my_portfolio.txt` in the project root directory
2. Add one stock symbol per line
3. Use uppercase symbols (e.g., AAPL, MSFT, GOOGL)
4. Empty lines and comments (lines starting with #) are ignored

### Example `my_portfolio.txt`:
```
AAPL
MSFT
GOOGL
AMZN
TSLA
NVDA
META
# Technology stocks focus
CRM
ADOBE
NFLX
```

### How It Works

- If `my_portfolio.txt` exists, the application will load stocks from this file
- If the file doesn't exist or is empty, it falls back to the default stock list from `config.py`
- The application will display which source it's using when you run it
- Supports flexible formatting (handles extra whitespace, case-insensitive)
- Provides clear feedback on the number of stocks loaded and the source

## Market Scan

The application can also perform market-wide scans using a separate stock list for broader signal detection.

### Creating Your Scan List

1. Create a file named `scan_list.txt` in the project root directory
2. Add one stock symbol per line (typically top market cap stocks)
3. Use uppercase symbols

### Example `scan_list.txt`:
```
AAPL
MSFT
GOOGL
AMZN
NVDA
TSLA
META
BRK.B
TSM
UNH
# ... more stocks
```

### How Market Scan Works

- Runs automatically after portfolio analysis
- Analyzes all stocks in `scan_list.txt`
- **Telegram notifications only sent for BUY/SELL signals** (HOLD signals are filtered out)
- Separate notification message from portfolio alerts
- Provides summary of signals found
- Skips scan if `scan_list.txt` doesn't exist

### Telegram Notifications

You can enable Telegram notifications to receive stock signals directly in your Telegram chat. Create a `telegram_config.json` file in the project directory:

```json
{
    "api_key": "YOUR_BOT_TOKEN",
    "user_ids": ["YOUR_TELEGRAM_USER_ID"]
}
```

**Setup Instructions:**

1. **Create a Telegram Bot:**
   - Message @BotFather on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token (api_key)

2. **Get Your User ID:**
   - Message @userinfobot on Telegram
   - Copy your user ID

3. **Start the Bot:**
   - Find your bot on Telegram and send `/start`
   - This allows the bot to send you messages

4. **Configure the Application:**
   - Create `telegram_config.json` with your bot token and user ID
   - Run the application - it will automatically send notifications if configured

Example notification message:
```
🔔 Stock Signal Alert

📊 Current Signals:
AAPL   🟡HOLD  45.2  $150.25
TSLA   🟢BUY   28.5  $195.75
MSFT   🔴SELL  72.1  $380.50

🟢 Buy Signals: TSLA (RSI: 28.5)
🔴 Sell Signals: MSFT (RSI: 72.1)
```

If `telegram_config.json` doesn't exist, the application will run normally without sending notifications.

This will analyze the following stocks by default:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- AMZN (Amazon)
- TSLA (Tesla)
- NVDA (NVIDIA)
- META (Meta)
- NFLX (Netflix)

### Custom Usage

```python
from main import RSISignalGenerator

# Initialize with custom parameters
signal_generator = RSISignalGenerator(
    rsi_period=21,  # Use 21-day RSI instead of default 14
    oversold_threshold=25,  # More conservative buy threshold
    overbought_threshold=75,  # More conservative sell threshold
    check_calendar_events=True  # Enable calendar event checking (default)
)

# Analyze a single stock
result = signal_generator.generate_signals('AAPL', period='6mo')
print(f"Current signal for AAPL: {result['currentSignal']}")

# Analyze multiple stocks
stocks = ['AAPL', 'MSFT', 'GOOGL']
results = signal_generator.analyze_multiple_stocks(stocks)
```

### Available Time Periods

- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year (default)
- `2y` - 2 years
- `5y` - 5 years
- `10y` - 10 years
- `ytd` - Year to date
- `max` - Maximum available data

## Output Format

The enhanced signal generator returns a dictionary with the following information:

```python
{
    "symbol": "AAPL",
    "currentPrice": 150.25,
    "currentRSI": 45.67,
    "currentSignal": "HOLD",
    "signalStrength": "NORMAL",
    "currentMACD": -1.7033,
    "currentMACDSignal": -1.3228,
    "currentMACDHistogram": -0.3805,
    "macdPosition": "Dead Cross",
    "recentBuySignals": 2,
    "recentSellSignals": 1,
    "calendarEvents": {
        "ex_date_tomorrow": false,
        "earnings_tomorrow": false
    },
    "calendarReasons": [],
    "lastUpdated": "2024-01-15 10:30:00",
    "data": [...] # Last 10 days of OHLCV + RSI data
}
```

## Example Output

```
============================================================
MOJILA SIGNAL - RSI Stock Market Signal Generator
============================================================
RSI Oversold Threshold: 30
RSI Overbought Threshold: 70
============================================================

CURRENT SIGNALS:
--------------------------------------------------------------------------------
Symbol   Price      RSI      Signal   Strength   Buy/30d  Sell/30d Calendar
AAPL     $150.25    45.2     HOLD     NORMAL     2        1        -
MSFT     $380.50    72.1     SELL     NORMAL     0        3        -
TSLA     $195.75    28.5     BUY      NORMAL     4        0        -
JNJ      $165.30    68.9     SELL     NORMAL     1        2        Ex-dividend date tomorrow
GOOGL    $140.80    28.9     BUY      NORMAL     4        0        -
AMZN     $155.20    55.4     HOLD     NORMAL     1        2        -
NVDA     $520.30    42.8     HOLD     NORMAL     3        1        -
META     $350.75    31.2     HOLD     NORMAL     2        0        -
NFLX     $480.90    68.5     HOLD     NORMAL     0        2        -       
--------------------------------------------------------------------------------

Legend:
BUY  - RSI <= 30 (Oversold, potential buying opportunity)
SELL - RSI >= 70 (Overbought, potential selling opportunity)
HOLD - RSI between 30-70 (Neutral zone)
Buy/30d, Sell/30d - Number of signals in the last 30 days
```

## Dependencies

- **yfinance**: Yahoo Finance API for stock data
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

## RSI Technical Indicator

The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements. It oscillates between 0 and 100 and is typically used to identify overbought or oversold conditions in a stock.

- **RSI > 70**: Generally considered overbought (potential sell signal)
- **RSI < 30**: Generally considered oversold (potential buy signal)
- **RSI 30-70**: Neutral zone

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.