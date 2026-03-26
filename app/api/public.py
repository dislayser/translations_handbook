from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict
import sys
import os

# Добавляем путь для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.crud import (
    get_all_languages, 
    get_translations_by_language, 
    get_translation,
    get_translations_map,
    get_language
)
from app.schemas import (
    LanguageResponse, 
    TranslationResponse, 
    TranslationsByLanguage,
    LanguageListResponse,
    TranslationListResponse
)

router = APIRouter(prefix="/api/public", tags=["Public API"])

@router.get("/languages", response_model=LanguageListResponse)
async def get_languages():
    """Get all available languages"""
    languages = get_all_languages()
    return LanguageListResponse(
        languages=[LanguageResponse(code=l.code, title=l.title) for l in languages],
        total=len(languages)
    )

@router.get("/translations/{language_code}", response_model=TranslationsByLanguage)
async def get_translations_by_lang(
    language_code: str,
    key: Optional[str] = Query(None, description="Filter by specific translation key")
):
    """Get all translations for a specific language"""
    language = get_language(language_code)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    if key:
        translation = get_translation(key, language_code)
        if not translation:
            raise HTTPException(status_code=404, detail="Translation not found")
        translations_map = {key: translation.value}
    else:
        translations_map = get_translations_map(language_code)
    
    return TranslationsByLanguage(
        language_code=language_code,
        translations=translations_map
    )

@router.get("/translations/{language_code}/{key}", response_model=TranslationResponse)
async def get_specific_translation(language_code: str, key: str):
    """Get a specific translation by key and language"""
    translation = get_translation(key, language_code)
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    return TranslationResponse(
        key=translation.key,
        value=translation.value,
        language_id=translation.language_id
    )

@router.get("/all-translations", response_model=Dict[str, Dict[str, str]])
async def get_all_translations_grouped():
    """Get all translations grouped by language"""
    languages = get_all_languages()
    result = {}
    
    for lang in languages:
        result[lang.code] = get_translations_map(lang.code)
    
    return result