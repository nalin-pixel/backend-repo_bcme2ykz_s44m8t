import os
import random
from datetime import datetime, timedelta
from typing import List

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
        "collections": [],
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
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
    import os as _os

    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -------- Mock API used by frontend ---------
class BeforeAfter(BaseModel):
    before: str
    after: str


class Win(BaseModel):
    brand: str
    delta_revenue: int


class MetricsResponse(BaseModel):
    total_extra_revenue_month: float
    before_after: List[BeforeAfter]
    wins: List[Win]


@app.get("/api/metrics", response_model=MetricsResponse)
def get_metrics():
    brands = [
        "Flipkart",
        "Swiggy",
        "Zalora",
        "Nykaa",
        "Myntra",
        "Ajio",
        "BigBasket",
        "Reliance",
    ]

    total_extra = random.uniform(1_500_000, 3_200_000)

    sample_pairs = [
        ("nike run sh 9 blu", "Nike Running Shoes | Blue | Size 9"),
        ("GTIN —", "GTIN: 0012345678905"),
        ("Men > Misc", "Men > Shoes > Running"),
        ("SKU_991_no-img", "High-res image stitched"),
        ("20% title duplication", "No duplicates, semantic titles"),
    ]

    before_after = [
        BeforeAfter(before=b, after=a) for (b, a) in random.sample(sample_pairs, k=min(4, len(sample_pairs)))
    ]

    wins = [
        Win(brand=random.choice(brands), delta_revenue=random.randint(20_000, 300_000))
        for _ in range(8)
    ]

    return MetricsResponse(
        total_extra_revenue_month=total_extra,
        before_after=before_after,
        wins=wins,
    )


class TrialSignup(BaseModel):
    anon_id: str
    minutes_ago: int
    market: str


@app.get("/api/trials", response_model=List[TrialSignup])
def get_trials():
    markets = ["IN", "SG", "UAE", "US", "ID", "MY"]

    def make_id():
        return "Q" + "".join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(6))

    now = datetime.utcnow()
    items = []
    for _ in range(12):
        minutes = random.randint(1, 120)
        items.append(
            TrialSignup(
                anon_id=make_id(),
                minutes_ago=minutes,
                market=random.choice(markets),
            )
        )
    return items


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
