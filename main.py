import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def error_response(message: str, code: int = 400):

    return JSONResponse(
        status_code=code,
        content={
            "status": "failure",
            "reason": message
        },
    )


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"status": "working"}


@app.post("/create")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user:
            return error_response(message="Username already registered")
        return crud.create_user(db=db, user=user)
    except Exception as e:
        message = str(e)
        return error_response(message)


@app.post("/add/{requesting_user_name}/{receiving_user_name}")
def add_friend(requesting_user_name: str, receiving_user_name: str, db: Session = Depends(get_db)):
    try:
        db_user_requesting = crud.get_user_by_username(db, username=requesting_user_name)
        db_user_receiving = crud.get_user_by_username(db, username=receiving_user_name)

        if not db_user_requesting:
            return error_response(message=f"Username '{requesting_user_name}' does not exist")

        if not db_user_receiving:
            return error_response(message=f"Username '{receiving_user_name}' does not exist")

        crud.create_friend_request(db=db,
                                   requesting_user_name=requesting_user_name,
                                   receiving_user_name=receiving_user_name)
        return {"status": "success"}
    except Exception as e:
        message = str(e)
        return error_response(message)


@app.get("/friendRequests/{user_name}")
def get_friend_requests(user_name: str, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_username(db, username=user_name)
        if not db_user:
            return error_response(message="User does not exist")

        result = crud.get_friend_requests(db=db, username=user_name)
        if len(result) < 1:
            return error_response(message="No friend requests", code=404)

        return {"friend_requests": result}
    except Exception as e:
        message = str(e)
        return error_response(message)


@app.get("/friends/{user_name}")
def get_friends(user_name: str, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_username(db, username=user_name)
        if not db_user:
            return error_response(message="User does not exist")

        result = crud.get_friends(db=db, username=user_name)
        if len(result) < 1:
            return error_response(message="No friends", code=404)

        return {"friends": result}
    except Exception as e:
        message = str(e)
        return error_response(message)


@app.get("/suggestions/{user_name}")
def get_suggestions(user_name: str, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_username(db, username=user_name)
        if not db_user:
            return error_response(message="User does not exist")

        result = crud.get_friends_suggestions(db=db, username=user_name)
        if len(result) < 1:
            return error_response(message="No suggestions", code=404)

        return {"suggestions": result}
    except Exception as e:
        message = str(e)
        return error_response(message)


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", reload=True)
