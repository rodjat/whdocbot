from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from authx import AuthX, AuthXConfig

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse

from models import UserModelSchema

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from config import config


bot = Bot(
        config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML")
    )
dp = Dispatcher()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

auth_config = AuthXConfig()
auth_config.JWT_SECRET_KEY = config.JWT_SECRET_TOKEN.get_secret_value()
auth_config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
auth_config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=auth_config)

markup = (
    InlineKeyboardBuilder()
    .button(text="Open Me", web_app=WebAppInfo(url=config.WEBAPP_URL))
).as_markup()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello!", reply_markup=markup)


@app.post("/api/login")
async def login(creds: UserModelSchema, response: Response):
    if creds.username == "test" and creds.role == "user":
        token = security.create_access_token(uid="12345")
        response.set_cookie(auth_config.JWT_ACCESS_COOKIE_NAME, token)
        print("token get")
        return {"access_token": token}
    raise HTTPException(401, "Incorrect")


@app.post("/api/answer")
async def get_answer(request: Request):
    ...


@app.post(config.WEBHOOK_PATH)
async def webhook(req: Request) -> None:
    update = Update.model_validate(await req.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


if __name__ == "__main__":
    print('started')
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
