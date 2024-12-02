from fastapi import FastAPI, Depends, HTTPException, Path
import models # parent toot can not find models so we have to change "import models"
from database import engine, Base
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from routers import auth, todos
from models import Assignee, Todos


app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(todos.router)

