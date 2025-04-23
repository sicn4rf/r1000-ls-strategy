# Multi-Factor Long/Short U.S. Equity Strategy

April 2025

## Strategy Overview

Long/short equity strategy on the Russell 1000 using factor-based forecasting and machine learning. Dollar-neutral construction. Rebalanced monthly. Optimized via quadratic programming under constraints.

## Investment Thesis

Persistent return premia exist across Momentum, Value, Size, Quality, and Low Volatility factors. Academic literature supports long-term outperformance when held through full market cycles. This strategy combines traditional cross-sectional signals with machine learning models to enhance asset selection and incorporate regime awareness using macroeconomic data.

## Factors Used

Factor             | Signal Description                        | Update Frequency     | Notes
------------------ | ----------------------------------------- | -------------------- | ---------------------------------------------------
Momentum           | 12-month return minus most recent 1-month | Monthly              | High turnover signal; behavioral alpha source
Value              | Book-to-price, earnings yield             | Quarterly/Annual     | Mean-reversion effect; long horizon payoff
Size               | Market capitalization                     | Quarterly            | Captures small-cap premium and liquidity risk
Quality            | Return on equity, debt-to-assets          | Quarterly            | Outperforms in late cycle / stress regimes
Low Volatility     | 1Y rolling standard deviation              | Monthly              | Defensive tilt; reduces drawdowns
Sentiment          | LLM-based scores on earnings calls, 10-Ks | Event-driven         | NLP overlay; incorporated via deep learning
Technical          | RSI, MACD, MA crossovers                   | Daily/Monthly        | Used for entry and position scaling
Macro              | CPI, Fed Funds Rate, VIX, Oil, USD Index  | Monthly              | Used for regime flags and signal tilting

## Forecasting Approach

Model: XGBoost and Random Forest  
Horizon: 3–6 months  
Features: Standardized and ranked factor inputs, macro indicators, and engineered lags  
Targets: Forward returns based on rolling window (1000–2000 days)  
Sentiment Layer: NLP-generated sentiment scores enhance signals where applicable

## Portfolio Construction

Universe: Russell 1000  
Long/Short: Long top decile, short bottom decile by predicted return  
Factor Weighting: Equal weights initially; dynamic adjustment tested  
Asset Weighting: Mean-variance optimization with constraints  
Constraints: Sector neutrality, max name exposure, beta neutrality  
Rebalancing: Monthly  
Turnover: Controlled via trading costs and rebalance threshold

## Macro Regime Adjustment

Macroeconomic variables are not direct signals but inform risk regime filters and factor rotation. Example: shift from momentum to quality in high-volatility, high-inflation regimes.

## Data Sources

Price data: Yahoo Finance (yfinance)  
Macro data: FRED (via pandas-datareader)  
Sentiment data: Proprietary NLP pipeline (planned)  
Storage: Local CSVs under /data/raw/equity and /data/raw/macro

## Tools and Infrastructure

Python (JupyterLab for research, VS Code for production)  
Libraries: pandas, numpy, scikit-learn, xgboost, mlfinlab, matplotlib  
Repository structure:
project/
├── data/raw/equity/  
├── data/raw/macro/  
├── notebooks/  
├── src/  
└── README.md

## Next Steps

- Backtest signal on top 50–100 Russell 1000 names
- Validate Sharpe, drawdown, turnover under different factor weight schemes
- Implement dynamic factor weighting (HMM or ML-based)
- Expand to full universe and evaluate live-paper performance
