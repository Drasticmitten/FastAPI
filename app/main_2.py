import time
from typing import Optional
from . import models
from .database import engine, get_db
import psycopg2
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, Response, HTTPException, Depends  # Response for the code exit
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)

# py -3 -m venv "name" -> create the environment
# venv/Scripts/activate.bat -> active the virtual envi
# unicorn main:app -reload -> execute and every time that I update the file it'll refresh automatically
app = FastAPI()

my_posts = [{"Id": 1, "Title": "Title of post 1", "Content": "Content of post 1", "User": "User of post 1",
             "Published": True, "Rating": 50}, {"Id": 2, "Title": "Title of post 2", "Content": "Content of post 2",
                                                "User": "User of post 2", "Published": True, "Rating": 70}]

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='147258369', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database  connection was successfully\n")
        break
    except Exception as error:
        print('Connection to database failed')
        print('Error: ', error)
        time.sleep(2)


class Post(BaseModel):
    title: str
    content: str
    user: str
    published: bool = True  # value by defect true
    rating: Optional[int] = None  # the attribute is optional allowing that user don't send this
    # if he doesn't want, and validates if the value is an intege


app = FastAPI()


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"Data": posts}


@app.get("/posts")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"Data": posts}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(title=post.title, content=post.content, published=post.published,user=post.user, rating=post.rating)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}
