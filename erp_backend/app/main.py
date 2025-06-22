import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth
from .database import SessionLocal, engine, init_db

# Initialize the database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="ERP System API",
    description="A modern ERP system with FastAPI and SQLAlchemy",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Authentication Endpoints ---

@app.post("/api/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user account
    """
    return crud.create_user(db=db, user=user)

# --- User Endpoints ---

@app.get("/api/users/me", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Get current user details
    """
    return current_user

# --- Inventory Endpoints ---

@app.post("/api/items/", response_model=schemas.InventoryItem, status_code=status.HTTP_201_CREATED, tags=["Inventory"])
async def create_item(
    item: schemas.InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new inventory item
    """
    return crud.create_user_item(db=db, item=item, owner_id=current_user.id)

@app.get("/api/items/", response_model=List[schemas.InventoryItem], tags=["Inventory"])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve inventory items with pagination
    """
    items = crud.get_items(db, skip=skip, limit=limit, owner_id=current_user.id)
    return items

@app.get("/api/items/{item_id}", response_model=schemas.InventoryItem, tags=["Inventory"])
async def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific inventory item by ID
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_item

@app.put("/api/items/{item_id}", response_model=schemas.InventoryItem, tags=["Inventory"])
async def update_item(
    item_id: int,
    item: schemas.InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update an inventory item
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return crud.update_item(db=db, db_item=db_item, item_update=item.dict(exclude_unset=True))

@app.delete("/api/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Inventory"])
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete an inventory item
    """
    db_item = crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud.delete_item(db=db, item_id=item_id)
    return {"ok": True}

# --- Health Check Endpoint ---

@app.get("/api/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """
    Health check endpoint for container orchestration
    """
    try:
        # Basic health check without database connection
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": "sqlite"
        }
    except Exception as e:
        # Log the error but still return 200 to prevent container restarts
        print(f"Health check warning: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# --- Error Handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
