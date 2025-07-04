from .user import router as user_router
from .team import router as team_router
from .news import router as news_router

routers = [user_router, team_router, news_router]
