# Product Finder

Multi-marketplace product search platform with analytics dashboard, SQLite persistence, user accounts, and influencer AI automation.

## Features

- **Multi-marketplace search** — Amazon, eBay, TikTok Shop, AliExpress, Alibaba, China market, plus local catalog
- **Analytics dashboard** — KPI cards, charts, provider activity, and top product leaderboard (inspired by modern BI dashboards)
- **SQLite persistence** — cached products, search history, user accounts, influencer integrations, AI workflows
- **User accounts** — register/login with JWT authentication
- **Influencer Hub** — connect social/affiliate accounts and configure AI-powered automation workflows

## Quick start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open:
- **Dashboard:** http://127.0.0.1:8000
- **Influencer Hub:** http://127.0.0.1:8000/influencer
- **API docs:** http://127.0.0.1:8000/docs

### Demo account

- Username: `demo`
- Password: `demo1234`

## Marketplace API keys

Copy `.env.example` to `.env` and add credentials to switch providers from demo mode to live mode:

```env
AMAZON_ACCESS_KEY=...
AMAZON_SECRET_KEY=...
AMAZON_PARTNER_TAG=...
EBAY_APP_ID=...
TIKTOK_SHOP_APP_KEY=...
ALIEXPRESS_APP_KEY=...
ALIBABA_APP_KEY=...
CHINA_MARKET_API_KEY=...
```

Without keys, marketplace providers return realistic demo listings so the app works out of the box.

## API overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/register` | Create account |
| `POST /api/auth/login` | Login (OAuth2 form) |
| `GET /api/auth/me` | Current user |
| `GET /api/dashboard` | Analytics dashboard data |
| `GET /api/search?q=...` | Unified marketplace search |
| `GET /api/influencer/dashboard` | Influencer profile, integrations, workflows |
| `POST /api/influencer/profile` | Save influencer profile |
| `POST /api/influencer/integrations` | Connect platform account |
| `POST /api/influencer/workflows` | Create AI workflow |

## Architecture

```
backend/app/
├── main.py              # FastAPI app
├── database.py          # SQLite + SQLAlchemy
├── db_models.py         # ORM models
├── auth.py              # JWT auth
├── providers/           # Marketplace adapters
├── services/            # Search, dashboard, influencer logic
├── routers/             # API routes
└── static/              # Dashboard + Influencer Hub UI
```

Database file: `backend/product_finder.db` (auto-created on startup).
