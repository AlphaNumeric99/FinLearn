import time

from sqlalchemy.orm import Session

import models
import schemas


def get_friend_requests(db: Session, username: str):
    received_friends = (
        db.query(models.Friends.requesting_user_name)
        .filter(models.Friends.receiving_user_name == username)
        .filter(models.Friends.status == models.Status.RECEIVED)
    )
    return [i[models.Friends.requesting_user_name] for i in received_friends.all()]


def get_friends(db: Session, username: str):

    requested_friends = (
        db.query(models.Friends.receiving_user_name)
        .filter(models.Friends.requesting_user_name == username)
        .filter(models.Friends.status == models.Status.CONFIRMED)
    )
    received_friends = (
        db.query(models.Friends.requesting_user_name)
        .filter(models.Friends.receiving_user_name == username)
        .filter(models.Friends.status == models.Status.CONFIRMED)
    )
    return [i[models.Friends.receiving_user_name] for i in requested_friends.union(received_friends).all()]


def get_friends_suggestions(db: Session, username: str):

    result = set()
    friends = get_friends(db, username)

    for friend in friends:
        for i in get_friends(db, friend):
            if i not in friends and i is not username:
                result.add(i)
                for j in get_friends(db, i):
                    if j not in friends and j is not username:
                        result.add(j)

    return result


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_friend_request(db: Session, requesting_user_name: str, receiving_user_name: str):
    # If request exists from receiving user
    received_request = db.query(models.Friends) \
        .filter(models.Friends.receiving_user_name == requesting_user_name) \
        .filter(models.Friends.requesting_user_name == receiving_user_name) \
        .first()

    if received_request is not None:
        if received_request.status == models.Status.RECEIVED:
            received_request.status = models.Status.CONFIRMED
            db.commit()
            return
        else:
            raise Exception("Friend request already accepted.")

    # If request exists from requesting user
    received_request = db.query(models.Friends) \
        .filter(models.Friends.receiving_user_name == receiving_user_name) \
        .filter(models.Friends.requesting_user_name == requesting_user_name) \
        .first()

    if received_request is not None:
        if received_request.status == models.Status.RECEIVED:
            raise Exception("Duplicate friend request.")
        else:
            raise Exception("Already friends.")

    # Add to db
    friend_request = models.Friends(requesting_user_name=requesting_user_name,
                                    receiving_user_name=receiving_user_name,
                                    created=int(time.time()))

    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)

    return


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, firstname=user.firstname, lastname=user.lastname, username=user.username,
                          created=int(time.time()))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
