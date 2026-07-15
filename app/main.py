from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
import app.models  # ensure all models are registered
from app.routers.auth import router as auth_router
from app.routers.author_category import router as author_category_router
from app.routers.books import router as books_router
from app.routers.students import router as students_router
from app.routers.transactions import router as transactions_router
from app.routers.reports import router as reports_router

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System",
    description="RESTful API for managing books, students, issuance, returns and fines.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(author_category_router)
app.include_router(books_router)
app.include_router(students_router)
app.include_router(transactions_router)
app.include_router(reports_router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Library Management System API"}
