"""
RootRise Funding Readiness System - Backend API
FastAPI application with SQLite database for tracking funding opportunities and readiness items
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import json
import os
from contextlib import contextmanager

# ============================================
# Configuration
# ============================================

DATABASE_PATH = os.environ.get("DATABASE_PATH", "funding_readiness.db")
API_KEY = os.environ.get("API_KEY", "rootrise-dev-key-2024")

# ============================================
# Enums
# ============================================

class OpportunityStatus(str, Enum):
    RESEARCHING = "researching"
    PREPARING = "preparing"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"

class OpportunityType(str, Enum):
    ACCELERATOR = "accelerator"
    GRANT = "grant"
    VC_FUND = "vc_fund"
    ANGEL = "angel"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    COMPETITION = "competition"
    OTHER = "other"

class ReadinessStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"

class ReadinessCategory(str, Enum):
    LEGAL = "legal"
    FINANCIAL = "financial"
    PITCH = "pitch"
    TEAM = "team"
    PRODUCT = "product"
    MARKET = "market"
    OPERATIONS = "operations"
    DOCUMENTATION = "documentation"

# ============================================
# Pydantic Models
# ============================================

class OpportunityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: OpportunityType
    deadline: Optional[datetime] = None
    status: OpportunityStatus = OpportunityStatus.RESEARCHING
    fit_score: int = Field(default=50, ge=0, le=100)
    url: Optional[str] = None
    notes: Optional[str] = None
    funding_amount: Optional[str] = None
    requirements: Optional[str] = None
    contact_info: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[OpportunityType] = None
    deadline: Optional[datetime] = None
    status: Optional[OpportunityStatus] = None
    fit_score: Optional[int] = Field(None, ge=0, le=100)
    url: Optional[str] = None
    notes: Optional[str] = None
    funding_amount: Optional[str] = None
    requirements: Optional[str] = None
    contact_info: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class Opportunity(OpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ReadinessItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: ReadinessCategory
    status: ReadinessStatus = ReadinessStatus.NOT_STARTED
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    dependencies: Optional[str] = None
    completion_percentage: int = Field(default=0, ge=0, le=100)

class ReadinessItemCreate(ReadinessItemBase):
    pass

class ReadinessItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[ReadinessCategory] = None
    status: Optional[ReadinessStatus] = None
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    dependencies: Optional[str] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)

class ReadinessItem(ReadinessItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ActivityLog(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int
    details: Optional[str]
    timestamp: datetime

class DashboardStats(BaseModel):
    total_opportunities: int
    active_opportunities: int
    upcoming_deadlines: int
    total_readiness_items: int
    completed_items: int
    in_progress_items: int
    overall_readiness_score: float
    opportunities_by_status: dict
    opportunities_by_type: dict
    readiness_by_category: dict
    urgent_items: List[dict]
    recent_activity: List[dict]

# ============================================
# Database Setup
# ============================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize database with schema"""
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Opportunities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'researching',
                fit_score INTEGER DEFAULT 50,
                url TEXT,
                notes TEXT,
                funding_amount TEXT,
                requirements TEXT,
                contact_info TEXT,
                priority INTEGER DEFAULT 3,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Readiness items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readiness_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'not_started',
                owner TEXT,
                due_date TEXT,
                description TEXT,
                priority INTEGER DEFAULT 3,
                dependencies TEXT,
                completion_percentage INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Activity log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Check if we need to seed initial data
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        if cursor.fetchone()[0] == 0:
            seed_initial_data(cursor)

def seed_initial_data(cursor):
    """Seed database with initial RootRise funding opportunities and readiness items"""
    now = datetime.utcnow().isoformat()
    
    # Initial opportunities aligned with RootRise Funding Readiness Dashboard
    opportunities = [
        # URGENT - Google for Startups MENA
        ("Google for Startups MENA", "accelerator", "2026-01-30", "preparing", 80, 
         "https://startup.google.com/programs/accelerator/middle-east-north-africa-turkey/", 
         "Up to $350K GCP credits. URGENT: 7 days until deadline!", 
         "Up to $350K GCP credits", "Seed to Series A, product-market fit, AI/ML focus", None, 1),
        # Sanabil 500 MENA
        ("Sanabil 500 MENA (Batch 11)", "accelerator", "2026-03-08", "preparing", 60, 
         "https://500.co/mena", "Seed funding program. $35K program fee required.",
         "$35K program fee", "Early traction, MENA focus", None, 2),
        # EBRD Star Venture - TOP PRIORITY
        ("EBRD Star Venture (Cohort 5)", "accelerator", "2026-04-15", "researching", 100, 
         "https://www.ebrd.com/starventure", "18-month program, no equity. Primary target for RootRise.",
         "No equity, mentorship + network", "Egypt registration, <5 years old, tech focus, B2B", None, 1),
        # Flat6Labs Cairo
        ("Flat6Labs Cairo", "accelerator", None, "researching", 60, 
         "https://flat6labs.com/cairo", "$10-20K for 10-20% equity. Rolling applications.",
         "$10-20K for 10-20% equity", "Egyptian founder, MVP required", None, 3),
        # AUC Venture Lab
        ("AUC Venture Lab", "accelerator", None, "researching", 60, 
         "https://business.aucegypt.edu/research/vlab", "Egypt's first university accelerator. Cohort-based.",
         "Mentorship + workspace", "Innovation focus, Egyptian connection", None, 3),
        # EBRD Innovation Programme
        ("EBRD Innovation Programme", "grant", None, "researching", 80, 
         "https://www.ebrd.com/what-we-do/sectors/advice-small-businesses/star-venture.html", 
         "Up to €30K grants. Component-based applications.",
         "Up to €30K", "EBRD country operations, SME focus", None, 2),
        # Berytech ScaleSmart
        ("Berytech ScaleSmart", "accelerator", None, "researching", 60, 
         "https://berytech.org/", "Investor readiness program. Pre-applications open.",
         "Mentorship + investor access", "MENA startup, growth stage", None, 3),
        # Web Summit Qatar (Event)
        ("Web Summit Qatar", "competition", "2026-01-27", "preparing", 50, 
         "https://qatar.websummit.com/", "Networking opportunity. Jan 26-27, 2026.",
         "Exposure + networking", "Startup pitch competition entry", None, 2),
    ]
    
    for opp in opportunities:
        cursor.execute("""
            INSERT INTO opportunities 
            (name, type, deadline, status, fit_score, url, notes, funding_amount, requirements, contact_info, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*opp, now, now))
    
    # Readiness items aligned with RootRise Funding Readiness Dashboard
    readiness_items = [
        # COMPLETED Items (✓)
        ("Brand Identity", "documentation", "complete", "Tee", None, "Color system v6.5, 4 themes", 1, None, 100),
        ("Architecture Docs", "documentation", "complete", "Tee", None, "Complete technical blueprint", 1, None, 100),
        ("Agent System", "product", "complete", "Tee", None, "11 agents with prompts", 1, None, 100),
        ("Sector Knowledge", "product", "complete", "Tee", None, "27+ sector packs", 1, None, 100),
        ("Team Bios", "team", "complete", "Tee", None, "All founders documented", 2, None, 100),
        
        # IN PROGRESS Items (●)
        ("Pitch Deck (10 slides)", "pitch", "in_progress", "Tee", "2026-02-15", "Simplified version needed. Target: 10 slides max.", 1, None, 60),
        ("Financial Projections", "financial", "in_progress", "Rouba", "2026-02-28", "3-year model required", 1, None, 40),
        
        # NOT STARTED Items (○)
        ("One-Pager", "pitch", "not_started", None, "2026-02-15", "Single A4 summary for quick investor review", 1, "Pitch Deck", 0),
        ("Working Demo (MVD)", "product", "not_started", None, "2026-02-15", "Single flow Minimum Viable Demo", 1, None, 0),
        ("Demo Video (2 min)", "pitch", "not_started", None, "2026-02-28", "Screen recording walkthrough", 2, "Working Demo", 0),
        ("Customer Testimonials", "market", "not_started", None, "2026-03-31", "Target: 3 testimonials by March", 1, None, 0),
        ("Case Studies", "market", "not_started", None, "2026-03-31", "Target: 2 detailed case studies by March", 1, "Customer Testimonials", 0),
        
        # Additional readiness items for comprehensive tracking
        ("Company Registration", "legal", "complete", "Tee", None, "Egyptian commercial registration complete", 2, None, 100),
        ("Market Size Analysis", "market", "complete", "Rouba", None, "TAM/SAM/SOM for Egyptian SME market", 2, None, 100),
        ("Competitive Analysis", "market", "in_progress", "Rouba", "2026-02-20", "Detailed competitor landscape", 2, None, 60),
        ("First 5 Pilots", "operations", "not_started", None, "2026-02-28", "Target: 5 pilot SMEs by end of February", 1, "Working Demo", 0),
        ("First Revenue", "financial", "not_started", None, "2026-03-31", "Target: $500 revenue by March", 1, "First 5 Pilots", 0),
    ]
    
    for item in readiness_items:
        cursor.execute("""
            INSERT INTO readiness_items 
            (name, category, status, owner, due_date, description, priority, dependencies, completion_percentage, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*item, now, now))

def log_activity(cursor, action: str, entity_type: str, entity_id: int, details: str = None):
    """Log an activity to the activity log"""
    cursor.execute("""
        INSERT INTO activity_log (action, entity_type, entity_id, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (action, entity_type, entity_id, details, datetime.utcnow().isoformat()))

# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="RootRise Funding Readiness API",
    description="API for tracking funding opportunities and readiness for DEVONEERS/RootRise",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

# ============================================
# Opportunity Endpoints
# ============================================

@app.get("/api/opportunities", response_model=List[Opportunity])
async def get_opportunities(
    status: Optional[OpportunityStatus] = None,
    type: Optional[OpportunityType] = None,
    min_fit_score: Optional[int] = Query(None, ge=0, le=100),
    sort_by: str = Query("deadline", pattern="^(deadline|fit_score|priority|created_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$")
):
    """Get all funding opportunities with optional filters"""
    with db_session() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM opportunities WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if type:
            query += " AND type = ?"
            params.append(type.value)
        if min_fit_score:
            query += " AND fit_score >= ?"
            params.append(min_fit_score)
        
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

@app.get("/api/opportunities/{opp_id}", response_model=Opportunity)
async def get_opportunity(opp_id: int):
    """Get a specific opportunity by ID"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return dict(row)

@app.post("/api/opportunities", response_model=Opportunity)
async def create_opportunity(opp: OpportunityCreate):
    """Create a new funding opportunity"""
    now = datetime.utcnow().isoformat()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO opportunities 
            (name, type, deadline, status, fit_score, url, notes, funding_amount, requirements, contact_info, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opp.name, opp.type.value, 
            opp.deadline.isoformat() if opp.deadline else None,
            opp.status.value, opp.fit_score, opp.url, opp.notes,
            opp.funding_amount, opp.requirements, opp.contact_info, opp.priority,
            now, now
        ))
        opp_id = cursor.lastrowid
        log_activity(cursor, "created", "opportunity", opp_id, f"Created opportunity: {opp.name}")
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        return dict(cursor.fetchone())

@app.put("/api/opportunities/{opp_id}", response_model=Opportunity)
async def update_opportunity(opp_id: int, opp: OpportunityUpdate):
    """Update an existing opportunity"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        update_fields = []
        params = []
        update_data = opp.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                if field == "deadline" and value:
                    value = value.isoformat()
                elif hasattr(value, 'value'):
                    value = value.value
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if update_fields:
            update_fields.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(opp_id)
            
            cursor.execute(
                f"UPDATE opportunities SET {', '.join(update_fields)} WHERE id = ?",
                params
            )
            log_activity(cursor, "updated", "opportunity", opp_id, 
                        f"Updated fields: {', '.join(update_data.keys())}")
        
        cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        return dict(cursor.fetchone())

@app.delete("/api/opportunities/{opp_id}")
async def delete_opportunity(opp_id: int):
    """Delete an opportunity"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM opportunities WHERE id = ?", (opp_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        cursor.execute("DELETE FROM opportunities WHERE id = ?", (opp_id,))
        log_activity(cursor, "deleted", "opportunity", opp_id, f"Deleted: {row['name']}")
        return {"message": "Opportunity deleted", "id": opp_id}

# ============================================
# Readiness Item Endpoints
# ============================================

@app.get("/api/readiness-items", response_model=List[ReadinessItem])
async def get_readiness_items(
    status: Optional[ReadinessStatus] = None,
    category: Optional[ReadinessCategory] = None,
    owner: Optional[str] = None,
    sort_by: str = Query("priority", pattern="^(due_date|priority|status|created_at|category)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$")
):
    """Get all readiness items with optional filters"""
    with db_session() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM readiness_items WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if category:
            query += " AND category = ?"
            params.append(category.value)
        if owner:
            query += " AND owner = ?"
            params.append(owner)
        
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

@app.get("/api/readiness-items/{item_id}", response_model=ReadinessItem)
async def get_readiness_item(item_id: int):
    """Get a specific readiness item by ID"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM readiness_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Readiness item not found")
        return dict(row)

@app.post("/api/readiness-items", response_model=ReadinessItem)
async def create_readiness_item(item: ReadinessItemCreate):
    """Create a new readiness item"""
    now = datetime.utcnow().isoformat()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO readiness_items 
            (name, category, status, owner, due_date, description, priority, dependencies, completion_percentage, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.name, item.category.value, item.status.value, item.owner,
            item.due_date.isoformat() if item.due_date else None,
            item.description, item.priority, item.dependencies, item.completion_percentage,
            now, now
        ))
        item_id = cursor.lastrowid
        log_activity(cursor, "created", "readiness_item", item_id, f"Created item: {item.name}")
        cursor.execute("SELECT * FROM readiness_items WHERE id = ?", (item_id,))
        return dict(cursor.fetchone())

@app.put("/api/readiness-items/{item_id}", response_model=ReadinessItem)
async def update_readiness_item(item_id: int, item: ReadinessItemUpdate):
    """Update an existing readiness item"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM readiness_items WHERE id = ?", (item_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Readiness item not found")
        
        update_fields = []
        params = []
        update_data = item.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                if field == "due_date" and value:
                    value = value.isoformat()
                elif hasattr(value, 'value'):
                    value = value.value
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        # Auto-update status based on completion percentage
        if "completion_percentage" in update_data:
            pct = update_data["completion_percentage"]
            if pct == 100 and "status" not in update_data:
                update_fields.append("status = ?")
                params.append("complete")
            elif pct > 0 and pct < 100 and existing["status"] == "not_started":
                update_fields.append("status = ?")
                params.append("in_progress")
        
        if update_fields:
            update_fields.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(item_id)
            
            cursor.execute(
                f"UPDATE readiness_items SET {', '.join(update_fields)} WHERE id = ?",
                params
            )
            log_activity(cursor, "updated", "readiness_item", item_id,
                        f"Updated fields: {', '.join(update_data.keys())}")
        
        cursor.execute("SELECT * FROM readiness_items WHERE id = ?", (item_id,))
        return dict(cursor.fetchone())

@app.delete("/api/readiness-items/{item_id}")
async def delete_readiness_item(item_id: int):
    """Delete a readiness item"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM readiness_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Readiness item not found")
        
        cursor.execute("DELETE FROM readiness_items WHERE id = ?", (item_id,))
        log_activity(cursor, "deleted", "readiness_item", item_id, f"Deleted: {row['name']}")
        return {"message": "Readiness item deleted", "id": item_id}

# ============================================
# Dashboard & Stats Endpoints
# ============================================

@app.get("/api/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get computed dashboard statistics"""
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Opportunity stats
        cursor.execute("SELECT COUNT(*) FROM opportunities")
        total_opps = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM opportunities WHERE status NOT IN ('rejected', 'closed')")
        active_opps = cursor.fetchone()[0]
        
        # Upcoming deadlines (next 30 days)
        thirty_days = (datetime.utcnow() + timedelta(days=30)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM opportunities 
            WHERE deadline IS NOT NULL 
            AND deadline <= ? 
            AND deadline >= ?
            AND status NOT IN ('submitted', 'accepted', 'rejected', 'closed')
        """, (thirty_days, datetime.utcnow().isoformat()))
        upcoming_deadlines = cursor.fetchone()[0]
        
        # Readiness stats
        cursor.execute("SELECT COUNT(*) FROM readiness_items")
        total_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM readiness_items WHERE status = 'complete'")
        completed_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM readiness_items WHERE status = 'in_progress'")
        in_progress_items = cursor.fetchone()[0]
        
        # Overall readiness score (weighted by priority)
        cursor.execute("""
            SELECT 
                SUM(completion_percentage * (6 - priority)) as weighted_completion,
                SUM(6 - priority) as total_weight
            FROM readiness_items
        """)
        row = cursor.fetchone()
        overall_score = (row[0] / row[1]) if row[1] and row[0] else 0
        
        # Opportunities by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM opportunities 
            GROUP BY status
        """)
        opps_by_status = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Opportunities by type
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM opportunities 
            GROUP BY type
        """)
        opps_by_type = {row["type"]: row["count"] for row in cursor.fetchall()}
        
        # Readiness by category
        cursor.execute("""
            SELECT category, 
                   AVG(completion_percentage) as avg_completion,
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) as completed
            FROM readiness_items 
            GROUP BY category
        """)
        readiness_by_cat = {
            row["category"]: {
                "avg_completion": round(row["avg_completion"], 1),
                "total": row["total"],
                "completed": row["completed"]
            } for row in cursor.fetchall()
        }
        
        # Urgent items (due within 7 days or overdue, not complete)
        seven_days = (datetime.utcnow() + timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT * FROM readiness_items 
            WHERE due_date IS NOT NULL 
            AND due_date <= ?
            AND status != 'complete'
            ORDER BY due_date ASC
            LIMIT 10
        """, (seven_days,))
        urgent_items = [dict(row) for row in cursor.fetchall()]
        
        # Recent activity
        cursor.execute("""
            SELECT * FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        recent_activity = [dict(row) for row in cursor.fetchall()]
        
        return DashboardStats(
            total_opportunities=total_opps,
            active_opportunities=active_opps,
            upcoming_deadlines=upcoming_deadlines,
            total_readiness_items=total_items,
            completed_items=completed_items,
            in_progress_items=in_progress_items,
            overall_readiness_score=round(overall_score, 1),
            opportunities_by_status=opps_by_status,
            opportunities_by_type=opps_by_type,
            readiness_by_category=readiness_by_cat,
            urgent_items=urgent_items,
            recent_activity=recent_activity
        )

@app.get("/api/activity-log", response_model=List[ActivityLog])
async def get_activity_log(limit: int = Query(20, ge=1, le=100)):
    """Get recent activity log"""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

# ============================================
# Utility Endpoints
# ============================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/reset-database")
async def reset_database():
    """Reset database to initial state (dev only)"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    init_db()
    return {"message": "Database reset to initial state"}

# Serve static files and frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Frontend not found. Please build the frontend.</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
