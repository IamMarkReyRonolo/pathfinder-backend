import sys, os, pdb, json, imp, re, math
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from urllib import response
from db import connection
from fastapi import APIRouter, Depends, status, Response, Body, Query, Path, HTTPException, status, Depends, Request
from lib.jwt_bearer import JWTBearer
from lib import jwt_handler
from models.staff_models import user_request_schemas
from controllers import user_controller

routes = APIRouter(
    prefix='/users',
    tags=['User APIs']
)


@routes.post("/login",  status_code=status.HTTP_200_OK)
async def login(credentials: user_request_schemas.LogIn):
    login_user = user_controller.login(connection.engine, credentials)
    if(login_user):
        name = login_user.full_name
        token = jwt_handler.signJWT(str(login_user.uuid), name)
        return token
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Username or Password is wrong.")


@routes.post("/register", status_code=status.HTTP_201_CREATED)
async def register(account: user_request_schemas.Registration):
    registered_user = user_controller.register_user(
        connection.engine, account)
    return {"detail": "Successfully Added User", "user": registered_user}


@routes.get("/user_data/", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def get_user_data(request: Request):
    uuid = request.state.user_details['uuid']
    user_data = user_controller.get_user_data(
        connection.engine, uuid)
    return {"user": user_data}


@routes.get("/find/{username}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def find_user(username: str):  # type: ignore
    user = user_controller.get_specific_user(
        connection.engine, username)

    return user


@routes.get("/admin/all", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def get_all_users(role: str = None, page_num: int = 1, page_size: int = 10):  # type: ignore
    user = user_controller.get_all_users(
        connection.engine, role, page_num, page_size)

    response = {
        "data": user[1],
        "count": len(user[1]),
        "total": user[0][0],
        "page": page_num,
        "no_of_pages": math.ceil(user[0][0]/page_size),
    }

    return response

@routes.get("/connections", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_200_OK)
async def get_user_connections(request: Request):  # type: ignore
    uuid = request.state.user_details['uuid']
    connections = user_controller.get_all_connections(
        connection.engine, uuid)
    response = {
        "connections" : connections
    }
    return response


@routes.patch("/connection_request/{request_uuid}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def request_connection(request_uuid: str, request: Request):
    user_uuid = request.state.user_details['uuid']
    user_controller.request_for_connection(
        connection.engine, user_uuid, request_uuid)
    notification_message = request.state.user_details['name'] + " wants to connect with you"
    notification = user_request_schemas.Notification(notification_title="Accept Connection", notification_message=notification_message, friend_ids=[request_uuid])
    created_notification = user_controller.send_notification(
        connection.engine, notification)
    return {"detail": "Request Sent"}


@routes.patch("/accept_connection/{request_uuid}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def accept_connection(request_uuid: str, request: Request):
    user_uuid = request.state.user_details['uuid']
    user_controller.accept_request(
        connection.engine, user_uuid, request_uuid)
    notification_message = request.state.user_details['name'] + " accepted your connection request"
    notification = user_request_schemas.Notification(notification_title="Accept Connection", notification_message=notification_message, friend_ids=[request_uuid])
    created_notification = user_controller.send_notification(
        connection.engine, notification)
    return {"detail": "Request Accepted"}

@routes.patch("/remove_connection/{request_uuid}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def accept_connection(request_uuid: str, request: Request):
    user_uuid = request.state.user_details['uuid']
    user_controller.remove_connection(
        connection.engine, user_uuid, request_uuid)
    return {"detail": "Successfully removed connection"}

# @routes.post("/activate_find_me", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
# async def activate_find_me(notification: user_request_schemas.Notification):
#     created_notification = user_controller.send_notification(
#         connection.engine, notification)
#     return {"detail": "Successfully Sent Notification", "notification": created_notification}

@routes.post("/respond_to_findme", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def activate_find_me(notification: user_request_schemas.Notification):
    created_notification = user_controller.send_notification(
        connection.engine, notification)
    return {"detail": "Successfully Sent Notification", "notification": created_notification}

@routes.get("/notifications", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def get_notifications(request: Request):
    user_uuid = request.state.user_details['uuid']
    notifications = user_controller.get_user_notifications(
        connection.engine, user_uuid)
    return {"notifications": notifications}

@routes.get("/check_for_active_find_me", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def check_for_active_find_me(request: Request):
    user_uuid = request.state.user_details['uuid']
    room = user_controller.check_for_active_room(
        connection.engine, user_uuid)
    return {"room": room}


@routes.post("/activate_find_me", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def activate_find_me(room_session: user_request_schemas.RoomSession, request: Request):
    user_uuid = request.state.user_details['uuid']
    user_full_name = request.state.user_details['name']
    notification = user_controller.create_session_room(
        connection.engine, room_session, user_uuid, user_full_name)
    return {"detail": "Successfully Created Room", "notification" : notification}

@routes.patch("/respond_to_findme/{room_code}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def respond_find_me(room_code: str, request: Request):
    user_full_name = request.state.user_details['name']
    user_uuid = request.state.user_details['uuid']
    
    room = user_controller.add_users_to_room(
        connection.engine, room_code, user_uuid, user_full_name)
    return {"detail": "Successfully Updated Room", "room" : room}

@routes.delete("/terminate_find_me/{room_code}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_201_CREATED)
async def activate_find_me(room_code: str, request: Request):
    user_uuid = request.state.user_details['uuid'] 
    user_full_name = request.state.user_details['name']
    notification = user_controller.delete_room(
        connection.engine, room_code, user_uuid, user_full_name)
    return {"detail": "Successfully Deleted Room", "notification" : notification}


# @routes.get("/get_people_count/", dependencies=[Depends(JWTBearer(access_level='admin'))], status_code=status.HTTP_200_OK)
# async def get_user_data(request: Request):
#     result = staff_controller.get_count(
#         connection.engine)
#     return {"data": result}





# @routes.get("/specific/{uuid}", dependencies=[Depends(JWTBearer(access_level='admin'))], status_code=status.HTTP_200_OK)
# async def get_specific_staff(uuid: str):
#     user_data = staff_controller.get_user_data(
#         connection.engine, uuid)
#     return {"user": user_data}


# @routes.put("/update_user_details/{uuid}", dependencies=[Depends(JWTBearer(access_level='admin'))], status_code=status.HTTP_200_OK)
# async def update_details(uuid: str, update: staff_request_schemas.UpdateAccountDetails, request: Request):
#     updated_by = request.state.user_details['name']
#     update.updated_by = updated_by
#     result = staff_controller.update_details(
#         connection.engine, uuid, update)
#     return {"Successfully updated": result}


# @routes.put("/change_user_password/{uuid}",  dependencies=[Depends(JWTBearer(access_level='admin'))])
# async def change_password(uuid: str, update: staff_request_schemas.ChangePassword, request: Request):
#     updated_by = request.state.user_details['name']
#     update.updated_by = updated_by
#     result = staff_controller.change_password(
#         connection.engine, uuid, update)
#     if(result):
#         return {"message": "Successfully change password"}
#     else:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                             detail="Unsuccessful update.")



# @routes.delete("/delete/{uuid}", dependencies=[Depends(JWTBearer(access_level='admin'))], status_code=status.HTTP_200_OK)
# async def change_password(uuid: str):
#     result = staff_controller.delete_account(
#         connection.engine, uuid)
#     if(result):
#         return {"message": "Successfully deleted"}
#     else:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                             detail="Unsuccessful delete.")
