from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.user_login_details import UserLogin
from dependencies.auth import get_authenticated_user
from schemas.create_new_user_schema import CreateNewUser
from service.create_admin import new_admin_creation
from database.connections import get_db

create_admin_router = APIRouter()
#new admin created by admin user
@create_admin_router.post("/admin/register")
def create_admin(user: CreateNewUser, db: Session = Depends(get_db), current_user: UserLogin = Depends(get_authenticated_user)):
    return new_admin_creation(user,db,current_user)
