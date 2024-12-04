# from aiogram import Bot, Dispatcher
# from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
# from aiogram.filters import CommandStart, Command
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# import logging
# import random
# import string

# # Logging setup
# logging.basicConfig(level=logging.INFO)

# # Bot initialization
# BOT_TOKEN = "8024236657:AAG2mTsP1KRtNltfF5RZZESslvW_Nix9NFI"  # Replace with your bot's token
# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()

# # In-memory store
# pending_messages = {}  # Format: {sender_id: recipient_id}
# blocklist = {}  # Format: {recipient_id: set(sender_ids)}
# previous_messages = {}  # Format: {recipient_id: (message_id, inline_buttons)}
# user_links = {}  # Format: {user_id: unique_code}
# link_to_user = {}  # Format: {unique_code: user_id}


# # Generate a unique code for links
# def generate_unique_code(length=8):
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# # Handle /start command
# @dp.message(CommandStart())
# async def start_handler(message: Message, command: CommandStart):
#     if command.args:
#         unique_code = command.args
#         recipient_id = link_to_user.get(unique_code)

#         if recipient_id:
#             # Check if the recipient has blocked the sender
#             if recipient_id in blocklist and message.chat.id in blocklist[recipient_id]:
#                 await message.answer("You cannot send a message to this user.")
#                 return

#             keyboard = InlineKeyboardBuilder()
#             keyboard.button(text="Cancel", callback_data="cancel")
#             await message.answer(
#                 "Send your anonymous message, photo, or video below. "
#                 "Click 'Cancel' if you change your mind.",
#                 reply_markup=markup,
#             )
#             pending_messages[message.chat.id] = recipient_id
#         else:
#             await message.answer("Invalid link. Please check the link and try again.")
#     else:
#         user_id = str(message.chat.id)
#         bot_username = (await bot.get_me()).username

#         # Generate or retrieve the user's unique link
#         if user_id not in user_links:
#             unique_code = generate_unique_code()
#             user_links[user_id] = unique_code
#             link_to_user[unique_code] = user_id
#         else:
#             unique_code = user_links[user_id]

#         start_link = f"https://t.me/{bot_username}?start={unique_code}"
#         await message.answer(
#             f"Welcome to the Anonymous Messaging Bot!\n\n"
#             f"Share this link with others to receive anonymous messages:\n{start_link}"
#         )



# # Handle sending text and media messages
# @dp.message(lambda message: message.chat.id in pending_messages)
# async def handle_anonymous_message(message: Message):
#     recipient_id = pending_messages.pop(message.chat.id, None)
#     if recipient_id:
#         try:
#             keyboard = InlineKeyboardBuilder()
#             keyboard.button(text="Answer", callback_data=f"answer:{message.chat.id}")
#             keyboard.button(text="Block", callback_data=f"block:{message.chat.id}")

#             sent_message = None
#             if message.photo:
#                 sent_message = await bot.send_photo(
#                     chat_id=int(recipient_id),
#                     photo=message.photo[-1].file_id,
#                     caption=message.caption,
#                     reply_markup=markup,
#                 )
#             elif message.video:
#                 sent_message = await bot.send_video(
#                     chat_id=int(recipient_id),
#                     video=message.video.file_id,
#                     caption=message.caption,
#                     reply_markup=markup,
#                 )
#             elif message.document:
#                 sent_message = await bot.send_document(
#                     chat_id=int(recipient_id),
#                     document=message.document.file_id,
#                     caption=message.caption,
#                     reply_markup=markup,
#                 )
#             else:
#                 sent_message = await bot.send_message(
#                     chat_id=int(recipient_id),
#                     text=f"Anonim xabar:\n\n{message.text}",
#                     reply_markup=markup,
#                 )

#             if sent_message:
#                 # Store the previous message's ID and inline buttons
#                 previous_messages[int(recipient_id)] = (sent_message.message_id, markup)

#             await message.answer("Your anonymous message has been sent!")
#         except Exception as e:
#             logging.error(f"Error sending message: {e}")
#             await message.answer("Failed to deliver the message. The recipient may not be reachable.")
#     else:
#         await message.answer("An error occurred. Please try again.")

# # Run the bot
# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(dp.start_polling(bot))

from pprint import pprint
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from middlewares.error_loggin_middleware import ErrorLoggingMiddleware
from middlewares.rate_limit_middleware import RateLimitMiddleware
import logging
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)
# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Bot initialization
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# In-memory store for pending message states and blocklist
pending_messages = {}  # Format: {sender_id: recipient_id}
blocklist = {}  # Format: {recipient_id: set(sender_ids)}


# Handle /start command
@dp.message(CommandStart())
async def start_handler(message: Message, command: CommandStart, state: FSMContext):
    if command.args:
        recipient_id = command.args
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
            await state.update_data(prev_msg=prev_msg.message_id)
            pending_messages[message.chat.id] = recipient_id
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
            "\n\n\n🤝 *O'zingizni anonim his eting\\!* Biz sizga xavfsiz va ishonchli anonim muloqot muhitini taqdim etamiz\\. Har qanday taklif va savollaringiz bo'lsa, bemalol\\! 😊"
            "\n\n🔗 *Shaxsiy havolangizni oling va do'stlaringiz bilan ulashing\\!*"
            ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await welcome_msg.reply(f"https://t.me/{bot_username}?start={user_id}")


# Handle sending text and media messages
@dp.message(lambda message: message.chat.id in pending_messages)
async def handle_anonymous_message(message: Message, state: FSMContext):
    s_data = await state.get_data()
    prev_msg_id = s_data.get('prev_msg')
    reply_to = s_data.get('reply_to')
    print('MSG ID: ', prev_msg_id)
    print('REPLY TO: ', reply_to)
    if prev_msg_id:
        await bot.delete_message(message.chat.id, prev_msg_id)
        await state.update_data(prev_msg=None)
    recipient_id = pending_messages.pop(message.chat.id, None)
    if recipient_id:
        try:
            markup = InlineKeyboardBuilder()
            markup.button(text="Javob yozish", callback_data=f"answer:{message.chat.id}")
            markup.button(text="Bloklash", callback_data=f"block:{message.chat.id}")
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
            await state.clear()
            await message.answer("Sizning bu xabaringiz ↗️\n👆 Ushbu xabar muallifiga yuborildi", reply_to_message_id=reply_to)
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            await message.answer("Xabar yetkazilishda muvofaqiyatsizlikka uchradi. Qabul qiluvchiga eltib bo'lmadi.")
    else:
        await message.answer("Nomalum xato sodir bo'ldi. Qaytadan urinib ko'ring.")


# Handle the Cancel button
@dp.callback_query(lambda query: query.data == "cancel")
async def cancel_callback(callback: CallbackQuery):
    if callback.message.chat.id in pending_messages:
        pending_messages.pop(callback.message.chat.id)
    await callback.message.delete()


# Handle Answer button
@dp.callback_query(lambda query: query.data.startswith("answer:"))
async def answer_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(reply_to=callback.message.message_id)
    sender_id = int(callback.data.split(":")[1])
    if int(sender_id) in blocklist and callback.message.chat.id in blocklist[int(sender_id)]:
        await callback.answer("Siz bu foydalanuvchiga xabar yubora olmaysiz.\nU sizni bloklagan!", show_alert=True)
        return await callback.message.edit_reply_markup(reply_markup=None)
    try:
        prev_msg = await callback.message.reply(
            "👆 Ushbu xabar yuboruvchiga javob yozing:",
            reply_markup=InlineKeyboardBuilder().button(text="Cancel", callback_data="cancel").as_markup(),
        )
        await state.update_data(prev_msg=prev_msg.message_id)
        pending_messages[callback.message.chat.id] = sender_id
    except Exception as e:
        logging.error(f"Error in answering: {e}")


# Handle Block button
@dp.callback_query(lambda query: query.data.startswith("block:"))
async def block_callback(callback: CallbackQuery):
    sender_id = int(callback.data.split(":")[1])
    # recipient_id = callback.message.chat.id
    if int(sender_id) in blocklist and callback.message.chat.id in blocklist[int(sender_id)]:
        await callback.answer("Allaqachon bloklangan", show_alert=True)
        return

    # Ask for confirmation
    markup = InlineKeyboardBuilder()
    markup.button(text="Ha, Bloklansin", callback_data=f"confirm_block:{sender_id}")
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
    sender_id = int(callback.data.split(":")[1])
    recipient_id = callback.message.chat.id

    if recipient_id not in blocklist:
        blocklist[recipient_id] = set()
    blocklist[recipient_id].add(sender_id)

    await callback.message.edit_text("Siz ushbu xabarning yuboruvchisini blokladingiz. Ortiq u sizga xabar yubora olmaydi.")


# Handle /get_my_link command
@dp.message(Command(commands=["get_my_link"]))
async def get_my_link_handler(message: Message):
    await message.reply('Kechirasiz, hozircha link olish imkoniyati mavjud emas.')
    # user_id = str(message.chat.id)
    # bot_username = (await bot.get_me()).username

    # # Retrieve or generate the user's unique link
    # if user_id not in user_links:
    #     unique_code = generate_unique_code()
    #     user_links[user_id] = unique_code
    #     link_to_user[unique_code] = user_id
    # else:
    #     unique_code = user_links[user_id]

    # start_link = f"https://t.me/{bot_username}?start={unique_code}"
    # await message.answer(
    #     f"Here is your anonymous message link:\n{start_link}"
    # )


# Handle /renew_my_link command
@dp.message(Command(commands=["renew_my_link"]))
async def renew_my_link_handler(message: Message):
    await message.reply('Kechirasiz, hozircha linkni yangilarsh imkoniyati mavjud emas')
    # user_id = str(message.chat.id)
    # bot_username = (await bot.get_me()).username

    # # Generate a new unique link
    # if user_id in user_links:
    #     # Remove the old link from the mapping
    #     old_code = user_links[user_id]
    #     if old_code in link_to_user:
    #         del link_to_user[old_code]

    # # Generate a new link
    # unique_code = generate_unique_code()
    # user_links[user_id] = unique_code
    # link_to_user[unique_code] = user_id

    # start_link = f"https://t.me/{bot_username}?start={unique_code}"
    # await message.answer(
    #     f"Your anonymous message link has been renewed:\n{start_link}"
    # )


# Run the bot
if __name__ == "__main__":
    import asyncio
    dp.message.middleware(ErrorLoggingMiddleware(bot, '-1002266947327'))
    dp.callback_query.middleware(ErrorLoggingMiddleware(bot, '-1002266947327'))
    dp.message.middleware(RateLimitMiddleware(1, 3))
    dp.callback_query.middleware(RateLimitMiddleware(1, 3))    
    asyncio.run(dp.start_polling(bot))
