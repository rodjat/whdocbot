import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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

markup = (
    InlineKeyboardBuilder()
    .button(text="Open Me", web_app=WebAppInfo(url=config.WEBHOOK_URL))
).as_markup()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello!", reply_markup=markup)


@app.post("/api/answer", response_class=JSONResponse)
async def get_answer(request: Request):
    data = await request.json()
    print(data)


@app.post(config.WEBHOOK_PATH)
async def webhook(req: Request) -> None:
    update = Update.model_validate(await req.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


if __name__ == "__main__":
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
