from fastapi import APIRouter, Depends, HTTPException, Path
from database import SessionLocal, engine, Base, get_db
from models import Todos, Assignee
from typing import Optional, Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status
from .auth import get_current_assignee
from datetime import timedelta, datetime, timezone, date
from fastapi.encoders import jsonable_encoder


router = APIRouter()


db_dependency = Annotated[Session, Depends(get_db)]
assignee_dependency = Annotated[dict, Depends(get_current_assignee)]



class TodoRequest(BaseModel):
    id: int = Field(gt=0, lt=21)
    category: str = Field(min_length=2)
    description: str = Field(min_length=2)
    priority: int = Field(gt=0, lt=4)
    notes: str = Field(min_length=2, max_length=100)
    due_date: date = Field(default_factory=lambda: (datetime.now() + timedelta(days=1)).date())



@router.get("/", status_code=status.HTTP_200_OK)
def read_all(assignee: assignee_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == assignee.get('id')).all()



@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(assignee: assignee_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if assignee is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == assignee.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')



@router.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(assignee: assignee_dependency, db: db_dependency,
                      todo_request: TodoRequest):
    if assignee is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Todos(**todo_request.model_dump(), owner_id=assignee.get('id'))

    db.add(todo_model)
    db.commit()



@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(assignee: assignee_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if assignee is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == assignee.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.id = todo_request.id
    todo_model.category = todo_request.category
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.notes = todo_request.notes
    todo_model.due_date = todo_request.due_date

    db.add(todo_model)
    db.commit()



@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(assignee: assignee_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if assignee is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == assignee.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == assignee.get('id')).delete()

    db.commit()


