import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Win(BaseModel):
    brand: str
    delta_revenue: float
    timestamp: float


class MetricsResponse(BaseModel):
    total_extra_revenue_month: float
    wins: List[Win]
    before_after: List[dict]


class TrialSignup(BaseModel):
    anon_id: str
    minutes_ago: int
    market: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ---------- Marketing-site live metrics (mocked) ----------
BRANDS = [
    "Flipkart", "Swiggy", "Zalora", "Nykaa", "Myntra", "BigBasket", "Ajio",
    "Noon", "Tokopedia", "Lazada", "ShopClues", "Croma"
]
MARKETS = ["US", "IN", "SG", "AE", "ID", "PH", "MY", "TH", "VN", "EU"]


def _random_wins(n: int = 5) -> List[Win]:
    wins: List[Win] = []
    now = time.time()
    for _ in range(n):
        wins.append(Win(
            brand=random.choice(BRANDS),
            delta_revenue=round(random.uniform(1500, 150000), 2),
            timestamp=now - random.randint(5, 3600)
        ))
    # most recent first
    wins.sort(key=lambda w: w.timestamp, reverse=True)
    return wins


@app.get("/api/metrics", response_model=MetricsResponse)
def get_metrics():
    total = round(random.uniform(1_500_000, 4_500_000), 2)
    before_after = [
        {
            "title": "SKU titles normalized",
            "before": "nike run sh 9 blu",
            "after": "Nike Running Shoes | Blue | Size 9"
        },
        {
            "title": "Missing GTIN fixed",
            "before": "GTIN: —",
            "after": "GTIN: 0012345678905"
        },
        {
            "title": "Wrong category",
            "before": "Men > Misc",
            "after": "Men > Shoes > Running"
        }
    ]
    return MetricsResponse(total_extra_revenue_month=total, wins=_random_wins(6), before_after=before_after)


@app.get("/api/trials", response_model=List[TrialSignup])
def get_trials():
    # Generate 8 anonymized signups in the last 60 minutes
    signups: List[TrialSignup] = []
    for _ in range(8):
        minutes = random.randint(1, 60)
        signups.append(TrialSignup(
            anon_id=f"cmo-{random.randint(1000,9999)}",
            minutes_ago=minutes,
            market=random.choice(MARKETS)
        ))
    # sort ascending minutes (most recent first in UI can handle)
    signups.sort(key=lambda s: s.minutes_ago)
    return signups


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
