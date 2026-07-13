from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.librarian import Librarian
from app.schemas.auth import LibrarianCreate, LibrarianOut, Token
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=LibrarianOut, status_code=201)
def register(data: LibrarianCreate, db: Session = Depends(get_db)):
    if db.query(Librarian).filter(Librarian.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    librarian = Librarian(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(librarian)
    db.commit()
    db.refresh(librarian)
    return librarian


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    librarian = db.query(Librarian).filter(Librarian.email == form.username).first()
    if not librarian or not verify_password(form.password, librarian.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not librarian.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token({"sub": str(librarian.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=LibrarianOut)
def me(db: Session = Depends(get_db), token: str = ""):
    # Thin wrapper — real auth via get_current_librarian dependency
    from app.core.security import get_current_librarian
    return get_current_librarian(token, db)
