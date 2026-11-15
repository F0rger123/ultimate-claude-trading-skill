"""Plain-English explanations of each strategy, for the phone's account detail screen.

Written for the owner, not for a quant: what it watches, when it buys or sells, when it gets out, what
protects it, why it might work, and when it struggles. Strategies from the research bank use the bundle's
own written rules (research/strategy_bank/2026-11-13/strategies_40.json).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPLAIN = {
    "mtf_quick": {
        "summary": "Your own method. It only trades when four chart timeframes (1 hour, 30, 15 and 5 minutes) all "
                   "point the same way, and volume confirms.",
        "entry": "Each timeframe gets a SuperTrend reading (up or down); SuperTrend stands in for your TradingView "
                 "indicator until you send its name. On the 5-minute bar where all four agree for the first time, "
                 "and volume is above its 20-bar average, it buys (all up) or sells short (all down).",
        "exit": "Gets out when the 15-minute reading flips against the trade.",
        "stop": "A stop 1.5 x the 15-minute ATR away (ATR is the average bar size), so a normal wiggle does not "
                "knock it out but a real reversal does.",
        "why": "When every timeframe agrees, a move is usually backed by real buying or selling, so it tends to keep "
               "going for a while. Most trades lose a little; a few catch a big run.",
        "struggles": "Choppy, sideways markets: the timeframes keep agreeing and disagreeing, so it pays fees on many "
                     "small losers. Its two-year backtest lost money after costs. Your sub-strategies test your fix: "
                     "follow the bigger timeframes in chop and ignore signals that appear and vanish.",
    },
    "ema_pullback": {
        "summary": "Buys dips inside an uptrend (and sells rallies inside a downtrend), with a fixed profit target.",
        "entry": "Trend = the 50-bar average above the 200-bar average. In an uptrend it waits for a bar that dips to "
                 "the 20-bar average and closes back above it, green; mirror image for downtrends.",
        "exit": "Takes profit at 2 x the risk (2R), or the stop.",
        "stop": "A multiple of ATR below entry (the average bar size).",
        "why": "Trends rarely move in a straight line; buying the pause instead of the breakout gets a better price "
               "and a clear place for the stop.",
        "struggles": "Trend changes: the 'dip' turns into a real drop and the stop is hit.",
    },
    "ema_pullback_1h": None,  # same as ema_pullback, on 1-hour bars
    "rsi2_reversion": {
        "summary": "Buys sharp short-term dips in an uptrend and sells sharp pops in a downtrend, expecting a quick "
                   "snap back.",
        "entry": "On 15-minute bars: RSI(2), a very fast 'how stretched is it' gauge, falls below 10 while price is "
                 "above the 1-hour 200 average (buy), or rises above 90 below it (sell).",
        "exit": "When price crosses back over its 5-bar average, usually within hours.",
        "stop": "2 x the 15-minute ATR.",
        "why": "Very short drops inside a bigger uptrend often bounce. It wins often but each win is small.",
        "struggles": "Fees: wins are small, so costs eat a big share. A few large losses can wipe out many wins.",
    },
    "donchian_breakout": {
        "summary": "Buys when price breaks above its recent range (and sells below it), only in the direction of the "
                   "1-hour trend.",
        "entry": "The bar closes above the highest high of the last N bars (or below the lowest low), and the 1-hour "
                 "50 average agrees with the direction.",
        "exit": "When price falls back through the half-length channel (the N/2-bar low for longs).",
        "stop": "A multiple of ATR from entry.",
        "why": "Breakouts from a range often start new moves; the classic 'Turtle' idea.",
        "struggles": "False breakouts in ranging markets.",
    },
    "donchian_1h": None, "donchian_4h": None,
    "trend_ensemble": {
        "summary": "The slow trend follower the evidence supports most. It looks at five look-backs (20 to 120 days) "
                   "and only trades when most of them agree.",
        "entry": "Each day, each look-back votes up (today's close above the close that many days ago) or down. "
                 "When 60% or more agree, it goes long or short.",
        "exit": "When the votes drop back below the threshold, or the stop.",
        "stop": "3 x the 20-day ATR.",
        "why": "Time-series momentum: trends in many markets have persisted for over a century of data, and crypto "
               "trends strongly.",
        "struggles": "Sharp reversals and long sideways stretches. It trades a few times a month, so it is quiet most "
                     "days. In a crash it makes no new entries; in choppy or jumpy markets it trades half size.",
    },
    "vol_managed_trend": {
        "summary": "The same five-look-back trend vote, but it shrinks position size when the market gets wild.",
        "entry": "Votes from 20, 40, 60, 90 and 120 days; long at 60% agreement or more, short likewise.",
        "exit": "Votes fall below the threshold, the stop, or a crisis.",
        "stop": "3 x the 20-day ATR. Crisis rule: a 7-day drop of 18% or more, or 30% below the 30-day high, closes "
                "longs and blocks new ones.",
        "why": "Same trend edge, with steadier risk: big-volatility periods are where trend followers give back gains.",
        "struggles": "Quick V-shaped reversals.",
    },
    "vol_filtered_breakout": {
        "summary": "Daily breakouts to new 20- or 55-day highs or lows, skipped when the market is already unusually "
                   "wild.",
        "entry": "The daily close beats the prior N-day high (long) or low (short), and 20-day volatility is not in "
                 "its top fifth of the last 180 days.",
        "exit": "The opposite, shorter channel (10 or 20 days), or the stop.",
        "stop": "3 x the 20-day ATR.",
        "why": "New highs and lows in crypto tend to keep going; filtering out the wildest periods avoids many "
               "blow-off reversals.",
        "struggles": "Ranges with repeated false breaks.",
    },
    "weekly_strength_rotation": {
        "summary": "Each Monday it holds the strongest of BTC, ETH and SOL over the last 90 days, and nothing else.",
        "entry": "On Monday, ranks the three coins by their 90-day return and buys the leader.",
        "exit": "The next Monday, if another coin has taken the lead, or the stop.",
        "stop": "3 x the 20-day ATR.",
        "why": "Cross-sectional momentum: the coin that has led recently tends to keep leading (Liu, Tsyvinski and "
               "Wu, Journal of Finance 2022).",
        "struggles": "Leadership changes quickly; spot fees (0.9% a side) are high. It only trades on Mondays.",
    },
    "scalp10": {
        "summary": "A demonstration scalper: trades about every 10 minutes. Retired: fees beat it.",
        "entry": "Follows the 5-minute EMA 9/21 direction on any bar that closes the same way.",
        "exit": "After about 10 minutes, at a 1 x ATR target, or the stop.",
        "stop": "1.5 x the 5-minute ATR.",
        "why": "There was no expected edge; it existed so you could watch frequent trading.",
        "struggles": "Every trade pays about 0.16% in fees and slippage; 159 trades a day lost 1.6% in a day.",
    },
    "vwap_reclaim": {
        "summary": "US-session trades when price crosses back over the day's average price (VWAP) with volume.",
        "entry": "Between 8 AM and 3 PM Eastern, with the 1-hour trend: the 5-minute close crosses back over VWAP and "
                 "volume is 1.2 x normal.",
        "exit": "2R target, the stop, or the end of the UTC day.",
        "stop": "2 x the 5-minute ATR.",
        "why": "A common day-trading setup in stocks.",
        "struggles": "Crypto trades 24/7, so the 'day' resets at an arbitrary time and VWAP means less. Retired.",
    },
    "tsmom_daily": {
        "summary": "Daily time-series momentum: long when today's close is above the close N days ago, short when "
                   "below.",
        "entry": "Direction of the N-day return.", "exit": "When that direction flips.", "stop": "A multiple of ATR.",
        "why": "Moskowitz, Ooi and Pedersen (2012).", "struggles": "Choppy markets.",
    },
}
for k, v in (("ema_pullback_1h", "ema_pullback"), ("donchian_1h", "donchian_breakout"),
             ("donchian_4h", "donchian_breakout")):
    EXPLAIN[k] = EXPLAIN[v]

# research-bank strategies: index (1-based rank) into the bundle's strategies_40.json
BUNDLE = {"lib_tsmom_atr": 1, "lib_return_vote": 2, "lib_daily_ema_cross": 6, "lib_daily_roc": 11,
          "lib_closing_range_breakout": 17, "lib_tail_candle": 25, "lib_month_boundary": 34,
          "lib_4h_volume_donchian": 7, "lib_4h_atr_trail": 8, "lib_4h_ema_reclaim": 9, "lib_4h_bb_squeeze": 13,
          "lib_weekend_break": 30, "lib_1h_ema50_reclaim": 4, "lib_1h_rsi_reset": 10, "lib_1h_atr_expansion": 14,
          "lib_1h_macd": 16, "lib_1h_adx_cross": 18, "lib_weekday_1h_breakout": 22, "lib_1h_roc_volcap": 24,
          "lib_1h_rsi2_daily": 31, "lib_us_hour_follow": 32, "lib_15m_trend_resume": 15, "lib_15m_range_break": 19,
          "lib_5m_impulse": 20, "lib_5m_volume_break": 33, "lib_overlap_range_break": 21}
_BANK = None


def _bank():
    global _BANK
    if _BANK is None:
        p = os.path.join(ROOT, "research", "strategy_bank", "2026-11-13", "strategies_40.json")
        try:
            with open(p, encoding="utf-8") as f:
                _BANK = json.load(f)
        except (OSError, ValueError):
            _BANK = []
    return _BANK


def explain(cls):
    """Explanation dict for a strategy class (always returns something)."""
    e = EXPLAIN.get(cls.id)
    if e:
        return dict(e, source=getattr(cls, "source", ""))
    k = BUNDLE.get(cls.id)
    b = _bank()
    if k and k <= len(b):
        s = b[k - 1]
        return {"summary": s.get("why_it_should_work", ""),
                "entry": "Long: %s Short: %s" % (s.get("entry_long", ""), s.get("entry_short", "")),
                "exit": s.get("exit", ""), "stop": s.get("stop", "") + (" Target: %s" % s["target"]
                                                                         if s.get("target") not in (None, "", "none") else ""),
                "why": s.get("why_it_should_work", ""), "struggles": s.get("fails_when", ""),
                "source": "Research bank 2026-11-13 (designed by deep research, not backtested there). Evidence: " +
                          "; ".join(e.get("source", "") for e in s.get("evidence", [])[:3])}
    doc = (cls.__doc__ or "").strip()
    return {"summary": doc.split("\n")[0], "entry": doc, "exit": "", "stop": "", "why": "", "struggles": "",
            "source": getattr(cls, "source", "")}
