import asyncio
import base64
import hashlib
import hmac
from urllib.parse import parse_qs

from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# from authx import AuthX, AuthXConfig

from fastapi import FastAPI, Request, HTTPException
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

# auth_config = AuthXConfig()
# auth_config.JWT_SECRET_KEY = config.JWT_SECRET_TOKEN
# auth_config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
# auth_config.JWT_TOKEN_LOCATION = ["cookies"]
#
# security = AuthX(config=auth_config)

markup = (
    InlineKeyboardBuilder()
    .button(text="Open Me", web_app=WebAppInfo(url=config.WEBHOOK_URL))
).as_markup()

def verify_telegram_web_app_data(telegram_init_data):
    init_data = parse_qs(telegram_init_data)
    hash_value = init_data.get('hash', [None])[0]
    data_to_check = []

    # Sort key-value pairs alphabetically
    sorted_items = sorted((key, val[0]) for key, val in init_data.items() if key != 'hash')
    data_to_check = [f"{key}={value}" for key, value in sorted_items]

    # HMAC Calculation
    secret = hmac.new(b"WebAppData", config.BOT_TOKEN.encode(), hashlib.sha256).digest()
    _hash = hmac.new(secret, "\n".join(data_to_check).encode(), hashlib.sha256).hexdigest()

    # Verify hash matches
    if _hash == hash_value:
        return init_data.get('user', [None])[0], None
    else:
        return None, "Invalid hash"


def require_authentication(f):
    def wrapper(request: Request, *args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return HTTPException(401, {"error": "Authorization required"})

        # Decode the base64 token
        token = auth_header.split(" ")[1]
        try:
            decoded_token = base64.b64decode(token).decode()
        except Exception as e:
            return HTTPException(401, {"error": "Token decoding failed"})

        # Verify Telegram Web App data
        user, error = verify_telegram_web_app_data(decoded_token)
        if error:
            return HTTPException(401, {"error": error})
        if not user:
            return HTTPException(401, {"error": "User not authenticated"})
        return f(user, *args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper

@app.post("/api/answer", response_class=JSONResponse)
@require_authentication
async def get_answer(data):
    print(data)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello!", reply_markup=markup)


@app.post(config.WEBHOOK_PATH)
async def webhook(req: Request) -> None:
    update = Update.model_validate(await req.json(), context={"bot": bot})
    await dp.feed_update(bot, update)


if __name__ == "__main__":
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
