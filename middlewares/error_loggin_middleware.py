from aiogram import BaseMiddleware, types
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
import traceback
from utils.misc import noww

from aiogram import BaseMiddleware, types, Bot
from aiogram.exceptions import TelegramBadRequest
import traceback

class ErrorLoggingMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, error_channel_id: int):
        super().__init__()
        self.bot = bot
        self.error_channel_id = error_channel_id

    async def send_error_message(self, error_text):
        try:
            await self.bot.send_message(
                chat_id=self.error_channel_id,
                text=error_text
            )
        except Exception as e:
            if 'message is too long' in str(e):
                # Recursively split the message
                half = len(error_text) // 2
                await self.send_error_message(error_text[:half])  # Send first half
                await self.send_error_message(error_text[half:])  # Send second half

    async def __call__(self, handler, event, data):
        try:
            # Call the next handler in the middleware chain
            return await handler(event, data)
        except Exception as e:
            # Capture and format the exception details
            error_text = (
                f"#ANONIM\n#RUNTIME_ERROR at {noww()}\n🚨 Error Occurred\n\n"
                f"Type: `{type(e).__name__}`\n"
                f"Message: `{str(e)}`\n\n"
                f"Traceback:\n```{traceback.format_exc()}```"
            )
            # Send the error message to the designated channel
            await self.send_error_message(error_text)
            
            # Re-raise the exception if further handling is needed
            raise e
