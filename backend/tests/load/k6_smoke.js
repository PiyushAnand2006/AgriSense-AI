/**
 * k6 load test for the AgriSense AI backend — **LOCAL / STAGING USE ONLY**.
 *
 * ⚠️  NEVER point this at the live deployment (agrisense-api.onrender.com or
 * similar): load-testing a live app can crash it for real users and burn the
 * free plan. Run it against a local server (or a disposable staging copy)
 * with its own throwaway database.
 *
 * Usage (Windows / Git Bash):
 *   winget install k6 --source winget              # one-time install
 *   cd backend
 *   ./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
 *   k6 run tests/load/k6_smoke.js
 *
 * Environment overrides:
 *   BASE_URL      default http://localhost:8000   (target server)
 *   DEMO_EMAIL    default demo@agrisense.ai       (seeded demo account)
 *   DEMO_PASSWORD default Demo@1234
 *   RAMP          per-stage ramp duration, default 30s
 *   HOLD          hold-at-peak duration, default 30s
 *
 * Flows covered (3-5 things real users do most):
 *   1. Browse the crop catalog          GET /api/v1/crops?season=RABI
 *   2. Open a crop's disease guide      GET /api/v1/crops/wheat/diseases
 *   3. Check today's mandi price board  GET /api/v1/market/prices
 *   4. Open the dashboard               GET /api/v1/dashboard/summary (auth)
 *
 * Login happens once in setup() and the token is shared — this is a load
 * test, not an auth test. If you raise the VU counts, also raise
 * RATE_LIMIT_* env vars on the server or auth/upload/assistant calls
 * will trip the per-IP limiter.
 */

import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const DEMO_EMAIL = __ENV.DEMO_EMAIL || "demo@agrisense.ai";
const DEMO_PASSWORD = __ENV.DEMO_PASSWORD || "Demo@1234";

export const options = {
  // Ramp 0 -> 20 -> 50 -> 100 virtual users, hold at peak, ramp down.
  stages: [
    { duration: __ENV.RAMP || "30s", target: 20 },
    { duration: __ENV.RAMP || "30s", target: 50 },
    { duration: __ENV.RAMP || "30s", target: 100 },
    { duration: __ENV.HOLD || "30s", target: 100 },
    { duration: "15s", target: 0 },
  ],
  thresholds: {
    // Clear pass/fail gates (see the "scale" runbook).
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
  // The dashboard call needs the setup() token, so no per-request auth jitter.
  insecureSkipTLSVerify: true,
  noConnectionReuse: false,
};

export function setup() {
  const login = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({ email: DEMO_EMAIL, password: DEMO_PASSWORD }),
    { headers: { "Content-Type": "application/json" } },
  );
  check(login, {
    "setup: demo login works": (r) => r.status === 200,
  });
  const body = login.json();
  if (!body || !body.token) {
    throw new Error(
      `Demo login failed (${login.status}). Start the backend first: uvicorn app.main:app --port 8000`,
    );
  }
  return { token: body.token };
}

export default function (data) {
  const authHeaders = {
    headers: { Authorization: `Bearer ${data.token}` },
  };

  // 1. Crop catalog (public reference data).
  const catalog = http.get(`${BASE_URL}/api/v1/crops?season=RABI`);
  check(catalog, {
    "catalog 200": (r) => r.status === 200,
  });

  // 2. Disease guide for one crop.
  const diseases = http.get(`${BASE_URL}/api/v1/crops/wheat/diseases`);
  check(diseases, {
    "diseases 200": (r) => r.status === 200,
  });

  // 3. Market price board (exercises the daily latest-per-combo cache).
  const prices = http.get(`${BASE_URL}/api/v1/market/prices?limit=20`);
  check(prices, {
    "prices 200": (r) => r.status === 200,
  });

  // 4. Dashboard (auth-specific data).
  const dashboard = http.get(`${BASE_URL}/api/v1/dashboard/summary`, authHeaders);
  check(dashboard, {
    "dashboard 200": (r) => r.status === 200,
  });

  // Realistic think time between screen loads (deterministic per-iteration
  // variation; k6 has no crypto needs here).
  sleep(1 + (__ITER % 3) * 0.5);
}
