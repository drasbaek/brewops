"""Lab A finish line: is "Flat White" supported end to end? Run from the repo root:

    uv run scripts/lab_a_check.py

Green means: the API knows the drink, accepts a flat-white brew, and it
shows up in the stats.
"""

import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

PORT = 8123
BASE = f"http://127.0.0.1:{PORT}"


def get_json(path: str, timeout: float = 3.0):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as resp:
        return json.loads(resp.read())


def post_json(path: str, payload: dict, timeout: float = 5.0):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read())


def api_reachable() -> bool:
    try:
        return "total_brews" in get_json("/api/stats")
    except Exception:
        return False


def start_app_if_needed() -> subprocess.Popen | None:
    if api_reachable():
        return None
    proc = subprocess.Popen(
        [shutil.which("uv") or "uv", "run", "start"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 30
    while time.time() < deadline:
        if api_reachable():
            return proc
        if proc.poll() is not None:
            break
        time.sleep(0.4)
    proc.terminate()
    print("[FAIL] could not start the app — does `uv run start` work? Did you run `uv run seed`?")
    sys.exit(1)


def find_flat_white() -> str | None:
    drinks = get_json("/api/drink-types")
    for d in drinks:
        label = (d.get("label") or "").strip().lower()
        name = (d.get("name") or "").strip().lower()
        if label == "flat white" or name in ("flat_white", "flat-white", "flatwhite"):
            return d["name"]
    return None


def main() -> int:
    if not Path("pyproject.toml").exists():
        print("[FAIL] run this from the repo root (pyproject.toml not found)")
        return 1

    proc = start_app_if_needed()
    try:
        drink = find_flat_white()
        if drink is None:
            print("[FAIL] no 'Flat White' in /api/drink-types.")
            print("       It needs to be a supported drink type — and remember the")
            print("       database is rebuilt from the drink list by `uv run seed`.")
            return 1
        print(f"[OK] drink type present: {drink}")

        timestamp = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        try:
            status, body = post_json(
                "/api/brews",
                {"machine_id": 1, "drink_type": drink, "timestamp": timestamp},
            )
        except urllib.error.HTTPError as e:
            print(f"[FAIL] POST /api/brews with a flat white was rejected ({e.code}):")
            print(f"       {e.read().decode()[:200]}")
            return 1
        print(f"[OK] logged a flat white brew (id {body.get('id')})")

        stats = get_json("/api/stats")
        counts = {d["name"]: d["count"] for d in stats["per_drink"]}
        if counts.get(drink, 0) < 1:
            print("[FAIL] the flat white was accepted but doesn't show up in /api/stats")
            return 1
        print(f"[OK] flat white appears in the stats (count: {counts[drink]})")

        print()
        print("[DONE] Lab A complete! Open http://localhost:8123 and admire your dashboard —")
        print("       your flat white is in there.")
        return 0
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    sys.exit(main())
