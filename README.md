# Browser Security Labs

Small, self-contained labs demonstrating common browser security flaws. Each lab
runs a deliberately vulnerable victim and a separate attacker server via Docker,
so the attacks are genuinely cross-origin. **Run only in an isolated environment.**

| Lab | Vulnerability | Victim | Attacker |
|-----|---------------|--------|----------|
| [`cors-vuln-lab`](./cors-vuln-lab) | CORS misconfiguration — a reflected `Origin` with credentials lets any site read a logged-in user's data | `:5000` | `:8000` |
| [`csp-lab`](./csp-lab) | CSP bypass — a whitelisted domain serving AngularJS allows HTML injection to run despite a nonce policy | `:8181` | `:9090` |

Each lab has its own `README.md` (overview) and `LAB_GUIDE.md` (step-by-step
walkthrough). To start one:

```bash
cd <lab> && docker-compose up --build
```
