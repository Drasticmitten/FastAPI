import time
from .schemas import Post
from . import models
from .database import engine, get_db
import psycopg2
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, Response, HTTPException, Depends  # Response for the code exit
from psycopg2.extras import RealDictCursor


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
    """new_post = models.Post(title=post.title, content=post.content, published=post.published,user=post.user,
                           rating=post.rating)"""
    new_post = models.Post(**post.model_dump())  # this is a way more efficient to pass the params
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get('/posts/{idt}')
def get_post(idt: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == idt).first()
    if not post:
        raise HTTPException(status_code=status.HTPP_404_NOT_FOUND,
                            detail=f'post   with id: {idt} was not found')
    return {'post_detail': post}


@app.delete('/posts/{idt}')
def delete_post(idt: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == idt)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {idt} does not exist')
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{idt}')
def update_post(idt: int, updated_post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == idt)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {idt} does not exist')
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return {'data': post_query.first()}
