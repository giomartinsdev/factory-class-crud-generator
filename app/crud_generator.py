from typing import Type, Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel as PydanticBaseModel, create_model
from app.database import get_db
from models.base import BaseModel


def create_pydantic_model(sqlalchemy_model: Type[BaseModel], exclude_fields: List[str] = None) -> Type[PydanticBaseModel]:
    """
    Create a Pydantic model from SQLAlchemy model for request/response validation
    """
    if exclude_fields is None:
        exclude_fields = []
    
    fields = {}
    
    for column in sqlalchemy_model.__table__.columns:
        if column.name in exclude_fields:
            continue
            
        try:
            python_type = column.type.python_type
        except NotImplementedError:
            python_type = str
            
        default_value = ...
        
        if column.nullable and column.name not in ['id']:
            python_type = Optional[python_type]
            default_value = None
        elif column.default is not None:
            try:
                default_value = column.default.arg if hasattr(column.default, 'arg') else None
            except Exception:
                default_value = None
        elif column.name == 'id':
            continue
            
        fields[column.name] = (python_type, default_value)
    
    return create_model(f"{sqlalchemy_model.__name__}Model", **fields)


def create_crud_operations(model_class: Type[BaseModel]):
    """
    Create CRUD operations for a given model class
    """
    
    def create_item(db: Session, item_data: dict) -> BaseModel:
        """Create a new item"""
        try:
            db_item = model_class(**item_data)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Integrity error: {str(e.orig)}"
            )
    
    def get_item(db: Session, item_id: int) -> Optional[BaseModel]:
        """Get an item by ID (only active items)"""
        return db.query(model_class).filter(
            model_class.id == item_id,
            model_class.is_active
        ).first()
    
    def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[BaseModel]:
        """Get multiple items with pagination (only active items)"""
        return db.query(model_class).filter(
            model_class.is_active
        ).offset(skip).limit(limit).all()
    
    def update_item(db: Session, item_id: int, item_data: dict) -> Optional[BaseModel]:
        """Update an existing item (only active items)"""
        try:
            db_item = db.query(model_class).filter(
                model_class.id == item_id,
                model_class.is_active
            ).first()
            if not db_item:
                return None
            
            for key, value in item_data.items():
                if hasattr(db_item, key) and key != 'id':
                    setattr(db_item, key, value)
            
            db.commit()
            db.refresh(db_item)
            return db_item
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Integrity error: {str(e.orig)}"
            )
    
    def delete_item(db: Session, item_id: int) -> bool:
        """Soft delete an item by setting is_active to False"""
        db_item = db.query(model_class).filter(
            model_class.id == item_id,
            model_class.is_active
        ).first()
        if not db_item:
            return False
        
        db_item.soft_delete()
        db.commit()
        return True
    
    return {
        'create': create_item,
        'get': get_item,
        'get_all': get_items,
        'update': update_item,
        'delete': delete_item
    }


def generate_crud_routes(app: FastAPI, models: Dict[str, Type[BaseModel]]):
    """
    Generate CRUD routes for all discovered models
    """
    
    for model_name, model_class in models.items():
        create_model_schema = create_pydantic_model(model_class, exclude_fields=['id', 'created_at', 'updated_at', 'is_active'])
        update_model_schema = create_pydantic_model(model_class, exclude_fields=['id', 'created_at', 'updated_at', 'is_active'])
        create_pydantic_model(model_class)
        
        crud_ops = create_crud_operations(model_class)
        
        route_prefix = f"/{model_name.lower()}"
        
        def make_create_endpoint(model_cls, crud_operations, schema):
            async def create_endpoint(
                item: schema,
                db: Session = Depends(get_db)
            ):
                """Create a new item"""
                item_data = item.model_dump(exclude_unset=True)
                db_item = crud_operations['create'](db, item_data)
                return db_item.to_dict()
            return create_endpoint
        
        def make_get_endpoint(model_cls, crud_operations):
            async def get_endpoint(
                item_id: int,
                db: Session = Depends(get_db)
            ):
                """Get an item by ID"""
                db_item = crud_operations['get'](db, item_id)
                if not db_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{model_cls.__name__} not found"
                    )
                return db_item.to_dict()
            return get_endpoint
        
        def make_get_all_endpoint(model_cls, crud_operations):
            async def get_all_endpoint(
                skip: int = 0,
                limit: int = 100,
                db: Session = Depends(get_db)
            ):
                """Get all items with pagination"""
                db_items = crud_operations['get_all'](db, skip=skip, limit=limit)
                return [item.to_dict() for item in db_items]
            return get_all_endpoint
        
        def make_update_endpoint(model_cls, crud_operations, schema):
            async def update_endpoint(
                item_id: int,
                item: schema,
                db: Session = Depends(get_db)
            ):
                """Update an existing item"""
                item_data = item.model_dump(exclude_unset=True)
                db_item = crud_operations['update'](db, item_id, item_data)
                if not db_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{model_cls.__name__} not found"
                    )
                return db_item.to_dict()
            return update_endpoint
        
        def make_delete_endpoint(model_cls, crud_operations):
            async def delete_endpoint(
                item_id: int,
                db: Session = Depends(get_db)
            ):
                """Delete an item"""
                success = crud_operations['delete'](db, item_id)
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"{model_cls.__name__} not found"
                    )
                return {"message": f"{model_cls.__name__} deleted successfully"}
            return delete_endpoint
        
        app.post(f"{route_prefix}/", response_model=dict, tags=[model_name])(
            make_create_endpoint(model_class, crud_ops, create_model_schema)
        )
        
        app.get(f"{route_prefix}/{{item_id}}", response_model=dict, tags=[model_name])(
            make_get_endpoint(model_class, crud_ops)
        )
        
        app.get(f"{route_prefix}/", response_model=List[dict], tags=[model_name])(
            make_get_all_endpoint(model_class, crud_ops)
        )
        
        app.put(f"{route_prefix}/{{item_id}}", response_model=dict, tags=[model_name])(
            make_update_endpoint(model_class, crud_ops, update_model_schema)
        )
        
        app.delete(f"{route_prefix}/{{item_id}}", tags=[model_name])(
            make_delete_endpoint(model_class, crud_ops)
        )
        
        print(f"Generated CRUD routes for {model_name}: {route_prefix}")

