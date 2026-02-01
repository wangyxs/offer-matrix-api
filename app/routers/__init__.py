from fastapi import APIRouter
from app.routers import auth, users, roles, interviews, interview, question_sets

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(interviews.router)
api_router.include_router(interview.router)
api_router.include_router(question_sets.router)
