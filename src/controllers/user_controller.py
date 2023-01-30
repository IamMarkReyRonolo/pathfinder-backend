import sys, os, psycopg2, sqlalchemy
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from fastapi import status, HTTPException
from models.staff_models import user_table_schema, user_request_schemas
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from lib.bcrypter import Hasher
from sqlalchemy.orm import load_only
from sqlmodel.sql.expression import Select, SelectOfScalar
from sqlalchemy.sql import text
from sqlmodel import col
from sqlalchemy import and_

Select.inherit_cache = True 
SelectOfScalar.inherit_cache = True 

def register_user(engine, user):
    with Session(engine) as session:
        try:
            created_user = user_table_schema.User(
                full_name=user.full_name,
                username=user.username,
                password=Hasher().hash_password(user.password),)

            session.add(created_user)
            session.commit()
            session.refresh(created_user)
            return created_user
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='email already exists')


def login(engine, credentials):
    with Session(engine) as session:

        try:
            with Session(engine) as session:
                query = select(user_table_schema.User).where(
                    user_table_schema.User.username == credentials.username)
                results = session.exec(query)
                account = results.one()
                verified = Hasher().verify_password(
                    login_password=credentials.password, member_password=account.password)

                if verified:
                    return account
                else:
                    return None
        except Exception as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                                detail="Username or Password is wrong.")


def get_all_connections(engine, user_uuid):
    try:
        with Session(engine) as session:
            query = select(user_table_schema.User).where(
                user_table_schema.User.uuid == user_uuid)
            results = session.exec(query)
            user = results.one()
            connections = user.connections
            return connections
    except Exception as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def get_specific_user(engine, username):
    try:
        with Session(engine) as session:
            # get count
            query = select(user_table_schema.User).where(
            user_table_schema.User.username == username
            ).options(load_only("uuid", "full_name"))
            result = session.exec(query)
            user = result.one()

            return user
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def get_user_data(engine, uuid: str):
    try:
        with Session(engine) as session:
            query = select(user_table_schema.User).where(
                user_table_schema.User.uuid == uuid).options(load_only("uuid", "full_name", "username"))
            results = session.exec(query)
            user = results.one()
            return user
    except NoResultFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")
    except sqlalchemy.exc.DataError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='invalid id')

def get_all_users(engine, role, page_num, page_size):
    try:
        with Session(engine) as session:
            # get count
            if role == 'all' or role == None:
                query1 = select(func.count()).select_from(
                    user_table_schema.User)
                query2 = select(user_table_schema.User)

            total_count = session.exec(query1).all()
            statement = query2.offset(
                (page_num - 1)*page_size).limit(page_size)
            results = session.exec(statement)
            all_users = results.all()

            return (total_count, all_users)
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def request_for_connection(engine, user_uuid, request_uuid):
    try:
        with Session(engine) as session:
            # get count
            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == user_uuid
            )
            result = session.exec(query)
            user1 = result.one()

            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == request_uuid
            )
            result = session.exec(query)
            user2 = result.one()

            user1.connections.append(user_table_schema.Friend(full_name = user2.full_name, status = 'Pending', friend_id= request_uuid))
            session.add(user1)


            user2.connections.append(user_table_schema.Friend(full_name = user1.full_name, status = 'Request', friend_id= user_uuid))
            session.add(user2)
            session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def accept_request(engine, user_uuid, request_uuid):
    try:
        with Session(engine) as session:
            # get count
            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == user_uuid
            )
            result = session.exec(query)
            user1 = result.one()

            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == request_uuid
            )
            result = session.exec(query)
            user2 = result.one()

            user1_connections = user1.connections
            user2_connections = user2.connections


            for i,connection in enumerate(user1_connections):
                    if(str(connection.friend_id) == request_uuid):
                        connection.status = "Accepted"
                        session.add(connection)


            for i,connection in enumerate(user2_connections):
                    if(str(connection.friend_id) == user_uuid):
                        connection.status = "Accepted"
                        session.add(connection)
                        
            session.add(user1)
            session.add(user2)
            session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def remove_connection(engine, user_uuid, request_uuid):
    try:
        with Session(engine) as session:
            # get count
            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == user_uuid
            )
            result = session.exec(query)
            user1 = result.one()

            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == request_uuid
            )
            result = session.exec(query)
            user2 = result.one()

            user1_connections = user1.connections
            user2_connections = user2.connections


            for i,connection in enumerate(user1_connections):
                    if(str(connection.friend_id) == request_uuid):
                        session.delete(connection)


            for i,connection in enumerate(user2_connections):
                    if(str(connection.friend_id) == user_uuid):
                        session.delete(connection)
                        
            session.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")


def send_notification(engine, notification):
    try:
        with Session(engine) as session:
            # get count
            created_notification = user_table_schema.Notification(
                notification_title= notification.notification_title,
                notification_message = notification.notification_message,
                users_involved = notification.friend_ids,
                code=notification.code )

            session.add(created_notification)
            session.commit()
            session.refresh(created_notification)
            return created_notification

    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def get_user_notifications(engine, user_uuid):
    try:
        with Session(engine) as session:
            query = select(user_table_schema.Notification).where(and_(user_table_schema.Notification.users_involved.any(user_uuid)))
            result = session.exec(query.order_by(user_table_schema.Notification.created_at.desc()))
            notifications = result.all()
            return notifications
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User Not Found.")

def create_session_room(engine, session_room, user_id, user_full_name):
    with Session(engine) as session:
        try:
            query = select(user_table_schema.User).where(
            user_table_schema.User.uuid == user_id
            )
            result = session.exec(query)
            user1 = result.one()

            user1.session_rooms.append(user_table_schema.RoomSession(
                room_code=session_room.room_code,
                users_responded=session_room.users_responded,
                users_requested=session_room.users_requested,
                ))
            session.add(user1)
            session.commit()
            message = user_full_name + " activated Find Me. Respond Now!"
            created_notification = user_request_schemas.Notification(notification_title="Find Me", notification_message=message,code=session_room.room_code,friend_ids=session_room.users_requested)
            notification = send_notification(engine, created_notification)

            return notification
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='Error Occured')

def add_users_to_room(engine, room_code, user_id, user_full_name):
    with Session(engine) as session:
        try:
            query = select(user_table_schema.RoomSession).where(
           user_table_schema.RoomSession.room_code == room_code
            )
            result = session.exec(query)
            room = result.one()
            if (user_id in room.users_responded or user_id == str(room.user_id)):
                return room
            else:
                users = []
                for user in room.users_responded:
                    users.append(str(user))
                users.append(str(user_id))
                room.users_responded = users
                session.add(room)   
                session.commit()
                session.refresh(room)

                message = user_full_name + " responded to your Find Me"
                created_notification = user_request_schemas.Notification(notification_title="Find Me", notification_message=message,code=room_code,friend_ids=[str(room.user_id)])
                send_notification(engine, created_notification)
                return room
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='Room Not Found or Terminated')

def delete_room(engine, room_code,  user_id, user_full_name):
    with Session(engine) as session:
        try:
            query = select(user_table_schema.RoomSession).where(
           user_table_schema.RoomSession.room_code == room_code
            )
            result = session.exec(query)
            room = result.one()
            friend_ids = room.users_requested
            session.delete(room)
            session.commit()

            message = user_full_name + " Find Me has ended."
            created_notification = user_request_schemas.Notification(notification_title="Find Me", notification_message=message,code=room_code,friend_ids=friend_ids)
            notification = send_notification(engine, created_notification)

            return notification
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='Error Occured')

def get_specific_session_room(engine, room_code):
    with Session(engine) as session:
        try:
            query = select(user_table_schema.RoomSession).where(
           user_table_schema.RoomSession.room_code == room_code
            )
            result = session.exec(query)
            room = result.one()
            return room
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail="Room Not Found")

def check_for_active_room(engine, uuid):
    with Session(engine) as session:
        try:
            query = select(user_table_schema.RoomSession).where(
           user_table_schema.RoomSession.user_id == uuid
            )
            result = session.exec(query)
            room = result.one()
            return room
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail="Room Not Found")



# def get_count(engine):
#     try:
#         with Session(engine) as session:
#             # get count

#             query1 = select(func.count()).select_from(
#                 user_table_schema.Staff)

#             staff_total_count = session.exec(query1.where(
#                 user_table_schema.Staff.role == 'staff')).all()
#             admin_total_count = session.exec(query1.where(
#                 user_table_schema.Staff.role == 'admin')).all()

#             payload = {'staff_total_count': staff_total_count[0], 'admin_total_count':
#                        admin_total_count[0], 'total': admin_total_count[0] + staff_total_count[0]}

#             return payload
#     except:
#         raise HTTPException(status.HTTP_404_NOT_FOUND,
#                             detail="Staff Not Found.")





# def update_details(engine, uuid: str, update):
#     with Session(engine) as session:
#         try:
#             query = select(user_table_schema.Staff).where(
#                 user_table_schema.Staff.uuid == uuid
#             )
#             results = session.exec(query)
#             staff = results.one()

#             staff.first_name = update.first_name
#             staff.middle_name = update.middle_name
#             staff.last_name = update.last_name
#             staff.role = update.role
#             staff.email = update.email
#             staff.updated_by = update.updated_by
#             staff.updated_at = update.updated_at

#             session.commit()

#             return True
#         except NoResultFound:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail="Staff Not Found.")
#         except sqlalchemy.exc.IntegrityError:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                                 detail='email already exists')
#         except sqlalchemy.exc.DataError:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                                 detail='invalid id')


# def change_password(engine, uuid: str, update):
#     with Session(engine) as session:
#         try:
#             query = select(user_table_schema.Staff).where(
#                 user_table_schema.Staff.uuid == uuid
#             )
#             results = session.exec(query)
#             staff = results.one()

#             verified = Hasher().verify_password(
#                 login_password=update.current_password, member_password=staff.password)

#             if(verified):
#                 staff.password = Hasher().hash_password(update.new_password)
#                 staff.updated_by = update.updated_by
#                 staff.updated_at = update.updated_at
#                 session.commit()
#                 return True

#             return None
#         except NoResultFound:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail="Staff Not Found.")
#         except sqlalchemy.exc.IntegrityError:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                                 detail='email already exists')
#         except sqlalchemy.exc.DataError:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                                 detail='invalid id')


# def delete_account(engine, uuid: str):
#     with Session(engine) as session:
#         try:
#             query = select(user_table_schema.Staff).where(
#                 user_table_schema.Staff.uuid == uuid)
#             results = session.exec(query)
#             staff = results.one()
#             session.delete(staff)
#             session.commit()
#             return True
#         except NoResultFound:
#             raise HTTPException(status.HTTP_404_NOT_FOUND,
#                                 detail="Staff Not Found.")
#         except sqlalchemy.exc.DataError:
#             raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                                 detail='invalid id')
