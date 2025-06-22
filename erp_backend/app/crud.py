from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from passlib.context import CryptContext
from fastapi import HTTPException, status

from . import models, schemas

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get a user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a user by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash"""
    return pwd_context.hash(password)

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    # Check if username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise ValueError("Username already registered")
        
    if user.email:
        db_email = get_user_by_email(db, email=user.email)
        if db_email:
            raise ValueError("Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        date_joined=datetime.utcnow(),
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, 
    db_user: models.User, 
    user_update: Dict[str, Any]
) -> models.User:
    """Update user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.date_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(
    db: Session, 
    username: str, 
    password: str
) -> Optional[models.User]:
    """Authenticate a user with username/email and password"""
    # Try to find user by username or email
    user = get_user_by_username(db, username=username)
    if not user and "@" in username:
        user = get_user_by_email(db, email=username)
    
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

# --- Inventory Item CRUD Operations ---

def get_item(db: Session, item_id: int) -> Optional[models.InventoryItem]:
    """Get an inventory item by ID"""
    return db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()

def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    owner_id: Optional[int] = None,
    name: Optional[str] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[models.InventoryItem]:
    """Get a list of inventory items with optional filters"""
    """Get a list of inventory items with optional filtering"""
    query = db.query(models.InventoryItem)
    
    if owner_id is not None:
        query = query.filter(models.InventoryItem.owner_id == owner_id)
    
    return query.offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int) -> Optional[models.InventoryItem]:
    """Get a single inventory item by ID"""
    return db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()

def create_user_item(
    db: Session, 
    item: schemas.InventoryItemCreate, 
    owner_id: int
) -> models.InventoryItem:
    """Create a new inventory item for a specific user"""
    db_item = models.InventoryItem(
        **item.dict(),
        owner_id=owner_id,
        date_created=datetime.utcnow()
    )
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating item: {str(e)}"
        )

def update_item(
    db: Session, 
    db_item: models.InventoryItem, 
    item_update: Dict[str, Any]
) -> models.InventoryItem:
    """Update an existing inventory item"""
    for field, value in item_update.items():
        setattr(db_item, field, value)
    
    db_item.date_updated = datetime.utcnow()
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating item: {str(e)}"
        )

def delete_item(db: Session, item_id: int) -> bool:
    """Delete an inventory item"""
    db_item = get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    try:
        db.delete(db_item)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting item: {str(e)}"
        )
