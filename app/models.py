from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Language(BaseModel):
    code: str = Field(..., min_length=2, max_length=10)
    title: str = Field(..., min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Translation(BaseModel):
    key: str = Field(..., min_length=1, max_length=200)
    value: str
    language_id: str  # language code
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TranslationCreate(BaseModel):
    key: str
    value: str
    language_id: str

class LanguageCreate(BaseModel):
    code: str
    title: str