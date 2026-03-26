from app.redis_client import redis_client
from app.models import Language, Translation
from typing import List, Optional, Dict
import json

# Language operations
def create_language(language: Language) -> Language:
    key = f"lang:{language.code}"
    redis_client.set_json(key, language.dict())
    return language

def get_language(code: str) -> Optional[Language]:
    key = f"lang:{code}"
    data = redis_client.get_json(key)
    if data:
        return Language(**data)
    return None

def get_all_languages() -> List[Language]:
    keys = redis_client.get_all_keys("lang:*")
    languages = []
    for key in keys:
        data = redis_client.get_json(key)
        if data:
            languages.append(Language(**data))
    return sorted(languages, key=lambda x: x.code)

def update_language(code: str, title: str) -> Optional[Language]:
    language = get_language(code)
    if not language:
        return None
    
    language.title = title
    key = f"lang:{code}"
    redis_client.set_json(key, language.dict())
    return language

def delete_language(code: str) -> bool:
    key = f"lang:{code}"
    if not redis_client.exists(key):
        return False
    
    # Delete all translations for this language
    translations = get_translations_by_language(code)
    for translation in translations:
        delete_translation(translation.key, code)
    
    redis_client.delete(key)
    return True

# Translation operations
def create_translation(translation: Translation) -> Translation:
    key = f"trans:{translation.language_id}:{translation.key}"
    redis_client.set_json(key, translation.dict())
    return translation

def get_translation(key: str, language_id: str) -> Optional[Translation]:
    redis_key = f"trans:{language_id}:{key}"
    data = redis_client.get_json(redis_key)
    if data:
        return Translation(**data)
    return None

def get_translations_by_language(language_id: str) -> List[Translation]:
    pattern = f"trans:{language_id}:*"
    keys = redis_client.get_all_keys(pattern)
    translations = []
    for key in keys:
        data = redis_client.get_json(key)
        if data:
            translations.append(Translation(**data))
    return sorted(translations, key=lambda x: x.key)

def get_all_translations() -> List[Translation]:
    keys = redis_client.get_all_keys("trans:*")
    translations = []
    for key in keys:
        data = redis_client.get_json(key)
        if data:
            translations.append(Translation(**data))
    return translations

def update_translation(key: str, language_id: str, value: str) -> Optional[Translation]:
    translation = get_translation(key, language_id)
    if not translation:
        return None
    
    translation.value = value
    redis_key = f"trans:{language_id}:{key}"
    redis_client.set_json(redis_key, translation.dict())
    return translation

def delete_translation(key: str, language_id: str) -> bool:
    redis_key = f"trans:{language_id}:{key}"
    if not redis_client.exists(redis_key):
        return False
    
    redis_client.delete(redis_key)
    return True

def get_translations_map(language_id: str) -> Dict[str, str]:
    """Get translations as key-value map for a language"""
    translations = get_translations_by_language(language_id)
    return {t.key: t.value for t in translations}