from pydantic import BaseModel
from typing import Dict, List, Optional

class LanguageResponse(BaseModel):
    code: str
    title: str

class TranslationResponse(BaseModel):
    key: str
    value: str
    language_id: str

class TranslationsByLanguage(BaseModel):
    language_code: str
    translations: Dict[str, str]

class MessageResponse(BaseModel):
    message: str
    success: bool

class LanguageListResponse(BaseModel):
    languages: List[LanguageResponse]
    total: int

class TranslationListResponse(BaseModel):
    translations: List[TranslationResponse]
    total: int