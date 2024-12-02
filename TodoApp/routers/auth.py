from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Assignee, Todos
# Model and our Assignee Model is going to be the user information that we created for our table. 
# Just like previously when we were using 2 new models to be able to query databases, we're going to do the same thing with our table. 
# So, if we look into our todos.py, we can see that we say from models import Todos, we're going to say the same thing, but Assignee within our auth.py. 
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, get_db
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'c53a7303bf976b69fa44588e20eeecae428756135b8e8a26068ffcfa2c96092d'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateAssigneeRequest(BaseModel):
    id: int
    role: str
    department: str
    username: str
    name: str
    surname: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_assignee(username: str, password: str, db):
    assignee = db.query(Assignee).filter(Assignee.username == username).first()
    if not assignee:
        return False
    if not bcrypt_context.verify(password, assignee.hashed_password):
        return False
    return assignee


def create_access_token(username: str, assignee_id: int, expires_delta: timedelta):
     
     encode = {'sub': username, 'id': assignee_id}
     expires = datetime.now(timezone.utc) + expires_delta
     encode.update({'exp': expires})
     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_assignee(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        assignee_id: int = payload.get('id')
        if username is None or assignee_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': assignee_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_assignee(db: db_dependency,
                    create_assignee_request: CreateAssigneeRequest):
       create_assignee_model = Assignee(
            id=create_assignee_request.id,
            role=create_assignee_request.role,
            department=create_assignee_request.department,
            username=create_assignee_request.username,
            name=create_assignee_request.name,
            surname=create_assignee_request.surname,
            email=create_assignee_request.email,
            hashed_password=bcrypt_context.hash(create_assignee_request.password),
    )
       
       db.add(create_assignee_model)
       db.commit()



@router.post("/token", response_model=Token)
def token_access(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    assignee = authenticate_assignee(form_data.username, form_data.password, db)
    if not assignee:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate user.')
    token = create_access_token(assignee.username, assignee.id, timedelta(minutes=120))

    return {'access_token': token, 'token_type': 'bearer'}


