# RootRise Funding Readiness System

A dynamic, real-time tracking system for DEVONEERS/RootRise funding opportunities and investor readiness preparation.

![RootRise Colors](https://img.shields.io/badge/Bronze-%23B8904A-B8904A) ![RootRise Colors](https://img.shields.io/badge/Teal-%235DD4C3-5DD4C3) ![RootRise Colors](https://img.shields.io/badge/Navy-%230F1419-0F1419)

## 🎯 Overview

This system helps track:
- **Funding Opportunities** - Accelerators, grants, VC funds, competitions
- **Readiness Items** - Legal, financial, pitch, team, product, market preparation
- **Dashboard Metrics** - Real-time progress tracking and analytics
- **Activity Log** - Complete audit trail of all changes

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone/download the project
cd funding-system

# Start with Docker Compose
docker-compose up -d

# Access at http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
cd backend
uvicorn main:app --reload --port 8000

# Access at http://localhost:8000
```

## 📁 Project Structure

```
funding-system/
├── backend/
│   └── main.py           # FastAPI application with all endpoints
├── frontend/
│   └── index.html        # Single-page dashboard application
├── data/                  # SQLite database (auto-created)
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md
```

## 🔌 API Endpoints

### Opportunities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/opportunities` | List all opportunities (with filters) |
| GET | `/api/opportunities/{id}` | Get single opportunity |
| POST | `/api/opportunities` | Create new opportunity |
| PUT | `/api/opportunities/{id}` | Update opportunity |
| DELETE | `/api/opportunities/{id}` | Delete opportunity |

### Readiness Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/readiness-items` | List all items (with filters) |
| GET | `/api/readiness-items/{id}` | Get single item |
| POST | `/api/readiness-items` | Create new item |
| PUT | `/api/readiness-items/{id}` | Update item |
| DELETE | `/api/readiness-items/{id}` | Delete item |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard-stats` | Get computed metrics |
| GET | `/api/activity-log` | Get recent activity |
| GET | `/api/health` | Health check |

### Query Parameters

**Opportunities:**
- `status`: Filter by status (researching, preparing, submitted, etc.)
- `type`: Filter by type (accelerator, grant, vc_fund, etc.)
- `min_fit_score`: Minimum fit score (0-100)
- `sort_by`: Sort field (deadline, fit_score, priority, created_at)
- `sort_order`: asc or desc

**Readiness Items:**
- `status`: Filter by status (not_started, in_progress, complete, blocked)
- `category`: Filter by category (legal, financial, pitch, etc.)
- `owner`: Filter by owner name
- `sort_by`: Sort field (due_date, priority, status, created_at, category)
- `sort_order`: asc or desc

## 📊 Data Models

### Opportunity
```json
{
  "id": 1,
  "name": "EBRD Star Venture Programme",
  "type": "accelerator",
  "deadline": "2025-03-15T00:00:00",
  "status": "researching",
  "fit_score": 85,
  "url": "https://www.ebrd.com/starventure",
  "notes": "Primary target - Egyptian cohort",
  "funding_amount": "Mentorship + Network",
  "requirements": "Egypt registration, <5 years old",
  "contact_info": null,
  "priority": 1,
  "created_at": "2025-01-23T...",
  "updated_at": "2025-01-23T..."
}
```

### Readiness Item
```json
{
  "id": 1,
  "name": "Pitch Deck (12-15 slides)",
  "category": "pitch",
  "status": "in_progress",
  "owner": "Tee",
  "due_date": "2025-02-20T00:00:00",
  "description": "Visual deck with &I narrative",
  "priority": 1,
  "dependencies": "Financial Projections",
  "completion_percentage": 75,
  "created_at": "2025-01-23T...",
  "updated_at": "2025-01-23T..."
}
```

## 🎨 Design System

The dashboard uses the RootRise brand colors:

| Color | Hex | Usage |
|-------|-----|-------|
| Bronze | `#B8904A` | Primary accent, CTAs, highlights |
| Teal | `#5DD4C3` | Secondary accent, progress, success states |
| Navy | `#0F1419` | Background, dark theme base |
| Cream | `#F5F1E8` | Text, light elements |

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings:
- `API_KEY` - Simple authentication (change for production!)
- `DATABASE_PATH` - SQLite file location
- `SLACK_WEBHOOK_URL` - For deadline notifications
- `SMTP_*` - For email digest functionality

## 🚢 Deployment

### Railway
1. Push to GitHub
2. Connect repo to Railway
3. Set environment variables
4. Deploy automatically

### Render
1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Self-Hosted
```bash
# With Docker
docker-compose up -d

# Or with systemd
# Create /etc/systemd/system/funding-readiness.service
```

## 📈 Roadmap

### Phase 1 ✅ (Current)
- [x] Basic API + SQLite database
- [x] Interactive frontend dashboard
- [x] CRUD for opportunities and readiness items
- [x] Dashboard statistics and metrics
- [x] Activity logging

### Phase 2 (Planned)
- [ ] User authentication (JWT)
- [ ] Email digest notifications
- [ ] Slack/Discord webhook alerts
- [ ] CSV import/export

### Phase 3 (Future)
- [ ] Multi-user support
- [ ] Document attachments
- [ ] Integration with calendar
- [ ] Mobile app (React Native)

## 🤝 Contributing

This is an internal tool for DEVONEERS/RootRise. For suggestions or issues, contact the development team.

## 📜 License

Proprietary - DEVONEERS © 2026


 
---

Built with ❤️ for RootRise's journey to Series A

*"When 'I's rise with &I, they transform"*
