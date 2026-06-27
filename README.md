# EdgeOne ORB

Private Streamlit dashboard for a **QQQ opening range breakout (ORB)** playbook.

- **Manual Mode** — type all inputs yourself (original v0.1 behavior).
- **Stage 2A: Live Data Mode** — pull recent **QQQ** and **SPY** intraday bars from **Alpaca** (`alpaca-py`) to fill opening range, last price, VWAPs, and VWAP/SPY confirmation flags. **Read-only:** no orders, no execution.
- **Stage 2B: Paper trading** — when the decision is **TRADE ALLOWED**, you can optionally send a **simulated** **QQQ** market order (**day** time-in-force) to your **Alpaca paper** account after you tick a confirmation checkbox. Order size is **capped** using paper **buying power** and a **max buying power usage %** so oversized orders are blocked before they reach Alpaca. **No live trading**, no automation, no webhooks.
- **Stage 3A: Historical backtesting** — download past **1-minute** **QQQ** and **SPY** bars over a date range, replay a simplified ORB + filter + exit model, and summarize performance (no ML, no auto-trading).

## What it does

- Captures your opening range (manual or from Alpaca), context toggles, and a trade plan (entry, stop, target).
- Computes position sizing from account risk and per-share risk.
- Scores the setup out of **100** and labels the decision: **TRADE ALLOWED**, **WATCH ONLY**, or **NO TRADE**.
- Optionally appends a snapshot to `signals.csv`.
- Optionally submits a **paper-only** QQQ order (Stage 2B) and logs fills metadata to `paper_orders.csv`.
- Optionally runs **Stage 3A** historical replay and writes `backtest_trades.csv` with per-trade stats and summary charts on the same page.

## Alpaca API keys (Stages 2A & 2B)

1. Copy `.env.example` to `.env` in the **same folder as `app.py`** (project root).
2. In the [Alpaca dashboard](https://app.alpaca.markets/), open **Paper Trading** and copy your **Paper** **API Key ID** and **Secret Key** (recommended for this project).
3. Paste them into `.env`:

```bash
ALPACA_API_KEY=paste_your_key_here
ALPACA_SECRET_KEY=paste_your_secret_here
```

**Paper vs live:** Alpaca issues **different** keys for paper vs live. **Market data** (Stage 2A) and **paper orders** (Stage 2B) should use your **paper trading** keys. The trading client in `broker.py` is created with **`paper=True` only** — it never points at the live trading API.

If the keys are missing, the app shows: **“Alpaca keys not found. Add them to a .env file.”** (and Live Data Mode falls back to manual OR / price fields until data loads; the **Send Paper Trade** button stays disabled).

## Setup

Create a virtual environment (recommended), then install and run:

```bash
cd /Users/brandongarrison/Desktop/edgeone-orb
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

## Live Data Mode (Stage 2A)

When **Live Data Mode** is selected, the app:

1. Loads `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` from the environment (via `python-dotenv` and your `.env` file).
2. Fetches today’s **1-minute** **QQQ** and **SPY** bars for the **regular session** (from **9:30 AM ET** through the current time, capped at **4:00 PM ET**).
3. Computes **QQQ opening range** high and low from bars whose **open time** falls in **9:30–9:45 AM Eastern** (first 15 minutes).
4. Derives **OR midpoint**, **OR size**, and **last QQQ close** from that data.
5. Computes **session VWAP** for QQQ and SPY from typical price × volume cumulatively from the **9:30** open through the latest bar.
6. Shows whether **QQQ** is **above / below / at** VWAP, and whether **SPY** confirms **Long** (price **above** SPY VWAP) or **Short** (price **below** SPY VWAP).
7. If the market is closed, keys are missing, or Alpaca returns no usable bars, you get a **clear message** instead of a crash; you can still use the **fallback** OR / QQQ inputs.

Use **Refresh market data** to pull again (for example after fixing `.env`).

## Paper trading (Stage 2B)

### How to run Stage 2B

Use the same install and command as above (`pip install -r requirements.txt`, then `streamlit run app.py`). Stage 2B is a **section on the main page**, not a separate mode: **Manual Mode** and **Live Data Mode** are unchanged.

### How to confirm you are in paper mode

- Put **only** [Alpaca Paper Trading](https://app.alpaca.markets/paper/dashboard/overview) **API keys** in `.env`.
- In code, orders go through `TradingClient(..., paper=True)`, which uses Alpaca’s **paper** REST host (`broker.py`). There is **no** code path that sets `paper=False`.

### What the **Send Paper Trade** button does

It appears only when **Decision** is **TRADE ALLOWED**. Above it you will see: *“This submits a simulated paper trade only. No live money is used.”*

1. The app loads your **Alpaca paper account** (buying power, cash, portfolio value). Use **Refresh paper account** if you change keys or want fresh balances.
2. Set **Max buying power usage percent** (default **25%**). Example: buying power **$200,000** and max usage **25%** → max allowed trade value **$50,000** before converting to whole shares.
3. The app computes **risk-based position size** (from your risk % and stop), **buying-power capped size** = `floor((buying_power × max_usage%) / entry)`, and **final paper order size** = `min(risk-based, cap)`. **Estimated order cost** = `final_order_size × entry`.
4. You must tick **“I confirm I want to submit this simulated paper-only order.”**
5. **Send Paper Trade** stays disabled until: keys exist, paper account loaded, **risk-based size ≥ 1**, **final size ≥ 1**, **estimated cost ≤ buying power**, direction is **Long** or **Short**, and the checkbox is checked. If **final** is below **1** share, you will see: *“Final paper order size is below 1 share.”*
6. On click, the app submits a **market**, **day** order for **QQQ** at **final** size (**BUY** for Long, **SELL** for Short).

Nothing is sent if the decision is not **TRADE ALLOWED**, if **risk-based** size is **0**, if **final** size is **0**, if **estimated cost** exceeds **buying power**, if keys are missing, or if the paper account cannot be loaded.

### Buying-power protection (refinement)

- **Goal:** stop Alpaca from rejecting paper orders because notional exceeds what the paper account can support.
- **Mechanism:** `broker.compute_paper_order_sizing()` in `broker.py` applies the cap; `app.py` shows all intermediate numbers and blocks submit when checks fail.
- **`paper_orders.csv`** now also logs: `max_buying_power_usage_percent`, `buying_power`, `cash`, `portfolio_value`, `risk_based_size`, `buying_power_cap_size`, `final_order_size`, `estimated_order_cost` (plus the existing order fields). If you have an **old** `paper_orders.csv` from before these columns, **rename or delete** it so the next write creates a matching header row.

### How to verify the order in Alpaca

1. Log in to Alpaca and open the **Paper Trading** dashboard (not Live).
2. Go to **Orders** (or **Activity**) and look for the new **QQQ** order by **order id** shown in the Streamlit success message.
3. Open **`paper_orders.csv`** in the project folder to match the log row to the dashboard.

## Historical backtesting (Stage 3A)

### What Stage 3A does

- Pulls **QQQ** and **SPY** **1-minute** bars from Alpaca for a **start date → end date** range (Eastern session days).
- For each calendar day with data, defines the **opening range** from the first **15 minutes** (9:30–9:45 ET), then scans later bars for **breakout signals**:
  - **Long:** first bar (after the OR window) where **QQQ close > OR high**, with optional **QQQ close > session VWAP**, optional **SPY close > SPY session VWAP**, optional **volume** vs OR-period average.
  - **Short:** first bar where **QQQ close < OR low**, with optional **QQQ close < VWAP**, optional **SPY close < SPY VWAP**, optional **volume** filter.
- **Entry** = **close** of the signal bar; **exits** are simulated on subsequent bars (gap-aware open first): **stop** before **target** if both could hit; otherwise **end-of-day** exit at the last bar **close**.
- **Stops / targets:** configurable **opposite OR side**, **OR midpoint**, or **fixed %** off entry; **R target** scales the target distance off **entry–stop** risk.
- **Sizing:** `floor((account × risk%) / risk_per_share)` whole shares (no leverage model beyond notional).
- Writes **`backtest_trades.csv`** and shows **summary metrics** plus **equity curve** and **R histogram** in Streamlit.

### How backtesting works (high level)

1. Scroll to **Stage 3A: Historical Backtesting** (same `streamlit run app.py` session).
2. Pick **start** / **end** dates and strategy parameters (risk %, R target, stop style, max trades per day, toggles, direction filter).
3. Click **Run Backtest**. Watch the progress messages (**Loading historical data…**, **Running historical replay…**, **Generating statistics…**).
4. Inspect metrics and charts; open **`backtest_trades.csv`** for the full trade list.

### How to test Stage 3A manually

1. Ensure `.env` has valid Alpaca keys (same as Stages 2A/2B).
2. Run `streamlit run app.py`, scroll to **Stage 3A: Historical Backtesting**.
3. Choose a **short** window first (e.g. last **5–10 trading days**) so the run finishes quickly.
4. Leave defaults or relax **VWAP/SPY** toggles to get more trades; click **Run Backtest**.
5. Confirm the three progress messages appear, then check metrics, **equity** line chart, **R** bar chart, and the **`backtest_trades.csv`** file on disk.

### Limitations (important)

- **Not** a tick-accurate simulator: **1-minute** bars only; intrabar path (stop vs target) is a **simplified rule** (open → low/high checks).
- **Slippage, commissions, borrow fees, halts, partial fills, and margin** for shorts are **not** modeled; P/L is **idealized** on mid-price assumptions.
- **Alpaca data** availability, **splits**, and **calendar** quirks can affect older ranges; empty ranges return a clear error.
- Past results **do not** guarantee future performance. Stage 3A does **not** place live or paper orders.

## Scoring (unchanged logic)

| Bucket | Points | How it is decided |
| --- | ---: | --- |
| Clean OR break | 20 | **Long** and QQQ price **above** OR high, or **Short** and price **below** OR low |
| VWAP aligned | 15 | “Yes” (manual) or derived in Live Data Mode from QQQ vs VWAP for your direction |
| SPY confirmed | 15 | “Yes” (manual) or derived in Live Data Mode from SPY vs VWAP for your direction |
| Volume confirmed | 15 | “Yes” (still **manual** in Live Data Mode) |
| Risk/reward quality | 20 | Tiers from **R multiple** (stronger R → more points) |
| Time quality | 10 | From the **US/Eastern** clock during **regular session** (weekdays 9:30–16:00 ET) |
| No warning signs | 5 | Only if **none** of the dashboard warning checks fire |

**Decision:** if **R** is **below 1.5** → **NO TRADE**. Otherwise: score **≥ 75** → **TRADE ALLOWED**; **65–74** → **WATCH ONLY**; **below 65** → **NO TRADE**.

## Sample test values (Manual Mode)

Use these in the inputs to see how the dashboard behaves. (Scores include a **time-quality** component from the **US/Eastern** clock during **regular session**; outside market hours that piece may be lower.)

### 1) Valid long trade (typically TRADE ALLOWED)

| Field | Value |
| --- | --- |
| Account size | `100000` |
| Risk percent | `1` |
| OR high | `450.00` |
| OR low | `448.00` |
| Current QQQ price | `450.60` *(above OR high → “clean OR break” for Long)* |
| Direction | `Long` |
| VWAP aligned | `Yes` |
| SPY confirmed | `Yes` |
| Volume confirmed | `Yes` |
| Entry | `450.25` |
| Stop | `449.50` |
| Target | `452.00` |

Expect strong **R multiple** (about **2.3R** with these numbers) and **no checklist warnings** if stops/targets stay as above.

### 2) Watch-only setup (typically WATCH ONLY)

| Field | Value |
| --- | --- |
| Account size | `50000` |
| Risk percent | `0.5` |
| OR high | `450.00` |
| OR low | `448.00` |
| Current QQQ price | `449.50` *(inside the opening range → no “clean OR break” points)* |
| Direction | `Long` |
| VWAP aligned | `Yes` |
| SPY confirmed | `Yes` |
| Volume confirmed | `Yes` |
| Entry | `450.00` |
| Stop | `448.00` |
| Target | `455.00` |

**R** is **2.5** (well above the minimum). You still miss the **clean OR break** bonus, so the total score typically lands in the **mid‑60s** → **WATCH ONLY** (works the same on weekends because it does not rely on the clock-based time-quality points).

### 3) No-trade setup (typically NO TRADE)

| Field | Value |
| --- | --- |
| Account size | `25000` |
| Risk percent | `1` |
| OR high | `450.00` |
| OR low | `448.00` |
| Current QQQ price | `450.60` |
| Direction | `Long` |
| VWAP aligned | `Yes` |
| SPY confirmed | `Yes` |
| Volume confirmed | `Yes` |
| Entry | `450.00` |
| Stop | `449.50` |
| Target | `450.40` |

**Target is too close to entry** → **R multiple** falls **below 1.5**, which forces **NO TRADE** by rule (even if other checklist items look fine).

Alternate **low-score** example: keep **OR** the same but set **Current QQQ price** to **`449.00`** (inside the range), set **SPY / VWAP / Volume** to **No**, and use a tight target — the score will usually stay **under 65** → **NO TRADE**.

## Father's Hand: Day Trading Training OS

A **separate private training app** for beginner-friendly day trading education and practice.

**This is NOT live trading. This is NOT financial advice.** No real orders. No profit promises. Skill-building only.

### How to run

From the project folder (same venv as EdgeOne ORB):

```bash
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run fathers_hand_app.py
```

Your browser opens the training app. It runs on its own — you do not need to run `app.py` at the same time.

The main EdgeOne dashboard (`app.py`) still has a smaller **Stage 3H** Father's Hand section for historical setup quizzes. The full training OS is `fathers_hand_app.py`.

### What Father's Hand teaches

Ten step-by-step modules in plain language (~5th-grade reading level):

1. What is day trading? (buy, sell, long, short, risk, reward)
2. Candles and charts (body, wick, OHLC)
3. Trend vs chop (uptrend, downtrend, consolidation, fakeouts)
4. VWAP (buyers vs sellers)
5. Opening Range Breakout (first 15 minutes, OR high/low)
6. Volume and RVOL
7. Risk management (stop, target, R, position size)
8. Trade decision checklist (trend, VWAP, SPY, RVOL, OR, no-trade rules)
9. Paper trading simulator (Long / Short / Watch / No Trade)
10. Review and journal

Plus: **Quiz engine**, **Replay Trainer**, **Risk Calculator**, and **Journal**.

### How to use it daily (~20–30 minutes)

1. **Home** — check lesson level, trader score, and stats.
2. **Lessons** — read one module.
3. **Quiz** — take that module's quiz for instant feedback.
4. **Replay Trainer** — practice one scenario (uses `environment_trades.csv` / `backtest_trades.csv` when available, plus built-in samples).
5. **Risk Calculator** — practice sizing and R math.
6. **Journal** — write why you took or skipped a setup, your risk, and whether you followed rules.

Repeat most weekdays. Review your journal weekly.

### How progress is scored

Your **Trader Skill Score** (0–100) blends:

| Input | Weight (approx.) |
| --- | --- |
| Quiz accuracy | 30% |
| Replay Trainer accuracy | 30% |
| Risk calculator practice | 20% |
| No-trade discipline (skipping bad setups) | 15% |
| Completed lessons + journal | 15% + small bonus |

**Labels:** Beginner → Developing → Consistent → Advanced → Elite-in-training

Progress saves to `fathers_hand_progress.json`. Journal entries append to `fathers_hand_journal.csv`.

### Training files

| File | Role |
| --- | --- |
| `fathers_hand_app.py` | Standalone Streamlit training UI (tabs: Home, Lessons, Quiz, Replay, Risk, Journal, Progress) |
| `fathers_hand.py` | Modules, quiz engine, replay grading, trader score, journal helpers |
| `fathers_hand_journal.csv` | Your practice log (created on first save) |
| `fathers_hand_progress.json` | Lesson completion and score stats |

## Files

| File | Role |
| --- | --- |
| `app.py` | Streamlit UI (mode selector, manual + live flows) |
| `data_provider.py` | Alpaca market data + OR / VWAP math (Stage 2A) |
| `broker.py` | Alpaca **paper-only** trading client + QQQ market orders + `paper_orders.csv` log (Stage 2B) |
| `backtester.py` | Stage 3A historical data, signals, simulation, analytics, `backtest_trades.csv` |
| `risk.py` | OR math, sizing, R multiple |
| `scoring.py` | Score, warnings, decision |
| `journal.py` | Append rows to `signals.csv` |
| `fathers_hand_app.py` | Father's Hand training OS (standalone Streamlit app) |
| `fathers_hand.py` | Training modules, quizzes, replay, scoring, journal |
| `.env.example` | Template for Alpaca keys |
| `.gitignore` | Ignores `.env`, venvs, bytecode |
| `requirements.txt` | Python dependencies |

## Disclaimer

Educational tooling only. Not financial advice. You are responsible for your own trading decisions.
