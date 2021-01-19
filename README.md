# Binance Trade Bot

## Trading Strategy

The bot buys with a set amount of currency when the current price crosses above 24h EMA. The price will keep rising in theory, due to market momentum. When the price starts to decline, the bot will sell bought assets after the current price pierces below 24h EMA. 

It is planned to switch to MACD indicator to predict the optimum selling price where the price will start to drop. This way, the bot will be able to sell assets in higher prices, before the price hits 24h EMA. 

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

6. Run the program with your API key and secret and optionally the symbol to trade and the amount of asset to trade with

```
python binance_bot.py --key BINANCEAPIKEY --secret BINANCEAPISECRET
```

For example, the command below buys and sells $10 worth of BTC according to the trading strategy stated above

```
python binance_bot.py --key BINANCEAPIKEY --secret BINANCEAPISECRET --symbol BTCUSDT --amount 10
```

## Arguments

| Parameter                 | Default        | Description                       |
| :------------------------ | :-------------:| :-------------------------------- |
| --symbol 	                | BTCUSDT        | the symbol to trade
| --amount                  | 10.0           | the amount of asset to trade with
| --key                     | None	         | Binance API key
| --secret                  | None	         | Binance API secret

## Planned Features

* MACD indicator (buy/sell)

## Liability

The software provided in the repository is not a product nor an investment tool, but an educational example. None of the contributors to this project are liable nor responsible for any losses the user may incur. 
