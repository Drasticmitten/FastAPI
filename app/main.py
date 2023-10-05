import time
from random import randrange
from typing import Optional
from . import models
from .database import engine, get_db
import psycopg2
from sqlalchemy.orm import Session
from fastapi import FastAPI, status, Response, HTTPException, Depends  # Response for the code exit
from fastapi.params import Body
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
"""
MONGO_HOST = 'localhost'
MONGO_PUERTO = '27017'
MONGO_TIEMPO = 1000

MONGO_URI = 'mongodb://'+MONGO_HOST+":"+MONGO_PUERTO+"/"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIEMPO)
    client.server_info()
    print("Database  connection was successfully\n")
    mydb = client['Database']
    mycoll = mydb['collection']
    mydict = {"name": "John", "address": "Highway 37"}
    mycoll.insert_one(mydict)
    print(mydb.list_collections())
    client.close()

except Exception as identifier:
    print(identifier)
"""


def find_post(idt: int):
    for p in my_posts:
        if p['Id'] == idt:
            return p


def find_index(idt):  # find the post index to delete
    for i, p in enumerate(my_posts):
        if p['Id'] == idt:
            return i


class Post(BaseModel):
    title: str
    content: str
    user: str
    published: bool = True  # value by defect true
    rating: Optional[int] = None  # the attribute is optional allowing that user don't send this
    # if he doesn't want, and validates if the value is an integer


@app.get('/')
def root():
    return {'Message:': 'Hello world !!'}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"Data": posts}


@app.get('/posts')
def get_posts():
    cursor.execute("""SELECT * FROM public.post""")
    posts = cursor.fetchall()
    print(posts)
    return {'Data ': posts}


# status_code=status.HTTP_201_CREATED for indicate the status code
@app.post('/posts', status_code=status.HTTP_201_CREATED)  # USER is a reserved word
def create_posts(post: Post):
    cursor.execute("""INSERT INTO public.post ("Title", "Content", "User", "Published", "Rating") VALUES (%s, %s, %s, 
    %s, %s) RETURNING *""",
                   (post.title, post.content, post.user, post.published, post.rating))
    # it passes the values in a second param, we use this method cause avoid that the user than make
    # SQL query in our database
    new_post = cursor.fetchone()
    conn.commit()
    return {"Data inserted": new_post}


@app.post('/post')
def create_post(my_data: dict = Body(...)):
    print(my_data)
    return {'New post': f"title: {my_data['Title']} Content: {my_data['Content']} User: {my_data['User']}"}


# title str, content str, user str


@app.post('/Post', status_code=status.HTTP_201_CREATED)
# status_code=status.HTTP_201_CREATED for indicate the status code
def create_post(new_post: Post):
    print(new_post)
    print(new_post.model_dump())  # Become the data in a python dictionary

    post_dict = new_post.model_dump()  # create a dictionary
    post_dict['Id'] = randrange(0, 1000000)  # assign a unique id between 0 and 1000000 due to the probability that a
    # 2 numbers are the same is really low
    my_posts.append(post_dict)  # add the new post into the posts
    print(my_posts[-1])
    return {"Data": post_dict}  # we should return the post_dict that includes the id variable


@app.get('/Post/last_post')
def get_last_post():  # It's important the order because it can be confused with '/Post/{idt}'
    return {"My post": my_posts[-1]}


@app.get('/posts/{idt}')  # take care !! with the _id because it's a string
def get_post(idt: int):  # response: Response - make sure that the idt is an integer and become it
    cursor.execute("""SELECT * FROM public.post WHERE id = %s """, (str(idt),))
    post = cursor.fetchone()
    if not post:
        """ response.status_code = status.HTTP_404_NOT_FOUND  # Code que means: Data not found
        # we can use status for indicate the status exit
        return {'message': f'Post with id: {idt}  was not found'}"""
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {idt} was not found')  # It throws an exception message with raise
    return {"post_detail": post}


@app.delete('/posts/{idt}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(idt: int):
    cursor.execute("""DELETE FROM public.post WHERE id = %s returning *""", (str(idt),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {idt} doesn't exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put('/posts/{idt}')
def update_post(idt: int, post: Post):  # post store the data that is typed by the users
    cursor.execute("""UPDATE public.post SET "Title" = %s, "Content" = %s, "User" = %s, "Published" = %s, "Rating" = %s 
    WHERE id = %s RETURNING *""", (post.title, post.content, post.user, post.published, post.rating, str(idt)))
    updated_data = cursor.fetchone()
    conn.commit()
    print(updated_data)
    if updated_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {idt} doesn't exist")
    return {'Updated Data': updated_data}
