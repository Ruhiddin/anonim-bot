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
import string, random
from utils import blocklist as b
from utils import user_token as u
from utils import call_token as c
from utils import token_generator as g
from decorators import valid_link_name
import os


env_path = Path('.env')
load_dotenv(dotenv_path=env_path)
BOT_TOKEN = os.getenv("BOT_TOKEN")
# BOT_TOKEN='7267176194:AAHhOme3QyXxr-Xuk5cSBydSNUI5VLCiUoM'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class User(StatesGroup):
    answer = State()
    msg = State()
    link_name = State()
    edit_link_name = State()


@dp.message(CommandStart())
async def start_handler(message: Message, command: CommandStart, state: FSMContext):
    await state.clear()
    if command.args:
        recipient_token = command.args
        recipient_id = await u.get_user_by_token(recipient_token)
        if not recipient_id:
            return await message.answer("Bu link ortiq ishlamaydi. Foydalanuvchi uni o'chirib yuborgan.")
        try:
            int(recipient_id)

            if await b.is_user_blocked(message.from_user.id, recipient_id):
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
            await state.update_data(prev_msg=prev_msg.message_id, recipient_token=recipient_token)
            await state.set_state(User.msg)
        except ValueError:
            await message.answer("Xato link. Iltimos linki tekshirib, qaytadan urinib ko'ring\n\nEslatma: foydalanuvchi o'z linkini yangilagan bo'lsa, eski linklar bekor qilinadi.")
    else:
        await message.answer(
            (
            "📨 *__ANONIM XABARLAR__ga Xush Kelibsiz\\!*"
            "\n\n*Bu botning afzalligi nimada?\\! Diqqat qiling:*"
            "\n\n🔒 *Xavfsizlik kafolatlangan*: Bot hech qanday Xabarlarni saqlamaydi yoki uchinchi shaxslarga uzatmaydi\\."
            "\n⛓️‍💥 *ID ham oshkor qilinmaydi:* Sababi bot link uchun noyob kodlardan foydalanadi"
            "\n\n\n🎁 *Nimalarni yuborishingiz mumkin?*"
            "\n\n✉️ *Matn* — Oddiy yoki hissiyotli yozuvlar\\."
            "\n🖼 *Rasm* — Har qanday suratlarni ulashing\\."
            "\n📹 *Video* — Oddiy yoki doira shaklidagi videolar\\."
            "\n🎙 *Ovoz* — Audio va Ovozli xabarlar yuborish\\."
            "\n📂 *Hujjat* — Fayllarni biriktirib ulashing\\."
            "\n🐾 *Animatsiya* — Gif va qiziqarli animatsiyalar\\."
            "\n🌍 *Manzil* — O'zingizning joylashuvingizni ulashing\\."  
            "\n🎥 *Doira shaklidagi video* — E'tiborni jalb qiluvchi maxsus videolar\\."
            "\n📞 *Kontakt* — Kontakt ma'lumotlarini ulashing\\."
            "\n\n\n🛡 *__Qulaylik va nazorat:__*"
            "\n\n🔒 *Bloklash imkoniyati* — Agar kimdir bezovta qilsa, uni bloklab qo'yishingiz mumkin\\."
            "\n🔗 *Linklar* — Istalgan sondagi linklar yaratish va boshqarish"
            "\n💬 *Nomlanish* — Linklaringizni nomlash orqali xabar qaysi link orqali yuborilganini bilish imkoni\\."
            "\n↩️ *Javob berish tugmasi* — Istalgan vaqtda istalgan xabarga javob yozish\\."
            "\n❌ *Bekor qilish tugmasi* — Xabar yuborish va boshqa amallarni bekor qilishingiz mumkin\\."
            "\n🔕 *YANGILIK VA REKLAMALAR BILAN BEZOVTA QILINMAYSIZ❗️*"
            "\n\n\n🤝 *O'zingizni anonim his eting\\!* Biz sizga xavfsiz va ishonchli anonim muloqot muhitini taqdim etamiz\\. Har qanday taklif va savollaringiz bo'lsa, bemalol\\! 😊"
            "\n\n🔗 *Shaxsiy havolangizni oling va do'stlaringiz bilan ulashing\\!*"
            "\n *Linklarni Boshqarish: /my\\_links*"
            ),
            parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
        )

@dp.message(StateFilter(User.msg, User.answer))
async def handle_anonymous_message(message: Message, state: FSMContext):
    s_data = await state.get_data()
    prev_msg_id = s_data.get('prev_msg')
    reply_to = s_data.get('reply_to')
    current_state = await state.get_state()
    print('MSG ID: ', prev_msg_id)
    print('REPLY TO: ', reply_to)
    if prev_msg_id:
        await bot.delete_message(message.chat.id, prev_msg_id)
        await state.update_data(prev_msg=None)

    recipient_token = s_data.get('recipient_token')
    if not recipient_token and current_state == User.msg:
        return message.reply("Noma'lum xatolik. Yetkazilmadi")
    if current_state == User.msg: 
        recipient_id = await u.get_user_by_token(recipient_token)
    else:
        recipient_id = s_data.get('recipient_id')
    if recipient_id:
        try:
            my_cb_token = await c.cb_get_token_by_user_id(message.from_user.id)
            if not my_cb_token:
                my_cb_token = await g.unique_callback_token()
                await c.cb_set_user_id(my_cb_token, message.from_user.id)
            markup = InlineKeyboardBuilder()
            markup.button(text="↩️ Javob yozish", callback_data=f"answer:{my_cb_token}")
            markup.button(text="🔒 Bloklash", callback_data=f"block:{my_cb_token}")
            markup = markup.as_markup()
            if current_state == User.msg:
                link_data = await u.get_my_tokens(recipient_id)
                name = link_data.get(recipient_token, 'Nomalum')
                via = f"<{name}> linki orqali"
            else:
                via = 'Javob tugmasi orqali'
            title = f'📨 Anonim Xabar! ({via}) \n\n'
            if message.text:
                await bot.send_message(
                    chat_id=int(recipient_id),
                    text=title + message.text,
                    reply_markup=markup,
                )
            elif message.photo:
                await bot.send_photo(
                    chat_id=int(recipient_id),
                    photo=message.photo[-1].file_id,
                    caption=title + message.caption,
                    reply_markup=markup,
                )

            elif message.video:
                await bot.send_video(
                    chat_id=int(recipient_id),
                    video=message.video.file_id,
                    caption=title + message.caption,
                    reply_markup=markup,
                )

            elif message.audio:
                await bot.send_audio(
                    chat_id=int(recipient_id),
                    audio=message.audio.file_id,
                    caption=title + message.caption,
                    reply_markup=markup,
                )

            elif message.voice:
                await bot.send_voice(
                    chat_id=int(recipient_id),
                    voice=message.voice.file_id,
                    caption=title + message.caption,
                    reply_markup=markup,
                )

            elif message.document:
                await bot.send_document(
                    chat_id=int(recipient_id),
                    document=message.document.file_id,
                    caption=title + message.caption,
                    reply_markup=markup,
                )

            elif message.animation:
                await bot.send_animation(
                    chat_id=int(recipient_id),
                    animation=message.animation.file_id,
                    caption=title + message.caption,
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
            if current_state == User.answer:
                text = "Sizning bu xabaringiz ↗️\n👆 Ushbu xabar muallifiga yuborildi"
            else:
                bot_username = (await bot.get_me()).username
                link = f"https://t.me/{bot_username}?start={recipient_token}"
                text = f"Sizning bu xabaringiz ↗️\n{link} link egasiga yuborildi!"
            await message.answer(text, reply_to_message_id=reply_to, disable_web_page_preview=True)
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
    sender_id = await c.cb_get_user_id(token)
    if sender_id is None:
        return await callback.message.reply('Serverda uzilish sodir bolgan. endi bu xabarga javob berolmaysiz')
    if await b.is_user_blocked(callback.from_user.id, sender_id):
        await callback.answer("Siz bu foydalanuvchiga xabar yubora olmaysiz.\nU sizni bloklagan!", show_alert=True)
        return await callback.message.edit_reply_markup(reply_markup=None)
    prev_msg = await callback.message.reply(
        "👆 Ushbu xabar yuboruvchiga javob yozing:",
        reply_markup=InlineKeyboardBuilder().button(text="Cancel", callback_data="cancel").as_markup(),
    )
    await state.set_state(User.answer)
    await state.update_data(prev_msg=prev_msg.message_id, recipient_id=sender_id)


@dp.callback_query(lambda query: query.data.startswith("block:"))
async def block_callback(callback: CallbackQuery):
    token = callback.data.split(":")[1]
    sender_id = await c.cb_get_user_id(token)
    if sender_id is None:
        return await callback.answer("Serverda uzilish sodir bolgan. Endi bu xabar egasini bloklay olmaysiz")
    if await b.is_user_blocked(callback.from_user.id, sender_id):
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
    sender_id = await c.cb_get_user_id(token)
    if sender_id is None:
        return await callback.answer("Serverda uzilish sodir bolgan. Endi bu xabar egasini bloklay olmaysiz")
    my_id = callback.message.chat.id

    result = await b.user_block(my_id, sender_id)
    if result:
        await callback.message.edit_text("Siz ushbu xabarning yuboruvchisini blokladingiz. Ortiq u sizga xabar yubora olmaydi.")
    else:
        await callback.message.edit_text("Allaqachon blocklagansiz")



@dp.message(Command('my_links'))
async def my_links(message: Message, state: FSMContext):
    user_id = message.chat.id
    links = await u.get_my_tokens(user_id)
    pprint(links)
    
    links_list = [{'token': token, 'name': name} for token, name in links.items()]
    await state.update_data(links=links_list)
    
    markup = InlineKeyboardBuilder()
    
    for i, link in enumerate(links_list, start=1):
        token = link['token']
        name = link['name']
        markup.button(text=f'🔗 {token} 💬 {name}', callback_data=f'my_links:GET_{i}')
    
    markup.button(text="➕ Yangi link", callback_data="my_links:NEW")
    markup.button(text="Yopish ❌", callback_data='my_links:CLOSE')
    
    markup.adjust(*[1 for _ in links_list], 2)
    
    m = await message.reply('Linklaringizni boshqaring', reply_markup=markup.as_markup())
    await state.update_data(prev_msg=m.message_id)



@dp.callback_query(lambda c: 'my_links:' in c.data)
async def my_links(c: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    s_data = await state.get_data()
    links = s_data.get('links')
    act = c.data.split(":")[-1]
    if act == 'CLOSE':
        await c.message.edit_text('Menyu yopildi!')
        return await state.clear()
    elif act == 'NEW':
        await state.set_state(User.link_name)
        text = f'Iltimos, avval yaratilajak linkka nom bering!\nFaqat ingliz harflari, raqamlar va pastki chiziq mumkin'
        cancel_markup = InlineKeyboardBuilder()
        cancel_markup.button(text="🔙 Orqaga", callback_data="my_links:BACK")
        return c.message.edit_text(text, reply_markup=cancel_markup.as_markup())
    elif act.startswith('GET_'):
        index = act.split('_')[-1]
        try:
            link_data = links[int(index) - 1]
            token = link_data.get('token')
            name = link_data.get('name')
            bot_username = (await bot.get_me()).username
            link = f"https://t.me/{bot_username}?start={token}"
            text = f"Nom: {name}\nLink: {link}"
            markup = InlineKeyboardBuilder()
            markup.button(text=f"⛔️ O'chirib yuborish", callback_data=f'my_links:DELETE_{index}')
            markup.button(text=f"✏️ Nomini O'zgartirish", callback_data=f'my_links:UPDATE_{index}')
            markup.button(text='🔙 Orqaga', callback_data='my_links:BACK')
            markup.adjust(2, 1)
            await c.message.edit_text(text, reply_markup=markup.as_markup(), disable_web_page_preview=True)
        except IndexError:
            return await c.answer('Xatolik yuz berdi')

    elif act == 'BACK':
        markup = InlineKeyboardBuilder()
        for i in range(1, len(links) + 1):
            link_data = links[i - 1]
            token = link_data.get('token')
            name = link_data.get('name')
            markup.button(text=f'🔗 {token} 💬 {name}', callback_data=f'my_links:GET_{i}')
        markup.button(text="➕ Yangi link", callback_data="my_links:NEW")
        markup.button(text="Yopish ❌", callback_data='my_links:CLOSE')
        markup.adjust(*[1 for i in links], 2)
        await c.message.edit_text('Linklaringizni boshqaring', reply_markup=markup.as_markup())
    elif act.startswith('DELETE_CONFIRM_'):
        index = act.split('_')[-1]
        try:
            link_data = links[int(index) - 1]
            try:
                token = link_data.get('token')
                name = link_data.get('name')
                result = await u.delete_my_token(c.from_user.id, token)
                if not result:
                    raise LookupError
                bot_username = (await bot.get_me()).username
                link = f"https://t.me/{bot_username}?start={token}"
                text = f"O'chirilgan Link:\n\nNom: {name}\nLink: {link}"
                await c.message.edit_text(text, disable_web_page_preview=True)
                await state.clear()
            except:
                return await c.answer("O'chirishda xatolik yuz berdi!")
            
        except IndexError:
            return await c.answer('Xatolik yuz berdi')
    elif act.startswith('DELETE_'):
        index = act.split('_')[-1]
        try:
            link_data = links[int(index) - 1]
            token = link_data.get('token')
            name = link_data.get('name')
            bot_username = (await bot.get_me()).username
            link = f"https://t.me/{bot_username}?start={token}"
            text = f"Rostdan ham bu linkni o'chirib yubormoqchimisiz?\nAgar shunday qilsangiz ortiq bu link orqali sizga xabar yo'llay olmaydilar\n\nNom: {name}\nLink: {link}"
            markup = InlineKeyboardBuilder()
            markup.button(text=f"Ha, O'chirib tashlansin!", callback_data=f'my_links:DELETE_CONFIRM_{index}')
            markup.button(text='🔙 Orqaga', callback_data=f'my_links:GET_{index}')
            await c.message.edit_text(text, reply_markup=markup.as_markup(), disable_web_page_preview=True)
        except IndexError:
            return await c.answer('Xatolik yuz berdi')
    elif act.startswith('UPDATE_'):
        index = act.split('_')[-1]
        try:
            link_data = links[int(index) - 1]
            token = link_data.get('token')
            name = link_data.get('name')
            bot_username = (await bot.get_me()).username
            link = f"https://t.me/{bot_username}?start={token}"
            text = f"Yangi nomni kiriting:\n\nEski Nom: {name}\nLink: {link}"
            markup = InlineKeyboardBuilder()
            markup.button(text='🔙 Orqaga', callback_data=f'my_links:GET_{index}')
            await c.message.edit_text(text, reply_markup=markup.as_markup(), disable_web_page_preview=True)
            await state.set_state(User.edit_link_name)
            await state.update_data(link=link_data)
        except IndexError:
            return await c.answer('Xatolik yuz berdi')


@dp.message(StateFilter(User.link_name))
@valid_link_name
async def link_name(msg: Message, state: FSMContext):
    s_data = await state.get_data()
    prev_msg_id = s_data.get('prev_msg')
    if prev_msg_id: await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=prev_msg_id, reply_markup=None)
    token = await g.unique_user_token()
    await u.create_my_new_token(msg.from_user.id, token, msg.text)
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={token}"
    await msg.reply(f'Yangi link!\n{link}\nNom: {msg.text}', disable_web_page_preview=True)
    await state.clear()


@dp.message(StateFilter(User.edit_link_name))
@valid_link_name
async def edit_link_name(msg: Message, state: FSMContext):
    s_data = await state.get_data()
    prev_msg_id = s_data.get('prev_msg')
    link_data = s_data.get("link")
    if prev_msg_id: await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=prev_msg_id, reply_markup=None)
    await u.update_my_token(msg.from_user.id, link_data.get('token'), msg.text)
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={link_data.get('token')}"
    await msg.reply(f"Link Nomi O'zgardi!\n\nEski Nom: {link_data.get('name')}\nYangi Nom: {msg.text}\nLink: {link}", disable_web_page_preview=True)
    await state.clear()



@dp.message(Command('help'))
async def help(msg: Message):
    text = """
📖 *Botdan Foydalanish Qo'llanmasi*

📨 *__ANONIM XABARLAR__ga Xush Kelibsiz\\!*  
Bu bot sizga anonim tarzda xabarlar yuborish va qabul qilish imkoniyatini beradi\\. Quyida botdan qanday foydalanish haqida batafsil ma'lumot berilgan:


🔒 *Botning Afzalliklari*
1\\. *Xavfsizlik kafolatlangan*: Bot hech qanday xabarlarni saqlamaydi va uchinchi shaxslarga uzatmaydi\\. Sizning maxfiyligingiz to'liq himoyalangan\\.
2\\. *ID oshkor qilinmaydi*: Bot sizning shaxsingizni yashirish uchun noyob kodlardan foydalanadi\\.
3\\. *Reklamasiz*: Sizni yangiliklar yoki reklamalar bilan bezovta qilmaymiz\\.


🎁 *Nimalarni Yuborishingiz Mumkin?*
Bot orqali quyidagi turdagi xabarlarni yuborishingiz mumkin:
    ✉️ *Matn*: Oddiy yoki hissiyotli yozuvlar\\.
    🖼 *Rasm*: Har qanday suratlarni ulashing\\.
    📹 *Video*: Oddiy yoki doira shaklidagi videolar\\.
    🎙 *Ovoz*: Audio va ovozli xabarlar yuborish\\.
    📂 *Hujjat*: Fayllarni biriktirib ulashing\\.
    🐾 *Animatsiya*: Gif va qiziqarli animatsiyalar\\.
    🌍 *Manzil*: O'zingizning joylashuvingizni ulashing\\.
    🎥 *Doira shaklidagi video*: Maxsus e'tiborni jalb qiluvchi videolar\\.
    📞 *Kontakt*: Kontakt ma'lumotlarini ulashing\\.


🛡 *Qulaylik va Nazorat*
1\\. 🔒 *Bloklash imkoniyati*: Agar kimdir sizni bezovta qilsa, uni bloklab qo'yishingiz mumkin\\.
2\\. 🔗 *Linklar yaratish va boshqarish*: Istalgan sondagi linklarni yaratib, ularni boshqarishingiz mumkin\\.
3\\. 💬 *Nomlanish*: Linklaringizni nomlash orqali xabar qaysi link orqali yuborilganini bilishingiz mumkin\\.
4\\. ↩️ *Javob berish tugmasi*: Istalgan vaqtda istalgan xabarga javob yozish imkoniyati\\.
5\\. ❌ *Bekor qilish tugmasi*: Xabar yuborish yoki boshqa amallarni bekor qilishingiz mumkin\\.


🔗 *Shaxsiy Havolangizni Olish*
1\\. Shaxsiy havolangizni olish uchun `/my_links` buyrug'idan foydalaning\\.
2\\. Havolani do'stlaringiz bilan ulashing va anonim xabarlarni qabul qiling\\.


📋 *Botdan Foydalanish Bo'yicha Qo'llanma*
1\\. *Xabar Yuborish*:
    Shaxsiy havolangizni ulashgan odamlar sizga anonim xabarlar yuborishi mumkin\\.
    Siz yuborilgan xabarlarga javob yozishingiz mumkin\\.

2\\. *Linklarni Boshqarish*:
    `/my_links` buyrug'ini yuboring\\.
    O'z linklaringizni ko'ring, yangi link yarating yoki mavjudlarini boshqaring\\.

3\\. *Bloklash*:
    Sizni bezovta qilayotgan foydalanuvchini bloklash uchun tegishli tugmani bosing\\.

4\\. *Xabarlarni Bekor Qilish*:
    Xabar yuborish jarayonini bekor qilish uchun "Bekor qilish" tugmasidan foydalaning\\.


🤝 *Bizning Maqsadimiz*
Biz sizga xavfsiz va ishonchli anonim muloqot muhitini taqdim etamiz\\. Har qanday savol yoki takliflaringiz bo'lsa, biz bilan bemalol bog'laning\\! 😊

🔗 *Shaxsiy havolangizni oling va do'stlaringiz bilan ulashing\\!*  
👉 *Linklarni boshqarish uchun*: /my\\_links

⁉️ *Savol va Takliflar uchun:* [Muhokama guruhi](https://t.me/pure_ideas/66/68)
    """
    await msg.reply(text, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)  # type: ignore









@dp.message(Command('manufacturer'))
async def manufacturer(msg: Message):
    await msg.reply('https://t.me/tezbots')











if __name__ == "__main__":
    import asyncio
    dp.message.middleware(ErrorLoggingMiddleware(bot, '-1002266947327'))
    dp.callback_query.middleware(ErrorLoggingMiddleware(bot, '-1002266947327'))
    dp.message.middleware(RateLimitMiddleware(1, 3))
    dp.callback_query.middleware(RateLimitMiddleware(1, 3))    
    asyncio.run(dp.start_polling(bot))
