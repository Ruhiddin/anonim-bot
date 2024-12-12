import re
from functools import wraps
from aiogram.types import Message
from aiogram.fsm.context import FSMContext






def valid_link_name(func):
    @wraps(func)
    async def wrapper(msg: Message, state: FSMContext, *args, **kwargs):
        # Regex pattern for valid link name (only letters, digits, and underscores)
        if not re.match(r'^[A-Za-z0-9_]+$', msg.text):
            # Send an error message if the link name is invalid
            await msg.reply("Iltimos, faqat ingliz harflari, raqamlar va pastki chiziqni ishlating.")
            return
        # Call the original function if the validation passes
        return await func(msg, state, *args, **kwargs)
    return wrapper
