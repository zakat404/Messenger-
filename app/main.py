from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .routers import auth_router, chat_router, message_router, websocket_router
from .database import engine, AsyncSessionLocal
from .models import Base
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Chat App")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(message_router.router)
app.include_router(websocket_router.router)

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
