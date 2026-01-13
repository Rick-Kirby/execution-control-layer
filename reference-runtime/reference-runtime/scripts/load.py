import argparse
import asyncio
import json
import time
import uuid
from typing import Tuple, List

import httpx

from app.hashing import hash_json

REQ_TEMPLATE = {
    "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
    "tool": {"name": "email.send", "args": {"to": "bob@example.com", "subject": "hi"}},
    "profile": {"id": "example", "version": "1.0.0"},
    "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
    "controls": {},
}


def _percentile(sorted_vals: List[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if pct <= 0:
        return sorted_vals[0]
    if pct >= 100:
        return sorted_vals[-1]
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


async def worker(client: httpx.AsyncClient, url: str, n: int) -> Tuple[int, int, List[float]]:
    ok = 0
    fail = 0
    lats: List[float] = []

    headers = {"content-type": "application/json"}

    for _ in range(n):
        req = dict(REQ_TEMPLATE)
        req["request_id"] = str(uuid.uuid4())

        t0 = time.perf_counter()
        try:
            r = await client.post(url, content=json.dumps(req), headers=headers)
            dt = (time.perf_counter() - t0) * 1000.0  # ms
            lats.append(dt)

            if r.status_code == 200:
                ok += 1
            else:
                fail += 1
        except Exception:
            # Timeout / connection errors count as failures.
            dt = (time.perf_counter() - t0) * 1000.0
            lats.append(dt)
            fail += 1

    return ok, fail, lats


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000/v1/execute")
    ap.add_argument("--requests", type=int, default=1000)
    ap.add_argument("--concurrency", type=int, default=20)
    args = ap.parse_args()

    # Distribute requests as evenly as possible across workers.
    per = args.requests // args.concurrency
    remainder = args.requests % args.concurrency

    # Benchmark-friendly HTTP client configuration
    timeout = httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=60.0)
    limits = httpx.Limits(
        max_connections=max(100, args.concurrency * 2),
        max_keepalive_connections=max(20, args.concurrency),
        keepalive_expiry=30.0,
    )

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        t0 = time.time()
        tasks = []
        for i in range(args.concurrency):
            n = per + (1 if i < remainder else 0)
            tasks.append(asyncio.create_task(worker(client, args.url, n)))

        results = await asyncio.gather(*tasks)
        t1 = time.time()

    total_ok = sum(r[0] for r in results)
    total_fail = sum(r[1] for r in results)
    all_lats: List[float] = []
    for _, _, lats in results:
        all_lats.extend(lats)

    dt = t1 - t0
    rps = total_ok / dt if dt > 0 else 0.0

    all_lats.sort()
    p50 = _percentile(all_lats, 50)
    p95 = _percentile(all_lats, 95)
    p99 = _percentile(all_lats, 99)

    print(
        f"OK: {total_ok}/{args.requests}  FAIL: {total_fail}  "
        f"time: {dt:.3f}s  throughput: {rps:.1f} req/s  "
        f"lat(ms) p50={p50:.1f} p95={p95:.1f} p99={p99:.1f}"
    )


if __name__ == "__main__":
    asyncio.run(main())
