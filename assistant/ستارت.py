# -*- coding: utf-8 -*-
# ملف start.py - نسخة مبسطة بدون زخرفة - متوافقة مع سورس عبود V11.0

import json
import requests
import logging
from collections import defaultdict
from datetime import datetime

from telethon import Button, events
from telethon.utils import get_display_name

import sys

# الوصول إلى دوال القاعدة من السورس الرئيسي
main_module = sys.modules.get('__main__')
if main_module:
    get_config = main_module.get_config
    set_config = main_module.set_config
    del_config = main_module.del_config
    session = main_module.session
    Base = main_module.Base
    Column = main_module.Column
    String = main_module.String
    BigInteger = main_module.BigInteger
    Integer = main_module.Integer
    OWNER_ID = main_module.OWNER_ID
else:
    def get_config(key): return None
    def set_config(key, value): pass
    def del_config(key): pass
    OWNER_ID = 6373993992

# جداول قاعدة البيانات المطلوبة
class BotPMUsers(Base):
    __tablename__ = "bot_pm_users"
    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger)
    first_name = Column(String(255))
    chat_id = Column(BigInteger)
    logger_id = Column(BigInteger)
    result_id = Column(Integer, default=0)

class BotStarters(Base):
    __tablename__ = "bot_starters"
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(255))
    date = Column(String(100))
    username = Column(String(255))

class BotBlacklist(Base):
    __tablename__ = "bot_blacklist"
    user_id = Column(BigInteger, primary_key=True)

if main_module and hasattr(main_module, 'engine'):
    Base.metadata.create_all(main_module.engine)

# دوال مساعدة
def gvarstatus(key):
    return get_config(key)

def add_starter_to_db(user_id, first_name, date, username):
    try:
        res = session.query(BotStarters).filter(BotStarters.user_id == user_id).first()
        if not res:
            new = BotStarters(user_id=user_id, first_name=first_name, date=date, username=username)
            session.add(new)
            session.commit()
    except:
        session.rollback()

def get_starter_details(user_id):
    return session.query(BotStarters).filter(BotStarters.user_id == user_id).first()

def check_is_black_list(user_id):
    return session.query(BotBlacklist).filter(BotBlacklist.user_id == user_id).first() is not None

def add_user_to_db(msg_id, first_name, chat_id, logger_id, result_id, reply_id=0):
    try:
        new = BotPMUsers(
            message_id=msg_id,
            first_name=first_name,
            chat_id=chat_id,
            logger_id=logger_id,
            result_id=result_id
        )
        session.add(new)
        session.commit()
    except:
        session.rollback()

async def reply_id(event):
    return event.id

# إعدادات عامة
LOGS = logging.getLogger(__name__)
bot_token = get_config("TOKEN")
botusername = ""

# قوائم المستخدمين
kk = []              # وضع إلغاء مؤقت
tt = []              # وضع التواصل
whisper_users = []   # وضع الفضفضة

# الإيموجيات المميزة
EMOJI_CONTACT = "5258215850745275216"
EMOJI_DELETE = "5350477112677515642"
EMOJI_CHANNEL = "5260450573768990626"
EMOJI_fatfta = "5188619457651567219"
EFFECT_ID = "5046509860389126442"

class FloodConfig:
    BANNED_USERS = set()
    USERS = defaultdict(list)
    MESSAGES = 3
    SECONDS = 6
    ALERT = defaultdict(dict)
    AUTOBAN = 10

async def check_bot_started_users(user, event):
    if user.id == OWNER_ID:
        return
    check = get_starter_details(user.id)
    usernaam = f"@{user.username}" if user.username else "لايوجـد"
    if check is None:
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        notification = f"<b>مرحبـاً سيـدي 🧑🏻‍💻</b>\n<b>شخـص قام بالدخـول لـ البـوت المسـاعـد 💡</b>\n\n<b>الاسـم : </b>{get_display_name(user)}\n<b>الايـدي : </b><code>{user.id}</code>\n<b>اليـوزر :</b> {usernaam}"
    else:
        start_date = check.date
        notification = f"<b>مرحبـاً سيـدي 🧑🏻‍💻</b>\n<b>شخـص قام بالدخـول لـ البـوت المسـاعـد 💡</b>\n\n<b>الاسـم : </b>{get_display_name(user)}\n<b>الايـدي : </b><code>{user.id}</code>\n<b>اليـوزر :</b> {usernaam}"
    try:
        add_starter_to_db(user.id, get_display_name(user), start_date, user.username)
    except Exception as e:
        LOGS.error(str(e))
    if gvarstatus("BOTLOG_CHATID"):
        await event.client.send_message(int(gvarstatus("BOTLOG_CHATID")), notification, parse_mode='html')

# ========== دالة الإعداد ==========
def setup(client):
    global botusername

    # جلب معلومات الحساب الشخصي (المطور) عند بدء التشغيل
    owner_info = {"name": "المطور", "username": ""}

    @client.on(events.NewMessage)
    async def get_bot_info(event):
        global botusername
        if not botusername:
            me = await client.get_me()
            botusername = f"@{me.username}" if me.username else ""
        # تحديث معلومات المطور
        try:
            owner = await client.get_entity(OWNER_ID)
            owner_info["name"] = get_display_name(owner)
            owner_info["username"] = owner.username if owner.username else ""
        except:
            pass

    # ========== الأمر /start ==========
    @client.on(events.NewMessage(incoming=True, pattern=r'^/start'))
    async def bot_start(event):
        if not event.is_private:
            return
        chat = await event.get_chat()
        user = await client.get_me()
        if check_is_black_list(chat.id):
            return
        if int(chat.id) in kk:
            kk.remove(int(chat.id))
        reply_to = await reply_id(event)

        mention = f'<a href="tg://user?id={chat.id}">{chat.first_name}</a>'
        my_mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

        my_fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

        # استخدام معلومات المطور من الجلسة
        dev_name = owner_info["name"]
        dev_uname = owner_info["username"]
        dev_url = f"https://t.me/{dev_uname}" if dev_uname else f"tg://user?id={OWNER_ID}"
        dev_text = dev_name

        PREMIUM_EMOJI_ID = 5210763312597326700
        EMOJI_HEART = 5258215850745275216
        EMOJI_WARN = 5350477112677515642
        EMOJI_Fatf = 5188619457651567219

        start_msg = f'''\
<tg-emoji emoji-id="{PREMIUM_EMOJI_ID}">✨</tg-emoji> <b>⌔ مـرحباً بـك عزيـزي  {mention} </b>

<tg-emoji emoji-id="{PREMIUM_EMOJI_ID}">🤖</tg-emoji> <b>انـا البـوت الخـاص بـ</b> <code>{my_fullname}</code>

❶ <b>التواصـل مـع مـالكـي مـن هنـا</b> <tg-emoji emoji-id="{EMOJI_HEART}">💌</tg-emoji>
من خـلال زر <b>اضغـط لـ التواصـل</b>
❷ <b>حـذف الحسـابات نهـائياً</b> <tg-emoji emoji-id="{EMOJI_WARN}">⚠️</tg-emoji>
❸ <b>فَضفـضه بَهوية مجهولـة</b> <tg-emoji emoji-id="{EMOJI_Fatf}">✉️</tg-emoji>
﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎
<tg-emoji emoji-id="{PREMIUM_EMOJI_ID}">👇</tg-emoji> <b>لـ البـدء إستخـدم الازرار بالاسفـل</b>'''

        # أزرار بسيطة بدون زخرفة
        if chat.id == OWNER_ID:
            buttons = [
                [{"text": "لـ حـذف حسـابك", "callback_data": "zzk_bot-5", "style": "danger", "icon_custom_emoji_id": EMOJI_DELETE}]
            ]
        else:
            buttons = [
                [{"text": "اضغـط لـ التواصـل", "callback_data": "ttk_bot-1", "style": "primary", "icon_custom_emoji_id": EMOJI_CONTACT}],
                [{"text": "فَضفضة بَهوية مجهولـة", "callback_data": "whisper_menu", "style": "success", "icon_custom_emoji_id": EMOJI_fatfta}],
                [{"text": "لـ حـذف حسـابك", "callback_data": "zzk_bot-5", "style": "danger", "icon_custom_emoji_id": EMOJI_DELETE}],
                [{"text": dev_text, "url": dev_url, "style": "primary", "icon_custom_emoji_id": EMOJI_CHANNEL}]
            ]

        try:
            custompic = gvarstatus("BOT_START_PIC")
            if custompic:
                await client.send_file(chat.id, file=custompic, caption='<b>🎉 مرحباً بك في البوت المساعد</b>', link_preview=False, reply_to=reply_to, parse_mode='html')
            send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            send_data = {
                "chat_id": chat.id,
                "text": start_msg,
                "parse_mode": "HTML",
                "reply_markup": json.dumps({"inline_keyboard": buttons}),
                "disable_web_page_preview": True,
                "message_effect_id": EFFECT_ID
            }
            response = requests.post(send_url, json=send_data, timeout=3)
            if response.status_code != 200:
                # fallback
                fb = []
                for row in buttons:
                    r = []
                    for b in row:
                        if "url" in b: r.append(Button.url(b["text"], b["url"]))
                        else: r.append(Button.inline(b["text"], data=b["callback_data"]))
                    fb.append(r)
                await event.reply(start_msg, buttons=fb, parse_mode='html', link_preview=False)
        except Exception as e:
            LOGS.error(f"خطأ start: {e}")

        await check_bot_started_users(chat, event)

    # ========== معالج الرسائل الخاصة ==========
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def bot_pms(event):
        chat = await event.get_chat()
        reply_to = await reply_id(event)
        if check_is_black_list(chat.id) or event.contact or int(chat.id) in kk:
            return
        if event.text and event.text.startswith("/start"):
            if chat.id in tt or chat.id in whisper_users:
                return
        if chat.id != OWNER_ID:
            if event.text and event.text.startswith("/cancle"):
                for lst in [kk, tt, whisper_users]:
                    if chat.id in lst: lst.remove(chat.id)
                return await client.send_message(chat.id, "**- تم الالغـاء .. بنجـاح**")

            # وضع الفضفضة
            if chat.id in whisper_users:
                sent = await client.send_message(OWNER_ID, f"**💭 رسالة فضفضة:**\n\n{event.text}", parse_mode='md')
                add_user_to_db(sent.id, get_display_name(chat), chat.id, event.id, 0)
                user = await client.get_me()
                mention = f"[{chat.first_name}](tg://user?id={chat.id})"
                my_mention = f"[{user.first_name}](tg://user?id={user.id})"
                await client.send_message(chat.id, f"**⌔ عـزيـزي  {mention} **\n**⌔ تم ارسـال رسالتـك لـ {my_mention} 💌**\n**⌔ دون اضهار هويتك .**",
                                          buttons=[[Button.inline("❌ تعطيل وضع الفضفضة", data="whisper_off")]], reply_to=reply_to)
                return

            # وضع التواصل
            if chat.id in tt:
                msg = await event.forward_to(OWNER_ID)
                add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0)
                user = await client.get_me()
                mention = f"[{chat.first_name}](tg://user?id={chat.id})"
                my_fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
                await client.send_message(chat.id, f"**⌔ عـزيـزي  {mention} **\n**⌔ تم ارسـال رسالتـك لـ {my_fullname} 💌**\n**⌔ تحلى بالصبـر وانتظـر الـرد 📨.**",
                                          buttons=[[Button.inline("تعطيـل التواصـل", data="ttk_bot-off")]], reply_to=reply_to)
                return

    # ========== معالج الأزرار (Callbacks) ==========
    @client.on(events.CallbackQuery())
    async def callback_handler(event):
        data = event.data.decode()
        chat_id = event.chat_id

        if data == "zzk_bot-5":
            await event.answer("سيتم توجيهك لصفحة حذف الحساب", alert=True)
            await client.send_message(chat_id, "https://my.telegram.org/auth?to=delete")
        elif data == "ttk_bot-1":
            if chat_id not in tt:
                tt.append(chat_id)
                await event.answer("✅ تم تفعيل وضع التواصل. أرسل رسالتك.")
            else:
                tt.remove(chat_id)
                await event.answer("❌ تم تعطيل وضع التواصل.")
        elif data == "whisper_menu":
            if chat_id not in whisper_users:
                whisper_users.append(chat_id)
                await event.answer("✅ تم تفعيل وضع الفضفضة. أرسل رسالتك.")
            else:
                whisper_users.remove(chat_id)
                await event.answer("❌ تم تعطيل وضع الفضفضة.")
        elif data == "whisper_off":
            if chat_id in whisper_users:
                whisper_users.remove(chat_id)
                await event.answer("❌ تم تعطيل وضع الفضفضة.")
        elif data == "ttk_bot-off":
            if chat_id in tt:
                tt.remove(chat_id)
                await event.answer("❌ تم تعطيل وضع التواصل.")

    LOGS.info("✅ تم تحميل موديول start.py (نسخة خالية من الزخرفة).")
