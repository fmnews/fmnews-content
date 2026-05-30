"""Fetch current cricket matches from CricAPI and write the result to
cricket.json in our GitHub-backed CMS schema. Runs from a GitHub Action
every 10 minutes — the app never touches CricAPI directly so the free
100-hits/day quota holds for the whole user base.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone


CRICAPI_BASE = "https://api.cricapi.com/v1/currentMatches"


def fetch_matches(api_key: str) -> list[dict]:
    url = f"{CRICAPI_BASE}?apikey={api_key}&offset=0"
    req = urllib.request.Request(url, headers={"User-Agent": "FMNewsApp-Cron/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"CricAPI HTTP {exc.code}: {exc.read().decode('utf-8', 'ignore')[:200]}")
        return []
    except Exception as exc:  # noqa: BLE001
        print(f"CricAPI error: {exc}")
        return []

    if payload.get("status") != "success":
        print(f"CricAPI status: {payload.get('status')} — {payload.get('reason', '')}")
        return []

    raw = payload.get("data") or []
    return raw


def normalize(raw_matches: list[dict]) -> list[dict]:
    """Map CricAPI's shape into the schema our Flutter app already reads."""
    out: list[dict] = []
    for m in raw_matches:
        teams = m.get("teamInfo") or []
        scores = m.get("score") or []
        team_a = teams[0] if len(teams) >= 1 else {}
        team_b = teams[1] if len(teams) >= 2 else {}

        # Pick the latest score row for each team — CricAPI returns one
        # entry per innings.
        def latest_for(name: str) -> str:
            relevant = [s for s in scores if name and name in (s.get("inning") or "")]
            if not relevant:
                return "Yet to bat"
            last = relevant[-1]
            runs = last.get("r")
            wkts = last.get("w")
            overs = last.get("o")
            if runs is None:
                return "Yet to bat"
            return f"{runs}/{wkts} ({overs})"

        # Decide a UI status: live > scheduled > finished.
        if m.get("matchStarted") and not m.get("matchEnded"):
            status = "live"
        elif m.get("matchEnded"):
            status = "finished"
        else:
            status = "scheduled"

        out.append({
            "id": m.get("id", ""),
            "status": status,
            "matchTitle": m.get("name", ""),
            "teamAShort": team_a.get("shortname", ""),
            "teamALogoUrl": team_a.get("img", ""),
            "teamAScore": latest_for(team_a.get("name", "")),
            "teamBShort": team_b.get("shortname", ""),
            "teamBLogoUrl": team_b.get("img", ""),
            "teamBScore": latest_for(team_b.get("name", "")),
            "note": m.get("status", ""),
            "watchUrl": "",
        })

    # Prefer live matches at the top, then scheduled, then finished.
    rank = {"live": 0, "scheduled": 1, "finished": 2}
    out.sort(key=lambda x: rank.get(x["status"], 3))
    return out


def main() -> int:
    api_key = os.environ.get("CRICAPI_KEY", "").strip()
    if not api_key:
        print("CRICAPI_KEY not set — writing empty match list.")
        matches: list[dict] = []
    else:
        matches = normalize(fetch_matches(api_key))

    payload = {
        "version": 1,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "matches": matches,
    }

    out_path = "cricket.json"
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)
        fp.write("\n")

    print(f"Wrote {len(matches)} matches to {out_path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
