from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models import Language, Translation, LanguageCreate, TranslationCreate
from app.crud import (
    create_language, get_language, get_all_languages, 
    update_language, delete_language,
    create_translation, get_translation, get_translations_by_language,
    update_translation, delete_translation, get_all_translations
)
from app.schemas import (
    LanguageResponse, TranslationResponse, MessageResponse,
    LanguageListResponse, TranslationListResponse
)
from app.auth import verify_api_key

router = APIRouter(prefix="/api/admin", tags=["Admin API"], dependencies=[Depends(verify_api_key)])

# Language management endpoints
@router.post("/languages", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_new_language(language: LanguageCreate):
    """Create a new language"""
    existing = get_language(language.code)
    if existing:
        raise HTTPException(status_code=400, detail="Language already exists")
    
    new_lang = Language(code=language.code, title=language.title)
    created = create_language(new_lang)
    return LanguageResponse(code=created.code, title=created.title)

@router.get("/languages", response_model=LanguageListResponse)
async def list_languages():
    """Get all languages (admin version)"""
    languages = get_all_languages()
    return LanguageListResponse(
        languages=[LanguageResponse(code=l.code, title=l.title) for l in languages],
        total=len(languages)
    )

@router.put("/languages/{code}", response_model=LanguageResponse)
async def update_language_by_code(code: str, title: str):
    """Update a language"""
    updated = update_language(code, title)
    if not updated:
        raise HTTPException(status_code=404, detail="Language not found")
    
    return LanguageResponse(code=updated.code, title=updated.title)

@router.delete("/languages/{code}", response_model=MessageResponse)
async def delete_language_by_code(code: str):
    """Delete a language and all its translations"""
    deleted = delete_language(code)
    if not deleted:
        raise HTTPException(status_code=404, detail="Language not found")
    
    return MessageResponse(message=f"Language {code} deleted successfully", success=True)

# Translation management endpoints
@router.post("/translations", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_translation(translation: TranslationCreate):
    """Create a new translation"""
    language = get_language(translation.language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    existing = get_translation(translation.key, translation.language_id)
    if existing:
        raise HTTPException(status_code=400, detail="Translation already exists")
    
    new_trans = Translation(
        key=translation.key,
        value=translation.value,
        language_id=translation.language_id
    )
    created = create_translation(new_trans)
    
    return TranslationResponse(
        key=created.key,
        value=created.value,
        language_id=created.language_id
    )

@router.get("/translations", response_model=TranslationListResponse)
async def list_translations(language_id: str = None):
    """Get all translations, optionally filtered by language"""
    if language_id:
        translations = get_translations_by_language(language_id)
    else:
        translations = get_all_translations()
    
    return TranslationListResponse(
        translations=[TranslationResponse(
            key=t.key, value=t.value, language_id=t.language_id
        ) for t in translations],
        total=len(translations)
    )

@router.put("/translations/{language_id}/{key}", response_model=TranslationResponse)
async def update_translation_by_key(language_id: str, key: str, value: str):
    """Update a translation"""
    updated = update_translation(key, language_id, value)
    if not updated:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return TranslationResponse(
        key=updated.key,
        value=updated.value,
        language_id=updated.language_id
    )

@router.delete("/translations/{language_id}/{key}", response_model=MessageResponse)
async def delete_translation_by_key(language_id: str, key: str):
    """Delete a translation"""
    deleted = delete_translation(key, language_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return MessageResponse(
        message=f"Translation {key} for language {language_id} deleted successfully",
        success=True
    )