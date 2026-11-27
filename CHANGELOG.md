# Changelog

## 2026-11-27: realistic spot fees, $100 pilot mirror, phone check-in

- Spot fees raised to 1.20% taker / 0.60% maker, the highest published Coinbase Advanced rate for the lowest volume tier (published 2026 figures range from 0.60% to 1.20% taker). Perp fees stay at 0.06% or $0.15 per contract, above every published rate.
- The pilot mirror is now $100 and runs daily momentum (90 days, 2.5 ATR stop). Its old trend ensemble lost money in both test years at spot fees; this was the only kind of strategy that stayed positive at $100 with these fees. It buys only, so it waits while coins fall.
- The phone API records which device last connected (device name and time, never the token) in state/app/clients.json.

## 2026-11-25: paper accounts no longer freeze after a 10% dip

- The per-account drawdown brake on paper accounts is off (owner's request). It froze the owner's original account on Nov 20 for good, because nothing ever resumed it, so it missed every trade after. Paper accounts replay from their start, so the account's result now includes those trades.
- The owner's drawdown rules (7.5% / 10% / 15%) are unchanged and still guard the real-money side, and the whole paper desk still turns the kill switch on at 15%.

## 2026-11-25: full audit, equal-start replay, year-check fix

- Every account replayed from the desk's first day (Nov 9) so new accounts are compared fairly with the owner's original. The original is still first over that window (+35% in the replay), but loses 73% and 89% over the last two full years.
- Fixed the weekly rotation's one-year check: it ran with the paper drawdown brake on, so the first 10% dip froze the test for the rest of the year. It passed a 1h+30m swing that loses 41% a year and rejected v2 versions that make 50-90%. The check now runs without the brake (as the lab already did). New test.
- Retired the 1h+30m swing (added by the faulty check) and the 1h EMA pullback (long-term loser). Added two chop accounts that only trade strong trends (ADX 30+), which improved all three chop accounts in both test years.

## 2026-11-19: sweep of every paper account, losing chop versions removed
- Backtested all 31 accounts with costs on the last year, the year before and the last 90 days.
- Removed at the owner's request: the plain chop version (0 of 10 paper trades won, -58% last year), the
  chop + 4h trend versions without the volume filter (weekdays, ADX 20, wide stop: 0 of 10 paper trades won
  between them), chop + 4h trend + volume (-3.5% last year, 38% worst drop) and the spot rotation (lost in
  every window).
- Lesson: the chop rule only helps on top of the v2 filters (1.8x volume, ADX 20, skip quiet markets, wide
  stop). Without the volume filter the confirmed entry comes late, after the move, and gets stopped out.
- Two new sub-strategies of the owner's method: v2 + chop rules (+49% / +15% / +16%) and v2 + 2-bar exit
  (+57% / +5% / +12%), last year / year before / last 90 days, with fees.
- Shake-up picks: a fast pick must also make money over the last year, every pick must have made money on
  its test, and no pick may copy a running account's settings.

## 2026-11-15: \$50,000 paper budget, owner's rules on paper, 20 new accounts
- `paper_total_usd` (default \$50,000) is split evenly across the paper accounts (the \$50 pilot mirror keeps
  its own \$50). Accounts are still simulated at \$10,000 and shown at their share: every trade and every
  percentage is unchanged, only dollar amounts scale.
- Paper accounts follow the owner's `risk_pct` (never above 1%) and `max_trades_per_day` (per account, from
  2026-11-15 on, so no past trade is removed).
- 20 new paper accounts picked by a two-year test with costs, grouped into categories (`category` in the
  roster); the owner's method family grows to 9.

## 2026-11-14: the owner's method gets a family
- MTFQuick: `entry_confirm` (agreement must hold k closed bars), `exit_tf` (exit on the 30m or 1h flip),
  `chop_mode` (after 2+ 1h flips in 24h, trade only 4h+1h agreement and exit on 1h). All off by default.
- Three sub-strategy paper accounts beside the protected original: chop rules; + 4h trend and 1.8x volume;
  + a 3.5x ATR stop. Account pages list the family (`family` in the roster, `/api/account`).

## 2026-11-14: lab, realistic costs, account detail
- `tradedesk/lab.py`: diagnoses the top strategies over a year with costs, grows versions one change at a
  time, checks each on the year before (holdout) and a shadow run since paper start, and carries winners
  into the next generation and the weekly shake-up.
- Costs: perp fee is now 0.06% or $0.15 per contract, whichever is larger; stop exits pay 0.04% slippage.
- `/api/account`: how each account trades (leverage, shorting, size, cost per trade), plain-English
  explanation, stats, splits and the lab. New `trend_gate_h` switch for higher-timeframe trend filters.

## 2026-11-13: strategy bank, first batch
- `tradedesk/library.py`: 26 researched strategies (daily momentum, 4h breakouts and trails, hourly pullbacks,
  volatility and seasonality rules, 15m/5m breakouts), untested until the desk tests them; they join the
  weekly shake-up pool. Pair trades and data-dependent ideas are parked.
- Winner improvements as off-by-default switches on EMA pullback and 4-timeframe alignment; the study tests
  them as v2 challengers.
- `indicators.py`: ADX, MACD. Fix: the study's weekday tag counted Fridays as weekends.

## 2026-11-13: study and improve
- `tradedesk/study.py`: tags every paper trade with its market context (session, weekday, trend, volatility,
  coin, side), reports where each account makes and loses money, and builds improved versions of winning
  accounts (one setting changed, or skipping a losing group), judged on data the parent never paper-traded.
- The weekly run studies first; qualified improvements compete for open slots as "v2" accounts.
- Only losing accounts can be cut. Family memory now counts running accounts too.
- `tradedesk/library.py` and `research/strategy_bank/` for researched strategies; `python -m tradedesk study`.

## 2026-11-09: weekly paper shake-up
- `tradedesk/rotation.py`: every Monday the desk ranks the paper accounts, retires the bottom three
  (after a 6-day fast / 27-day slow trial; the $50 pilot mirror is protected), tests up to three
  settings of every strategy family on recent data with costs, and starts the best three as new paper
  accounts. Retired results stay in the all-accounts total and feed a per-family memory.
- Paper accounts now live in `state/paper/roster.json`; retired ones in `state/paper/retired/`.
- `python -m tradedesk rotate` (`--dry-run`, `--force`), `GET /api/rotation`, skill `trading-rotation`.
- New `pb_fast_scalp10` account (trades about every 10 minutes, small size). Fast-account notes now
  state their real trade frequency.

## 2026-11-09: paper trading started
- `tradedesk/paper.py`: five paper books on the research portfolio engine, replayed hourly from a fixed
  start (2026-11-09 07:00 UTC). Same code as the backtest.
  - perp books ($10,000 each): trend ensemble, vol-managed trend, vol-filtered breakout
  - spot books: weekly rotation ($10,000) and a $50 spot pilot mirror
- `portfolio.run`: `close_at_end=False` keeps positions open for paper; `kill_at` flattens and blocks entries.
- The desk runs the paper books every hour. The phone API shows total paper equity and each book.

## 2026-11-09: Ultimate Claude Trading Skill
### Added
- **Accounting:** `tradedesk/portfolio.py`, a shared mark-to-market ledger (cash, positions, fees, signed
  funding, whole contracts, gross-exposure caps, drawdown tiers).
- **Statistics:** `tradedesk/metrics.py`
  - Sharpe, Sortino, Calmar, ES5, underwater time
  - hourly and daily drawdown on marked equity
  - block bootstrap, deflated Sharpe
- **Strategies:** `tradedesk/candidates.py`: vol-managed trend, vol-filtered breakout, weekly strength rotation.
- **Research:** `research/corrected_tournament.py`
  - leak-free walk-forward (1,095-day train / 180-day test)
  - benchmarks, risk-matched buy-and-hold
  - cost, risk and drawdown-policy stress
  - experiment registry
- **Reporting:** `research/summarize_corrected.py` (ranking with a deflated Sharpe across all trials) and
  `research/make_charts.py` (SVG evidence).
- **MNQ:** opening-range experiment (Pine v6, Python parity, synthetic tests).
- **Docs:** methodology, math, risk, setup, sources, funding, ORB, security, contributing.

### Changed
- **Desk:** owner drawdown tiers (7.5% warn → half risk, 10% block, 15% flatten + halt) on **marked**
  paper equity. Default risk is 0.5% per trade.
- **Reports:** old reports moved to `reports/legacy/` as HISTORICAL LEGACY RESULTS (closed-trade drawdown).

### Results
- 77 trials registered. All candidate/market pairs were positive OOS, but none is statistically proven
  (deflated Sharpe < 0.95). Spot versions are cost-fragile.

## 2026-11-07: initial release
- tradedesk engine, 8 Claude Code skills, blueprint, first tournaments.
