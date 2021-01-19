# Binance Trade Bot

## Trading Strategy

The bot buys with a set amount of currency when the current price crosses above 24h EMA. The price will keep rising in theory, due to market momentum. When the price starts to decline, the bot will sell bought assets after the current price pierces below 24h EMA. 

## Usage
1. Clone this repository

```
git clone https://github.com/aizuon/binance-bot.git
```

2. Create directory to repository

```
cd binance-bot
```

3. Create a conda environment and install dependencies

```
conda create -n binance-bot -f requirements.txt
```

4. Activate the conda environment

```
conda activate binance-bot
```

5. Create a Binance API key through https://www.binance.com/en/my/settings/api-management

6. Run the program with your API key and secret and desired symbol to trade

```
python binance_boy.py --symbol TRADINGSYMBOL(eg. BTCUSDT) --key BINANCEAPIKEY --secret BINANCEAPISECRET
```

## Liability

The program provided in the repository is not a product nor an investing tool, but an educational asset. None of the contributors to this project are liable for any losses the user may incur. 
