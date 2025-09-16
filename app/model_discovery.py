import os
import importlib
import inspect
from typing import Type, Dict
from app.config import settings
from models.base import BaseModel


def discover_and_register_models() -> Dict[str, Type[BaseModel]]:
    """
    Discover all model classes in the models directory
    and return a dictionary mapping model names to classes
    """
    models = {}
    models_dir = settings.models_dir
    
    models_path = os.path.join(os.getcwd(), models_dir)
    
    if not os.path.exists(models_path):
        print(f"Models directory '{models_path}' not found")
        return models
    
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            
            try:
                module = importlib.import_module(f"{models_dir}.{module_name}")
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseModel) and 
                        obj is not BaseModel and 
                        hasattr(obj, '__tablename__')):
                        
                        models[name] = obj
                        print(f"Discovered model: {name}")
                        
            except ImportError as e:
                print(f"Error importing module {module_name}: {e}")
                continue
    
    return models


def get_model_fields(model_class: Type[BaseModel]) -> Dict[str, str]:
    """
    Get field information for a model class
    Returns a dictionary mapping field names to their types
    """
    fields = {}
    
    for column in model_class.__table__.columns:
        field_name = column.name
        field_type = str(column.type)
        fields[field_name] = field_type
    
    return fields


def get_model_relationships(model_class: Type[BaseModel]) -> Dict[str, str]:
    """
    Get relationship information for a model class
    Returns a dictionary mapping relationship names to related models
    """
    relationships = {}
    
    if hasattr(model_class, '__mapper__'):
        for rel in model_class.__mapper__.relationships:
            relationships[rel.key] = rel.mapper.class_.__name__
    
    return relationships

