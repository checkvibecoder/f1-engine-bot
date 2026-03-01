# F1 Engine Bot 🏎️

Automated Formula 1 weekend update bot powered by:

- OpenF1 (live race telemetry)
- Jolpica (official classification data)
- GitHub Actions (automation)
- X API (tweet publishing)

---

## 🚀 What It Does

- Posts Practice classification (Top 7)
- Posts Qualifying results (Q1, Q2, Q3)
- Posts Sprint results (Top 8)
- Posts Live Race updates (Top 5 per lap change)
- Posts Final Race results (Top 10)

---

## ⚙️ How It Works

- Runs automatically every 10 minutes via GitHub Actions
- Stores state in `state.json`
- Prevents duplicate tweets
- Uses secure GitHub Secrets for API credentials

---

## 🔐 Security

All API keys are stored in GitHub Secrets.
No credentials are stored in the repository.

---

## 🏁 Status

Fully automated. No manual intervention required.
