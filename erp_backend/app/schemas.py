from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

# --- Token Schemas ---

class Token(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload schema"""
    username: Optional[str] = None

# --- User Schemas ---

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: Optional[EmailStr] = Field(None, example="user@example.com")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores')
        return v

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, example="securepassword123")
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., example="johndoe")
    password: str = Field(..., example="securepassword123")

class UserInDBBase(UserBase):
    """Base user in database schema"""
    id: int
    is_active: bool = True
    date_joined: datetime

    class Config:
        orm_mode = True

# This should match the User model
class User(UserInDBBase):
    """User response schema"""
    pass

# --- Inventory Schemas ---

class InventoryItemBase(BaseModel):
    """Base inventory item schema"""
    name: str = Field(..., min_length=1, max_length=100, example="Laptop")
    description: Optional[str] = Field(
        None, 
        max_length=500, 
        example="15-inch laptop with 16GB RAM, 512GB SSD"
    )
    quantity: int = Field(..., ge=0, example=10)
    price: float = Field(..., gt=0, example=999.99)

class InventoryItemCreate(InventoryItemBase):
    """Schema for creating a new inventory item"""
    pass

class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, example="Updated Laptop")
    description: Optional[str] = Field(None, max_length=500)
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, gt=0)

class InventoryItem(InventoryItemBase):
    """Inventory item response schema"""
    id: int
    owner_id: int
    date_created: datetime
    date_updated: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- Response Schemas ---

class ResponseBase(BaseModel):
    """Base response schema"""
    success: bool = True
    message: Optional[str] = None

class ItemResponse(ResponseBase):
    """Generic item response schema"""
    data: Optional[dict] = None

class ItemsResponse(ResponseBase):
    """Generic items response schema"""
    data: Optional[List[dict]] = None
    count: int = 0
    skip: int = 0
    limit: int = 100
