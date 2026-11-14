"""Strategy lab: versions grown inside a strategy, so the desk prepares improvements before it needs them.

Paper only, and nothing here changes a running account. For each of the top accounts (the owner's own
method always included) the lab:
1. Diagnoses the strategy over the last year WITH costs: gross result before fees, fees and slippage paid,
   longs vs shorts, win rate, how often it trades. Plain-English lines explain why it loses or wins.
2. Grows versions inside it: one change at a time on top of the current best version (a new filter, a
   different stop, a higher-timeframe trend gate...). Each version is tested two ways:
   - the last 365 days with costs (no drawdown block, so the whole year is measured), and
   - a silent "shadow" run over the same days the real paper account has been running.
3. Keeps the 5 best versions, plus one that combines the two best changes.
4. Generations: when a version beats its parent by 5+ score points over the year, keeps at least half of
   the parent's shadow result, AND also beats the parent on the year before (a holdout year no version was
   chosen on, so a lucky fit to one year is caught), it becomes the base for the next generation, so good ideas are grown further.
   Qualified versions join the weekly shake-up as "v2" candidates; they never replace the running account.
Score = 1-year return % minus half the worst drop %. One year is one market path: a lab winner is a lead.
"""
import json
import os
import time

from . import paper as PA
from . import portfolio as P

DAY = 86400
TOP = 3            # accounts studied per run (plus the owner's own method)
KEEP = 5           # versions shown per strategy
MIN_GAIN = 5.0     # score points over the parent to become the next generation's base
OWNER = "mtf_quick"

PHRASE = {
    "adx_min": "only trades when trend strength (ADX) is at least {v}, skipping choppy markets",
    "trend_gate_h": "only trades in the direction of the {tf} trend",
    "min_atr_frac": "skips quiet markets where bars are under {pct} of price, so moves can beat fees",
    "exit_confirm": "waits for {v} 15-minute bars against it before exiting, fewer whipsaw exits",
    "vol_k": "needs volume at least {v}x its normal level",
    "stop_atr": "stop at {v}x ATR",
    "weekday_only": "no new trades on weekends",
    "st_mult": "SuperTrend sensitivity {v}",
    "tgt_r": "profit target {v}R",
    "daily_fast_ema": "the daily trend must agree (daily EMA {v} above or below EMA 50)",
    "lo": "dip threshold RSI {v}",
}


def phrase(k, v):
    t = PHRASE.get(k)
    if not t:
        return "%s %s" % (k.replace("_", " "), v)
    tf = {4: "4-hour", 24: "daily"}.get(int(v) if isinstance(v, (int, float)) else 0, "%s-hour" % v)
    return t.format(v=v, tf=tf, pct="%.1f%%" % (100 * float(v)) if isinstance(v, (int, float)) else v)


def _book(spec, params):
    b = {"id": "lab", "cls": spec["cls"], "mode": spec["mode"], "equity": spec["equity"],
         "cadence": spec["cadence"], "params": params, "extra": spec.get("extra") or {}}
    for k in ("risk", "pos_lev", "gross_lev", "skip"):
        if spec.get(k) is not None:
            b[k] = spec[k]
    return b


def measure(spec, params, markets, now, start_paper):
    """1-year result with costs (no drawdown block) and the shadow result since the paper start."""
    b = _book(spec, params)
    cfg = PA._cfg(b)
    cfg.dd_policy = False
    try:
        r = P.run(markets, PA._variants(markets, b, params), cfg, start_t=now - 365 * DAY, end_t=now,
                  close_at_end=True)
        s = P.run(markets, PA._variants(markets, b, params), PA._cfg(b), start_t=start_paper, end_t=now,
                  close_at_end=False)
        # holdout: the year BEFORE the tuning year, never used to choose a version
        h = P.run(markets, PA._variants(markets, b, params), cfg, start_t=now - 730 * DAY, end_t=now - 365 * DAY,
                  close_at_end=True)
    except Exception as e:
        return {"error": str(e)[:200]}
    tr, curve = r["trades"], r["curve"]
    if not curve:
        return None
    peak, dd = b["equity"], 0.0
    for _, e in curve:
        peak = max(peak, e)
        dd = max(dd, (peak - e) / peak if peak else 0.0)
    ret = 100.0 * (curve[-1][1] / b["equity"] - 1)
    sh = (s["curve"][-1][1] - b["equity"]) if s["curve"] else 0.0
    hpk, hdd = b["equity"], 0.0
    for _, e in h["curve"]:
        hpk = max(hpk, e)
        hdd = max(hdd, (hpk - e) / hpk if hpk else 0.0)
    hret = 100.0 * (h["curve"][-1][1] / b["equity"] - 1) if h["curve"] else None
    return {"ret_pct": round(ret, 2), "max_dd_pct": round(100 * dd, 2), "score": round(ret - 50 * dd, 2),
            "trades": len(tr), "wins": sum(x["pnl"] > 0 for x in tr),
            "gross": round(sum(x["gross"] for x in tr), 2),
            "fees": round(sum(x["fees"] + x["funding"] for x in tr), 2),
            "long_pnl": round(sum(x["pnl"] for x in tr if x["side"] == 1), 2),
            "short_pnl": round(sum(x["pnl"] for x in tr if x["side"] == -1), 2),
            "hours": round(sum(x["hours"] for x in tr) / len(tr), 1) if tr else None,
            "shadow_pnl": round(sh, 2), "shadow_trades": len(s["trades"]) + len(s["open"]),
            "prior_ret_pct": None if hret is None else round(hret, 2),
            "prior_score": None if hret is None else round(hret - 50 * hdd, 2), "prior_trades": len(h["trades"])}


def diagnose(name, m):
    """Plain-English reasons from a 1-year measurement."""
    if not m or "error" in m:
        return []
    out = ["Over the last year with fees and slippage: %+.1f%%, worst drop %.1f%%, %d trades (%d won)." % (
        m["ret_pct"], m["max_dd_pct"], m["trades"], m["wins"])]
    g, f = m["gross"], m["fees"]
    out.append("Before costs the trades made %+.0f dollars; fees, slippage and funding cost %.0f." % (g, f))
    if f > abs(g) and m["ret_pct"] < 0:
        out.append("Costs are the main problem: it trades often with tight stops, so positions are large next to "
                   "the risk and each round trip pays fees on that size.")
    elif g < 0:
        out.append("The signals themselves lost before costs: the entries are on the wrong side too often.")
    if m["trades"] and m["wins"] / m["trades"] < 0.3:
        out.append("It wins under 30%% of trades, so it depends on a few big winners (%d of %d won)." % (
            m["wins"], m["trades"]))
    lp, sp = m["long_pnl"], m["short_pnl"]
    if (lp < 0) != (sp < 0):
        out.append("Longs %+.0f vs shorts %+.0f: it only made money on one side, so it depends on the market's "
                   "direction." % (lp, sp))
    if m["ret_pct"] > 0:
        out.append("Positive over the year: %s held up through a full year of markets." % name)
    return out


def ideas(spec, base):
    cls = spec["cls"]
    grid = {k: list(v) for k, v in (getattr(cls, "grid", {}) or {}).items()}
    for k, vs in (getattr(cls, "improve", {}) or {}).items():
        grid[k] = list(dict.fromkeys(grid.get(k, []) + list(vs)))
    full = dict(getattr(cls, "defaults", {}), **base)
    out = []
    for k in sorted(grid):
        for v in grid[k]:
            if full.get(k) != v:
                out.append((k, v))
    return out


def path(state_dir):
    return os.path.join(state_dir, "paper", "labs.json")


def load(state_dir):
    try:
        with open(path(state_dir), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def run(state_dir, books, markets_for, now=None, log=print):
    """books: [(spec, book)] already loaded. markets_for(cadence) -> markets covering the last year."""
    now = int(now or time.time())
    mem = load(state_dir)
    labs, challengers = {}, []
    ranked = sorted(books, key=lambda sb: -sb[1]["pnl"])
    chosen = [sb for sb in ranked if sb[0]["cls"].id == OWNER][:1]
    chosen += [sb for sb in ranked if sb not in chosen and not sb[0].get("protected")][:TOP]
    for spec, bk in chosen:
        cls = spec["cls"]
        markets = markets_for(spec["cadence"])
        parent_params = dict(spec.get("params") or {})
        if spec.get("report"):
            parent_params = PA.latest_params(spec["report"])[0]
        prev = mem.get(bk["id"], {})
        gen = prev.get("generation", 1)
        base = dict(prev.get("base_params") or parent_params)
        parent = measure(spec, parent_params, markets, now, bk["start"])
        if not parent or "error" in parent:
            log("lab %s: parent failed %s" % (bk["id"], (parent or {}).get("error")))
            continue
        base_m = parent if base == parent_params else measure(spec, base, markets, now, bk["start"])
        rows = []
        for k, v in ideas(spec, base):
            p2 = dict(base, **{k: v})
            m = measure(spec, p2, markets, now, bk["start"])
            if m and "error" not in m:
                rows.append({"change": {k: v}, "why": phrase(k, v), "params": p2, "test": m})
        rows.sort(key=lambda r: -r["test"]["score"])
        top = rows[:KEEP]
        good = [r for r in rows if r["test"]["score"] > base_m["score"]]
        if len(good) >= 2 and list(good[0]["change"])[0] != list(good[1]["change"])[0]:
            p3 = dict(base, **good[0]["change"], **good[1]["change"])
            m = measure(spec, p3, markets, now, bk["start"])
            if m and "error" not in m:
                top.append({"change": dict(good[0]["change"], **good[1]["change"]),
                            "why": good[0]["why"] + ", and " + good[1]["why"], "params": p3, "test": m,
                            "combined": True})
        top.sort(key=lambda r: -r["test"]["score"])
        best = top[0] if top else None
        # next-generation base: the best-scoring version that beats the parent over the year by MIN_GAIN and
        # keeps at least half of the parent's shadow result (or matches it when the parent is losing)
        floor = 0.5 * parent["shadow_pnl"] if parent["shadow_pnl"] > 0 else parent["shadow_pnl"]
        def holds(r):  # must also beat the parent on the year before, which no version was chosen on, and
            # actually trade there: a filter that cannot warm up in the holdout proves nothing
            a, b0 = r["test"].get("prior_score"), parent.get("prior_score")
            if a is None or b0 is None:
                return False
            need = min(10, max(3, parent.get("prior_trades", 0) // 4))
            return r["test"].get("prior_trades", 0) >= need and a >= b0
        ok = [r for r in top if r["test"]["score"] >= parent["score"] + MIN_GAIN and r["test"]["shadow_pnl"] >= floor
              and holds(r)]
        promoted = bool(ok)
        if ok:
            best = ok[0]
        labs[bk["id"]] = {"generation": gen, "name": bk["name"], "parent": parent, "base_params": base,
                          "diagnosis": diagnose(bk["name"], parent), "versions": top, "promoted": promoted,
                          "t": now}
        if promoted:
            mem[bk["id"]] = {"generation": gen + 1, "base_params": best["params"], "t": now}
            challengers.append({"kind": "lab", "params": best["params"], "skip": spec.get("skip") or [],
                                "why": "lab generation %d: %s" % (gen, best["why"]), "test": best["test"],
                                "parent": bk["id"], "parent_name": bk["name"], "cls": cls.id,
                                "cadence": spec["cadence"], "parent_test": parent})
        log("lab %-26s gen %d  parent %+6.1f%%/yr  best %s %+6.1f%%/yr%s" % (
            bk["id"], gen, parent["ret_pct"], best["why"][:50] if best else "-",
            best["test"]["ret_pct"] if best else 0, "  -> next generation" if promoted else ""))
    with open(path(state_dir) + ".tmp", "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=1)
    os.replace(path(state_dir) + ".tmp", path(state_dir))
    return labs, challengers
