from pprint import pprint
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from middlewares.error_loggin_middleware import ErrorLoggingMiddleware
from middlewares.rate_limit_middleware import RateLimitMiddleware
import logging
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from pathlib import Path
from dotenv import load_dotenv
import os
import string, random

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)
# BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_TOKEN='7267176194:AAHhOme3QyXxr-Xuk5cSBydSNUI5VLCiUoM'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

blocklist = {}  # Format: {recipient_id: set(sender_ids)}
user_map = {} # Format: {token: user_id}
callback_map = {} # Format: {token: user_id}

def generate_unique_id(length=8):
    """
    Generate a unique ID consisting of numbers and case-sensitive English letters.
    
    Args:
        length (int): The length of the unique ID. Default is 8.
    
    Returns:
        str: A randomly generated unique ID.
    """
    characters = string.ascii_letters + string.digits  # All case-sensitive letters and digits
    unique_id = ''.join(random.choices(characters, k=length))
    return unique_id

def get_or_create_token(id, the_map):
    for var, val in the_map.items():
        if val == id:
            return var
    while True:
        token = generate_unique_id()
        if token not in the_map:
            the_map[token] = id
            return token



class User(StatesGroup):
    msg = State()

@dp.message(CommandStart())
async def start_handler(message: Message, command: CommandStart, state: FSMContext):
    if command.args:
        recipient_token = command.args
        recipient_id = user_map.get(recipient_token, None)
        if recipient_id is None:
            return await message.answer("Bu link ortiq ishlamaydi. Foydalanuvchi uni yangilagan.")
        
        try:
            int(recipient_id)

            # Check if the recipient has blocked the sender
            if int(recipient_id) in blocklist and message.chat.id in blocklist[int(recipient_id)]:
                await message.answer("Siz bu foydalanuvchiga xabar yubora olmaysiz.\nU sizni bloklagan!")
                return

            markup = InlineKeyboardBuilder()
            markup.button(text="Bekor qilish", callback_data="cancel")
            markup = markup.as_markup()
            prev_msg = await message.answer(
                "Anonim xabaringizni yuboring matn, rasm, yoki video. "
                "Fikringizdan qaytsangiz, 'Bekor qilish' tugmasini bosing.",
                reply_markup=markup,
            )
            await state.update_data(prev_msg=prev_msg.message_id, recipient_id=recipient_id)
            await state.set_state(User.msg)
        except ValueError:
            await message.answer("Xato link. Iltimos linki tekshirib, qaytadan urinib ko'ring\n\nEslatma: foydalanuvchi o'z linkini yangilagan bo'lsa, eski linklar bekor qilinadi.")
    else:
        user_id = str(message.chat.id)
        bot_username = (await bot.get_me()).username
        welcome_msg = await message.answer(
            (
            "📩 *Anonim Xabar Botiga Xush Kelibsiz\\!*"
            "\n\n🔒 *Xavfsizlik kafolatlangan*: Sizning barcha xabarlaringiz maxfiy saqlanadi\\. Bot hech qanday ma'lumotlarni saqlamaydi yoki uchinchi shaxslarga uzatmaydi\\."
            "\n\n\n🎁 Nimalarni yuborishingiz mumkin?"
            "\n\n✉️ *Matn* — Oddiy yoki hissiyotli yozuvlar\\."
            "\n🖼 *Rasm* — Har qanday suratlarni ulashing\\."
            "\n📹 *Video* — Oddiy yoki doira shaklidagi videolar\\."
            "\n🎙 *Ovoz* — Audio va Ovozli xabarlar yuborish\\."
            "\n📂 *Hujjat* — Fayllarni biriktirib ulashing\\."
            "\n🐾 *Animatsiya* — Gif va qiziqarli animatsiyalar\\."
            "\n🌍 *Manzil* — O'zingizning joylashuvingizni ulashing\\."  
            "\n🎥 *Doira shaklidagi video* — E'tiborni jalb qiluvchi maxsus videolar\\."
            "\n📞 *Kontakt* — Kontakt ma'lumotlarini ulashing\\."
            "\n\n\n🛡 *Qulaylik va nazorat:*"
            "\n\n❌ *Bloklash imkoniyati* — Agar kimdir bezovta qilsa, uni bloklab, xabarlar olinishini to'xtatishingiz mumkin\\."
            "\n🛑 *Bekor qilish tugmasi* — Anonim xabar yuborish jarayonini istalgan vaqtda bekor qilishingiz mumkin\\."
            "\n🔄 *Xabar yuborish tugmachasi* — Xabaringizni saqlanmasdan bir zumda uzatamiz\\."
            "\n🚫 *Yangilik va Reklamalar bilan bezovta qilinmaysiz\\❗️*"
            "\n\n\n🤝 *O'zingizni anonim his eting\\!* Biz sizga xavfsiz va ishonchli anonim muloqot muhitini taqdim etamiz\\. Har qanday taklif va savollaringiz bo'lsa, bemalol\\! 😊"
            "\n\n🔗 *Shaxsiy havolangizni oling va do'stlaringiz bilan ulashing\\!*"
            ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        token = get_or_create_token(user_id, user_map)
        await welcome_msg.reply(f"https://t.me/{bot_username}?start={token}")


# Handle sending text and media messages
@dp.message(StateFilter(User.msg))
async def handle_anonymous_message(message: Message, state: FSMContext):
    s_data = await state.get_data()
    prev_msg_id = s_data.get('prev_msg')
    reply_to = s_data.get('reply_to')
    print('MSG ID: ', prev_msg_id)
    print('REPLY TO: ', reply_to)
    if prev_msg_id:
        await bot.delete_message(message.chat.id, prev_msg_id)
        await state.update_data(prev_msg=None)
    recipient_id = s_data.get('recipient_id')
    if recipient_id:
        try:
            my_token = get_or_create_token(message.chat.id, callback_map)
            markup = InlineKeyboardBuilder()
            markup.button(text="Javob yozish", callback_data=f"answer:{my_token}")
            markup.button(text="Bloklash", callback_data=f"block:{my_token}")
            markup = markup.as_markup()
            # Handle different types of media
            if message.text:
                await bot.send_message(
                    chat_id=int(recipient_id),
                    text=message.text,
                    reply_markup=markup,
                )
            elif message.photo:
                await bot.send_photo(
                    chat_id=int(recipient_id),
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    reply_markup=markup,
                )

            elif message.video:
                await bot.send_video(
                    chat_id=int(recipient_id),
                    video=message.video.file_id,
                    caption=message.caption,
                    reply_markup=markup,
                )

            elif message.audio:
                await bot.send_audio(
                    chat_id=int(recipient_id),
                    audio=message.audio.file_id,
                    caption=message.caption,
                    reply_markup=markup,
                )

            elif message.voice:
                await bot.send_voice(
                    chat_id=int(recipient_id),
                    voice=message.voice.file_id,
                    caption=message.caption,
                    reply_markup=markup,
                )

            elif message.document:
                await bot.send_document(
                    chat_id=int(recipient_id),
                    document=message.document.file_id,
                    caption=message.caption,
                    reply_markup=markup,
                )

            elif message.animation:
                await bot.send_animation(
                    chat_id=int(recipient_id),
                    animation=message.animation.file_id,
                    caption=message.caption,
                    reply_markup=markup,
                )

            elif message.location:
                await bot.send_location(
                    chat_id=int(recipient_id),
                    latitude=message.location.latitude,
                    longitude=message.location.longitude,
                    reply_markup=markup,
                )
            elif message.video_note:
                await bot.send_video_note(
                    chat_id=int(recipient_id),
                    video_note=message.video_note.file_id,
                    reply_markup=markup,
                )

            elif message.contact:
                await bot.send_contact(
                    chat_id=int(recipient_id),
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=message.contact.last_name or "",
                    reply_markup=markup,
                )

            elif message.poll:
                await state.clear()
                return await message.reply("Bot pollsni qo'llab quvvatlamaydi. Iltimos, boshqa xabar yuboring!")

            elif message.dice:
                await state.clear()
                return await message.reply("Bot dice (kubik) xabarlarni qo'llab quvvatlamaydi. Iltimos, boshqa xabar yuboring!")
            else:
                await state.clear()
                return await message.reply("Bu turdagi xabarlarni yuborish qo'llab quvvatlanmaydi. Iltimos, boshqa xabar yuboring.")
            await message.answer("Sizning bu xabaringiz ↗️\n👆 Ushbu xabar muallifiga yuborildi", reply_to_message_id=reply_to)
            await state.clear()
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await message.answer("Xabar yetkazilishda muvofaqiyatsizlikka uchradi. Qabul qiluvchiga eltib bo'lmadi.")
    else:
        await message.answer("Nimadir xato ketdi. Iltimos, qaytadan urinib ko'ring.")


# Handle the Cancel button
@dp.callback_query(lambda query: query.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()


# Handle Answer button
@dp.callback_query(lambda query: query.data.startswith("answer:"))
async def answer_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(reply_to=callback.message.message_id)
    token = callback.data.split(":")[1]
    sender_id = callback_map.get(token, None)
    if sender_id is None:
        return await callback.message.reply('Serverda uzilish sodir bolgan. endi bu xabarga javob berolmaysiz')
    if int(sender_id) in blocklist and callback.message.chat.id in blocklist[int(sender_id)]:
        await callback.answer("Siz bu foydalanuvchiga xabar yubora olmaysiz.\nU sizni bloklagan!", show_alert=True)
        return await callback.message.edit_reply_markup(reply_markup=None)
    prev_msg = await callback.message.reply(
        "👆 Ushbu xabar yuboruvchiga javob yozing:",
        reply_markup=InlineKeyboardBuilder().button(text="Cancel", callback_data="cancel").as_markup(),
    )
    await state.set_state(User.msg)
    await state.update_data(prev_msg=prev_msg.message_id, recipient_id=sender_id)


@dp.callback_query(lambda query: query.data.startswith("block:"))
async def block_callback(callback: CallbackQuery):
    token = callback.data.split(":")[1]
    sender_id = callback_map.get(token, None)
    if sender_id is None:
        return await callback.answer("Serverda uzilish sodir bolgan. Endi bu xabar egasini bloklay olmaysiz")
    if int(sender_id) in blocklist and callback.message.chat.id in blocklist[int(sender_id)]:
        await callback.answer("Allaqachon bloklangan", show_alert=True)
        return

    markup = InlineKeyboardBuilder()
    markup.button(text="Ha, Bloklansin", callback_data=f"confirm_block:{token}")
    markup.button(text="Yo'q, fikrimdan qaytdim", callback_data="cancel")
    try:
        await callback.message.reply(
                "Rostdan ham bu xabar yuboruvchisini bloklamoqchimisiz?\nQayta blokdan chiqarishning imkoni yo'q",
                reply_markup=markup.as_markup(),
            )
    except Exception as e:
        logging.error(f"Error in block confirmation: {e}")


# Confirm blocking
@dp.callback_query(lambda query: query.data.startswith("confirm_block:"))
async def confirm_block_callback(callback: CallbackQuery):
    token = callback.data.split(":")[1]
    sender_id = callback_map.get(token, None)
    if sender_id is None:
        return await callback.answer("Serverda uzilish sodir bolgan. Endi bu xabar egasini bloklay olmaysiz")
    recipient_id = callback.message.chat.id

    if recipient_id not in blocklist:
        blocklist[recipient_id] = set()
    blocklist[recipient_id].add(sender_id)

    await callback.message.edit_text("Siz ushbu xabarning yuboruvchisini blokladingiz. Ortiq u sizga xabar yubora olmaydi.")


# Handle /get_my_link command
@dp.message(Command(commands=["get_my_link"]))
async def get_my_link_handler(message: Message):
    user_id = str(message.chat.id)
    bot_username = (await bot.get_me()).username

    token = get_or_create_token(user_id, user_map)

    start_link = f"https://t.me/{bot_username}?start={token}"
    await message.answer(
        f"{start_link}"
    )


@dp.message(Command(commands=["renew_my_link"]))
async def renew_my_link_handler(message: Message):
    user_id = str(message.chat.id)
    bot_username = (await bot.get_me()).username

    need_del = None
    for var, val in user_map.items():
        if val == user_id:
            need_del = var
    if need_del: del user_map[need_del]

    token = get_or_create_token(user_id, user_map)

    start_link = f"https://t.me/{bot_username}?start={token}"
    await message.answer(
        f"Mana sizning yangi linkingiz.\nEndi eski linkingiz orqali sizga bog'lanish ilojsiz.\n{start_link}"
    )


if __name__ == "__main__":
    import asyncio
    dp.message.middleware(ErrorLoggingMiddleware(bot, '-1002266947327'))
    dp.callback_query.middleware(ErrorLoggingMiddleware(bot, '-1002266947327'))
    dp.message.middleware(RateLimitMiddleware(1, 3))
    dp.callback_query.middleware(RateLimitMiddleware(1, 3))    
    asyncio.run(dp.start_polling(bot))
