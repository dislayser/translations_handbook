from app.redis_client import redis_client, logger
from app.models import Language, Translation
from typing import List, Optional, Dict
from datetime import datetime

def check_redis():
    """Check if Redis is available"""
    if redis_client is None:
        logger.error("Redis client is not initialized")
        raise Exception("Redis client is not available")
    return redis_client

def _prepare_for_storage(obj):
    """Convert object to dict with proper datetime handling"""
    data = obj.dict()
    # Convert datetime to string for JSON serialization
    if 'created_at' in data and isinstance(data['created_at'], datetime):
        data['created_at'] = data['created_at'].isoformat()
    if 'updated_at' in data and isinstance(data['updated_at'], datetime):
        data['updated_at'] = data['updated_at'].isoformat()
    return data

def _restore_from_storage(data):
    """Restore datetime fields from strings"""
    if 'created_at' in data and isinstance(data['created_at'], str):
        data['created_at'] = datetime.fromisoformat(data['created_at'])
    if 'updated_at' in data and isinstance(data['updated_at'], str):
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
    return data

# Language operations
def create_language(language: Language) -> Language:
    """Create a new language"""
    client = check_redis()
    
    key = f"lang:{language.code}"
    data = _prepare_for_storage(language)
    
    client.set_json(key, data)
    logger.info(f"Created language: {language.code}")
    return language

def get_language(code: str) -> Optional[Language]:
    """Get language by code"""
    client = check_redis()
    key = f"lang:{code}"
    data = client.get_json(key)
    if data:
        data = _restore_from_storage(data)
        return Language(**data)
    return None

def get_all_languages() -> List[Language]:
    """Get all languages"""
    client = check_redis()
    keys = client.get_all_keys("lang:*")
    languages = []
    for key in keys:
        data = client.get_json(key)
        if data:
            data = _restore_from_storage(data)
            languages.append(Language(**data))
    return sorted(languages, key=lambda x: x.code)

def update_language(code: str, title: str) -> Optional[Language]:
    """Update language title"""
    language = get_language(code)
    if not language:
        return None
    
    language.title = title
    language.updated_at = datetime.now()
    
    client = check_redis()
    key = f"lang:{code}"
    data = _prepare_for_storage(language)
    
    client.set_json(key, data)
    logger.info(f"Updated language: {code}")
    return language

def delete_language(code: str) -> bool:
    """Delete language and all its translations"""
    client = check_redis()
    key = f"lang:{code}"
    if not client.exists(key):
        return False
    
    # Delete all translations for this language
    translations = get_translations_by_language(code)
    for translation in translations:
        delete_translation(translation.key, code)
    
    client.delete(key)
    logger.info(f"Deleted language: {code}")
    return True

# Translation operations
def create_translation(translation: Translation) -> Translation:
    """Create a new translation"""
    client = check_redis()
    
    key = f"trans:{translation.language_code}:{translation.key}"
    data = _prepare_for_storage(translation)
    
    client.set_json(key, data)
    logger.info(f"Created translation: {translation.key} for {translation.language_code}")
    return translation

def get_translation(key: str, language_code: str) -> Optional[Translation]:
    """Get translation by key and language"""
    client = check_redis()
    redis_key = f"trans:{language_code}:{key}"
    data = client.get_json(redis_key)
    if data:
        data = _restore_from_storage(data)
        return Translation(**data)
    return None

def get_translations_by_language(language_code: str) -> List[Translation]:
    """Get all translations for a language"""
    client = check_redis()
    pattern = f"trans:{language_code}:*"
    keys = client.get_all_keys(pattern)
    translations = []
    for key in keys:
        data = client.get_json(key)
        if data:
            data = _restore_from_storage(data)
            translations.append(Translation(**data))
    return sorted(translations, key=lambda x: x.key)

def get_all_translations() -> List[Translation]:
    """Get all translations"""
    client = check_redis()
    keys = client.get_all_keys("trans:*")
    translations = []
    for key in keys:
        data = client.get_json(key)
        if data:
            data = _restore_from_storage(data)
            translations.append(Translation(**data))
    return translations

def update_translation(key: str, language_code: str, value: str) -> Optional[Translation]:
    """Update translation value"""
    translation = get_translation(key, language_code)
    if not translation:
        return None
    
    translation.value = value
    translation.updated_at = datetime.now()
    
    client = check_redis()
    redis_key = f"trans:{language_code}:{key}"
    data = _prepare_for_storage(translation)
    
    client.set_json(redis_key, data)
    logger.info(f"Updated translation: {key} for {language_code}")
    return translation

def delete_translation(key: str, language_code: str) -> bool:
    """Delete translation"""
    client = check_redis()
    redis_key = f"trans:{language_code}:{key}"
    if not client.exists(redis_key):
        return False
    
    client.delete(redis_key)
    logger.info(f"Deleted translation: {key} for {language_code}")
    return True

def get_translations_map(language_code: str) -> Dict[str, str]:
    """Get translations as key-value map for a language"""
    translations = get_translations_by_language(language_code)
    return {t.key: t.value for t in translations}