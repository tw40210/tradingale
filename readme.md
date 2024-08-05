# :chart: Tradingale

![python-version](https://img.shields.io/badge/python-3.11-blue.svg)

## Introduction

In the rapidly evolving world of financial trading, the ability to test and validate trading strategies before deploying them in live markets is crucial. Our Backtest application, designed with a modularized algorithm stack strategy, offers a sophisticated solution for traders and analysts seeking to optimize their strategies with precision and flexibility.

## Installation

`python -m venv ./py_env `
`source ./py_env/bin/activate`
`python -m pip install -r ./requirement/requirements.txt`

## Quick start

`source ./py_env/bin/activate`
`python -m src.main`

Browse to `http://localhost:5000`

## Usage

1. Data control panel - help you manage your data fed into backtest module
2. Algo stack panel - help you build your own algorithm chain and setup them
3. Strategy and backtest control panel - help you link your "Strategy" to an "Algo Stack" and securities you want to include. You can also link your "Backtest" to a "Strategy" here.
4. Backtest display panel - display the result of your backtest
