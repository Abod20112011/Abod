# -*- coding: utf-8 -*-
# ملف start.py - تم تعديله ليتوافق مع سورس عبود المطور V11.0
# جميع حقوق الزخرفة والوظائف محفوظة

import re
import random
import json
import requests
import logging  # <-- تم إضافة هذا السطر لحل الخطأ
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from telethon import Button, events
from telethon.errors import UserIsBlockedError
from telethon.events import CallbackQuery, StopPropagation
from telethon.utils import get_display_name

# === تعديل الاستيرادات لتتوافق مع السورس الجديد ===
# بدلاً من استيراد Config و l313l من السورس القديم، نستورد الدوال من السورس الرئيسي
import sys
import os

# نحصل على الدوال من السورس الرئيسي (الذي تم استيراده في __main__)
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
    # fallback في حالة عدم التمكن من الوصول
    def get_config(key): return None
    def set_config(key, value): pass
    def del_config(key): pass
    OWNER_ID = 6373993992

# === تعريف الجداول المطلوبة للبوت المساعد (إن لم تكن موجودة) ===
class BotPMUsers(Base):
    __tablename__ = "bot_pm_users"
    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger)       # ID الرسالة المحولة للمالك
    first_name = Column(String(255))
    chat_id = Column(BigInteger)          # آيدي المستخدم المراسل
    logger_id = Column(BigInteger)        # ID رسالة المستخدم الأصلية
    result_id = Column(BigInteger, default=0)

class BotStarters(Base):
    __tablename__ = "bot_starters"
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(255))
    date = Column(String(100))
    username = Column(String(255))

class BotBlacklist(Base):
    __tablename__ = "bot_blacklist"
    user_id = Column(BigInteger, primary_key=True)

# إنشاء الجداول إذا لم تكن موجودة
if main_module and hasattr(main_module, 'engine'):
    Base.metadata.create_all(main_module.engine)

# === دوال مساعدة بديلة عن تلك الموجودة في السورس القديم ===
def gvarstatus(key):
    return get_config(key)

def delgvar(key):
    del_config(key)

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

def get_user_logging(message_id):
    return None

def get_user_reply(message_id):
    return None

def ban_user_from_bot(user_id):
    pass

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

def get_user_id(msg_id):
    res = session.query(BotPMUsers).filter(BotPMUsers.message_id == msg_id).first()
    return res.chat_id if res else None

# === دوال عامة ===
async def reply_id(event):
    return event.id

def _format(text, args):
    return text.format(**args) if args else text

# === إعدادات البوت ===
bot_token = get_config("TOKEN")
botusername = ""  # سيتم تعبئته عند التشغيل

# === متغيرات عامة ===
LOGS = logging.getLogger(__name__)
plugin_category = "utils"
Zel_Uid = OWNER_ID
dd = []      # قائمة المستخدمين في وضع الزخرفة
kk = []      # قائمة المستخدمين في وضع إلغاء مؤقت
tt = []      # قائمة المستخدمين في وضع التواصل
whisper_users = []  # قائمة المستخدمين في وضع الفضفضة
arabic_decor_users = []

# إيموجي بريميوم - بدون أسماء ألوان، بأسماء الأزرار
EMOJI_CONTACT = "5258215850745275216"      # ✨ لزر التواصل
EMOJI_DECOR = "5411580731929411768"        # ✅ لزر الزخرفة
EMOJI_DELETE = "5350477112677515642"       # 🔥 لزر الحذف
EMOJI_PAID = "5408997493784467607"         # 💎 لزر المدفوع
EMOJI_CHANNEL = "5260450573768990626"      # ✨ لزر القناة
EMOJI_fatfta = "5188619457651567219"       # فضفضه

# إيموجي بريميوم للتأثيرات
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

# === دالة الإعداد الرئيسية التي سيستدعيها السورس ===
def setup(client):
    """تسجيل جميع الأوامر والمعالجات للبوت المساعد"""
    global botusername

    # جلب اسم مستخدم البوت
    @client.on(events.NewMessage)
    async def get_bot_info(event):
        global botusername
        if not botusername:
            me = await client.get_me()
            botusername = f"@{me.username}" if me.username else ""

    # === الأمر /start ===
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

        first = chat.first_name
        last = chat.last_name
        fullname = f"{first} {last}" if last else first
        username = f"@{chat.username}" if chat.username else mention
        userid = chat.id
        my_first = user.first_name
        my_last = user.last_name
        my_fullname = f"{my_first} {my_last}" if my_last else my_first
        my_username = f"@{user.username}" if user.username else my_mention

        zz_txt = "• المـطـور •"
        zz_ch = gvarstatus("START_BUTUN") or (user.username if user.username else "aqhvv")

        zid = int(gvarstatus("ZThon_Vip") or 5427469031)

        custompic = gvarstatus("BOT_START_PIC") or None

        PREMIUM_EMOJI_ID = 5210763312597326700  # ✨
        EMOJI_HEART = 5258215850745275216        # 💌
        EMOJI_ART = 5411580731929411768        # 🎨
        EMOJI_WARN = 5350477112677515642
        EMOJI_Fatf = 5188619457651567219
        start_msg = f'''\
<tg-emoji emoji-id="{PREMIUM_EMOJI_ID}">✨</tg-emoji> <b>⌔ مـرحباً بـك عزيـزي  {mention} </b>

<tg-emoji emoji-id="{PREMIUM_EMOJI_ID}">🤖</tg-emoji> <b>انـا البـوت الخـاص بـ</b> <code>{my_fullname}</code>

❶ <b>التواصـل مـع مـالكـي مـن هنـا</b> <tg-emoji emoji-id="{EMOJI_HEART}">💌</tg-emoji>
من خـلال زر <b>اضغـط لـ التواصـل</b>
❷ <b>زخـرفـة النصـوص والأسمـاء</b> <tg-emoji emoji-id="{EMOJI_ART}">🎨</tg-emoji>
❸ <b>حـذف الحسـابات نهـائياً</b> <tg-emoji emoji-id="{EMOJI_WARN}">⚠️</tg-emoji>
❹ <b>فَضفـضه بَهوية مجهولـة</b> <tg-emoji emoji-id="{EMOJI_Fatf}">✉️</tg-emoji>
﹎﹎﹎﹎﹎﹎﹎﹎﹎﹎
<tg-emoji emoji-id="{PREMIUM_EMOJI_ID}">👇</tg-emoji> <b>لـ البـدء إستخـدم الازرار بالاسفـل</b>'''

        # الأزرار كما هي في الكود الأصلي مع الحفاظ على الأيقونات
        if chat.id == OWNER_ID and chat.id != zid:
            buttons = [
                [{"text": "زخـارف تمبلـر", "callback_data": "decor_main_menu", "style": "primary", "icon_custom_emoji_id": EMOJI_DECOR}],
                [{"text": "لـ حـذف حسـابك", "callback_data": "zzk_bot-5", "style": "danger", "icon_custom_emoji_id": EMOJI_DELETE}]
            ]
        elif chat.id == OWNER_ID and chat.id == zid:
            buttons = [
                [{"text": "زخـارف تمبلـر", "callback_data": "decor_main_menu", "style": "primary", "icon_custom_emoji_id": EMOJI_DECOR}],
                [{"text": "لـ حـذف حسـابك", "callback_data": "zzk_bot-5", "style": "danger", "icon_custom_emoji_id": EMOJI_DELETE}],
                [{"text": zz_txt, "url": f"https://t.me/{zz_ch}", "style": "primary", "icon_custom_emoji_id": EMOJI_CHANNEL}]
            ]
        else:
            buttons = [
                [{"text": "اضغـط لـ التواصـل", "callback_data": "ttk_bot-1", "style": "primary", "icon_custom_emoji_id": EMOJI_CONTACT}],
                [{"text": "فَضفضة بَهوية مجهولـة", "callback_data": "whisper_menu", "style": "success", "icon_custom_emoji_id": EMOJI_fatfta}],
                [{"text": "لـ حـذف حسـابك", "callback_data": "zzk_bot-5", "style": "Danger", "icon_custom_emoji_id": EMOJI_DELETE}],
                [{"text": "زخـارف تمبلـر", "callback_data": "decor_main_menu", "style": "success", "icon_custom_emoji_id": EMOJI_DECOR}],
                [{"text": zz_txt, "url": f"https://t.me/{zz_ch}", "style": "primary", "icon_custom_emoji_id": EMOJI_CHANNEL}]
            ]

        try:
            if custompic:
                await client.send_file(
                    chat.id,
                    file=custompic,
                    caption='<b>🎉 مرحباً بك في البوت المساعد</b>',
                    link_preview=False,
                    reply_to=reply_to,
                    parse_mode='html'
                )
            # استخدام API لإرسال مع تأثير
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
                fallback_buttons = []
                for row in buttons:
                    btn_row = []
                    for btn in row:
                        if "url" in btn:
                            btn_row.append(Button.url(btn["text"], btn["url"]))
                        else:
                            btn_row.append(Button.inline(btn["text"], data=btn["callback_data"]))
                    fallback_buttons.append(btn_row)
                await event.reply(start_msg, buttons=fallback_buttons, parse_mode='html', link_preview=False)
        except Exception as e:
            LOGS.error(f"❌ خطأ في إرسال رسالة البداية: {str(e)}")
            fallback_buttons = []
            for row in buttons:
                btn_row = []
                for btn in row:
                    if "url" in btn:
                        btn_row.append(Button.url(btn["text"], btn["url"]))
                    else:
                        btn_row.append(Button.inline(btn["text"], data=btn["callback_data"]))
                fallback_buttons.append(btn_row)
            await event.reply(start_msg, buttons=fallback_buttons, parse_mode='html', link_preview=False)

        await check_bot_started_users(chat, event)

    # === معالج الرسائل الخاصة العامة ===
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def bot_pms(event):
        chat = await event.get_chat()
        reply_to = await reply_id(event)
        if check_is_black_list(chat.id):
            return
        if event.contact or int(chat.id) in kk:
            return

        if event.text and event.text.startswith("/start"):
            if chat.id in tt or chat.id in whisper_users:
                return
        if chat.id != OWNER_ID:
            if event.text and event.text.startswith("/cancle"):
                if int(chat.id) in dd:
                    dd.remove(int(chat.id))
                if int(chat.id) in kk:
                    kk.remove(int(chat.id))
                zzc = "**- تم الالغـاء .. بنجـاح**"
                return await client.send_message(chat.id, zzc, link_preview=False, reply_to=reply_to)

            # ========== وضع الفضفضة ==========
            if chat.id in whisper_users:
                sent_msg = await client.send_message(
                    OWNER_ID,
                    f"**💭 رسالة فضفضة:**\n\n{event.text}",
                    parse_mode='md'
                )
                try:
                    add_user_to_db(sent_msg.id, get_display_name(chat), chat.id, event.id, 0)
                except Exception as e:
                    LOGS.error(str(e))
                user = await client.get_me()
                my_mention = f"[{user.first_name}](tg://user?id={user.id})"
                mention = f"[{chat.first_name}](tg://user?id={chat.id})"
                whisper_msg = f"""**⌔ عـزيـزي  {mention} **                            
**⌔ تم ارسـال رسالتـك لـ {my_mention} 💌**                            
**⌔ دون اضهار هويتك .**"""
                buttons = [[Button.inline("❌ تعطيل وضع الفضفضة", data="whisper_off")]]
                await client.send_message(chat.id, whisper_msg, buttons=buttons, reply_to=reply_to, link_preview=False)
                return

            # ========== وضع التواصل العادي ==========
            if int(chat.id) in tt:
                msg = await event.forward_to(OWNER_ID)
                chat = await event.get_chat()
                user = await client.get_me()
                mention = f"[{chat.first_name}](tg://user?id={chat.id})"
                my_mention = f"[{user.first_name}](tg://user?id={user.id})"
                first = chat.first_name
                last = chat.last_name
                fullname = f"{first} {last}" if last else first
                username = f"@{chat.username}" if chat.username else mention
                userid = chat.id
                my_first = user.first_name
                my_last = user.last_name
                my_fullname = f"{my_first} {my_last}" if my_last else my_first
                my_username = f"@{user.username}" if user.username else my_mention
                zz_txt = "⌔ قنـاتـي ⌔"
                zz_ch = gvarstatus("START_BUTUN") or (user.username if user.username else "aqhvv")
                customtasmsg = gvarstatus("TAS_TEXT") or None
                if customtasmsg:
                    tas_msg = customtasmsg.format(
                        zz_mention=mention, first=first, last=last, fullname=fullname,
                        username=username, userid=userid, my_first=my_first, my_last=my_last,
                        my_zname=my_fullname, my_username=my_username, my_mention=my_mention
                    )
                else:
                    tas_msg = f"""**⌔ عـزيـزي  {mention} **                            
**⌔ تم ارسـال رسالتـك لـ {my_fullname} 💌**                            
**⌔ تحلى بالصبـر وانتظـر الـرد 📨.**"""
                buttons = [[Button.inline("تعطيـل التواصـل", data="ttk_bot-off")]]
                await client.send_message(chat.id, tas_msg, link_preview=False, buttons=buttons, reply_to=reply_to)
                try:
                    add_user_to_db(msg.id, get_display_name(chat), chat.id, event.id, 0)
                except Exception as e:
                    LOGS.error(str(e))
                return

            # ========== وضع الزخرفة ==========
            if chat.id in dd:
                text = event.text
                # جميع قوائم الزخرفة كما هي بدون حذف أي حرف
                iitems = ['࿐', '𖣳', '𓃠', '𖡟', '𖠜', '‌♡⁩', '‌༗', '‌𖢖', '❥', '‌ঌ', '𝆹𝅥𝅮', '𖠜', '𖠲', '𖤍', '𖠛', ' 𝅘𝅥𝅮', '‌༒', '‌ㇱ', '߷', 'メ', '〠', '𓃬', '𖠄']
                smiile1 = random.choice(iitems)
                smiile2 = random.choice(iitems)
                smiile3 = random.choice(iitems)
                smiile4 = random.choice(iitems)
                smiile5 = random.choice(iitems)
                smiile6 = random.choice(iitems)
                smiile7 = random.choice(iitems)
                smiile8 = random.choice(iitems)
                smiile9 = random.choice(iitems)
                smiile10 = random.choice(iitems)
                smiile11 = random.choice(iitems)
                smiile12 = random.choice(iitems)
                smiile13 = random.choice(iitems)
                smiile14 = random.choice(iitems)
                smiile15 = random.choice(iitems)
                smiile16 = random.choice(iitems)
                smiile17 = random.choice(iitems)
                smiile18 = random.choice(iitems)
                smiile19 = random.choice(iitems)
                smiile20 = random.choice(iitems)
                smiile21 = random.choice(iitems)
                smiile22 = random.choice(iitems)
                smiile23 = random.choice(iitems)
                smiile24 = random.choice(iitems)
                smiile25 = random.choice(iitems)
                smiile26 = random.choice(iitems)
                smiile27 = random.choice(iitems)
                smiile28 = random.choice(iitems)
                smiile29 = random.choice(iitems)
                smiile30 = random.choice(iitems)
                smiile31 = random.choice(iitems)
                smiile32 = random.choice(iitems)
                smiile33 = random.choice(iitems)
                smiile34 = random.choice(iitems)
                smiile35 = random.choice(iitems)
                smiile36 = random.choice(iitems)
                smiile37 = random.choice(iitems)
                smiile38 = random.choice(iitems)
                smiile39 = random.choice(iitems)
                smiile40 = random.choice(iitems)

                # نصوص الزخرفة (WA1..WA18) كاملة كما هي
                WA1 = text.replace('a', 'ᵃ').replace('A', 'ᴬ').replace('b', 'ᵇ').replace('B', 'ᴮ').replace('c', 'ᶜ').replace('C', 'ᶜ').replace('d', 'ᵈ').replace('D', 'ᴰ').replace('e', 'ᵉ').replace('E', 'ᴱ').replace('f', 'ᶠ').replace('F', 'ᶠ').replace('g', 'ᵍ').replace('G', 'ᴳ').replace('h', 'ʰ').replace('H', 'ᴴ').replace('i', 'ⁱ').replace('I', 'ᴵ').replace('j', 'ʲ').replace('J', 'ᴶ').replace('k', 'ᵏ').replace('K', 'ᴷ').replace('l', 'ˡ').replace('L', 'ᴸ').replace('m', 'ᵐ').replace('M', 'ᴹ').replace('n', 'ⁿ').replace('N', 'ᴺ').replace('o', 'ᵒ').replace('O', 'ᴼ').replace('p', 'ᵖ').replace('P', 'ᴾ').replace('q', '۩').replace('Q', 'Q').replace('r', 'ʳ').replace('R', 'ᴿ').replace('s', 'ˢ').replace('S', 'ˢ').replace('t', 'ᵗ').replace('T', 'ᵀ').replace('u', 'ᵘ').replace('U', 'ᵁ').replace('v', 'ⱽ').replace('V', 'ⱽ').replace('w', 'ʷ').replace('W', 'ᵂ').replace('x', 'ˣ').replace('X', 'ˣ').replace('y', 'ʸ').replace('Y', 'ʸ').replace('z', 'ᶻ').replace('Z', 'ᶻ')
                WA2 = text.replace('a', 'ᴀ').replace('b', 'ʙ').replace('c', 'ᴄ').replace('d', 'ᴅ').replace('e', 'ᴇ').replace('f', 'ғ').replace('g', 'ɢ').replace('h', 'ʜ').replace('i', 'ɪ').replace('j', 'ᴊ').replace('k', 'ᴋ').replace('l', 'ʟ').replace('m', 'ᴍ').replace('n', 'ɴ').replace('o', 'ᴏ').replace('p', 'ᴘ').replace('q', 'ǫ').replace('r', 'ʀ').replace('s', 's').replace('t', 'ᴛ').replace('u', 'ᴜ').replace('v', 'ᴠ').replace('w', 'ᴡ').replace('x', 'x').replace('y', 'ʏ').replace('z', 'ᴢ').replace('A', 'ᴀ').replace('B', 'ʙ').replace('C', 'ᴄ').replace('D', 'ᴅ').replace('E', 'ᴇ').replace('F', 'ғ').replace('G', 'ɢ').replace('H', 'ʜ').replace('I', 'ɪ').replace('J', 'ᴊ').replace('K', 'ᴋ').replace('L', 'ʟ').replace('M', 'ᴍ').replace('N', 'ɴ').replace('O', 'ᴏ').replace('P', 'ᴘ').replace('Q', 'ǫ').replace('R', 'ʀ').replace('S', 'S').replace('T', 'ᴛ').replace('U', 'ᴜ').replace('V', 'ᴠ').replace('W', 'ᴡ').replace('X', 'X').replace('Y', 'ʏ').replace('Z', 'ᴢ')
                WA3 = text.replace('a','α').replace("b","в").replace("c","c").replace("d","∂").replace("e","ε").replace("E","ғ").replace("g","g").replace("h","н").replace("i","ι").replace("j","נ").replace("k","к").replace("l","ℓ").replace("m","м").replace("n","η").replace("o","σ").replace("p","ρ").replace("q","q").replace("r","я").replace("s","s").replace("t","т").replace("u","υ").replace("v","v").replace("w","ω").replace("x","x").replace("y","ү").replace("z","z").replace("A","α").replace("B","в").replace("C","c").replace("D","∂").replace("E","ε").replace("E","ғ").replace("G","g").replace("H","н").replace("I","ι").replace("J","נ").replace("K","к").replace("L","ℓ").replace("M","м").replace("N","η").replace("O","σ").replace("P","ρ").replace("Q","q").replace("R","я").replace("S","s").replace("T","т").replace("U","υ").replace("V","v").replace("W","ω").replace("X","X").replace("Y","ү").replace("Z","z")
                WA4 = text.replace('a','ᥲ').replace('b','ხ').replace('c','ᥴ').replace('d','ძ').replace('e','ᥱ').replace('f','ƒ').replace('g','ᘜ').replace('h','ɦ').replace('i','Ꭵ').replace('j','᧒').replace('k','ƙ').replace('l','ᥣ').replace('m','ꪔ').replace('n','ꪀ').replace('o','᥆').replace('p','ρ').replace('q','ᑫ').replace('r','ᖇ').replace('s','᥉').replace('t','ƚ').replace('u','ᥙ').replace('v','᥎').replace('w','᭙').replace('x','ꪎ').replace('y','ᥡ').replace('z','ᤁ').replace('A','ᥲ').replace('B','ხ').replace('C','ᥴ').replace('D','ძ').replace('E','ᥱ').replace('F','ƒ').replace('G','ᘜ').replace('H','ɦ').replace('I','Ꭵ').replace('J','᧒').replace('K','ƙ').replace('L','ᥣ').replace('M','ꪔ').replace('N','ꪀ').replace('O','᥆').replace('P','ρ').replace('Q','ᑫ').replace('R','ᖇ').replace('S','᥉').replace('T','ƚ').replace('U','ᥙ').replace('V','᥎').replace('W','᭙').replace('X','ꪎ').replace('Y','ᥡ').replace('Z','ᤁ')
                WA5 = text.replace('a','ُِᥲ').replace('b','َِხ').replace('c','ُِᥴ').replace('d','ُძ').replace('e','ُِᥱ').replace('f','َِƒ').replace('g','ᘜ').replace('h','َِɦ').replace('i','َِᎥ').replace('j','َِ᧒').replace('k','َِƙ').replace('l','َِᥣ').replace('m','ُِꪔ').replace('n','َِꪀ').replace('o','ُِ᥆').replace('p','ُِρ').replace('q','ُᑫ').replace('r','َِᖇ').replace('s','َِ᥉').replace('t','َِƚ').replace('u','ُِᥙ').replace('v','ُِ᥎').replace('w','ِ᭙').replace('x','َِꪎ').replace('y','ِᥡ').replace('z','ُِᤁ').replace('A','ُِᥲ').replace('B','َِხ').replace('C','ُِᥴ').replace('D','ُძ').replace('E','ُِᥱ').replace('F','َِƒ').replace('G','ᘜ').replace('H','َِɦ').replace('I','َِᎥ').replace('J','َِ᧒').replace('K','َِƙ').replace('L','َِᥣ').replace('M','ُِꪔ').replace('N','َِꪀ').replace('O','ُِ᥆').replace('P','ُِρ').replace('Q','ُᑫ').replace('R','َِᖇ').replace('S','َِ᥉').replace('T','َِƚ').replace('U','ُِᥙ').replace('V','ُِ᥎').replace('W','ِ᭙').replace('X','َِꪎ').replace('Y','ِᥡ').replace('Z','ُِᤁ')
                WA6 = text.replace('a','ꪖ').replace('b','Ⴆ').replace('c','ᥴ').replace('d','ᦔ').replace('e','꧖').replace('f','ƒ').replace('g','ᧁ').replace('h','ꫝ').replace('i','Ꭵ').replace('j','᧒').replace('k','ƙ').replace('l','ᥣ').replace('m','᧗').replace('n','ᥒ').replace('o','᥆').replace('p','ρ').replace('q','ᑫ').replace('r','ᖇ').replace('s','᥉').replace('t','ﾋ').replace('u','ꪊ').replace('v','ꪜ').replace('w','ꪝ').replace('x','ꪎ').replace('y','ꪗ').replace('z','ᤁ').replace('A','ꪖ').replace('B','Ⴆ').replace('C','ᥴ').replace('D','ᦔ').replace('E','꧖').replace('F','ƒ').replace('G','ᧁ').replace('H','ꫝ').replace('I','Ꭵ').replace('J','᧒').replace('K','ƙ').replace('L','ᥣ').replace('M','᧗').replace('N','ᥒ').replace('O','᥆').replace('P','ρ').replace('Q','ᑫ').replace('R','ᖇ').replace('S','᥉').replace('T','ﾋ').replace('U','ꪊ').replace('V','ꪜ').replace('W','ꪝ').replace('X','ꪎ').replace('Y','ꪗ').replace('Z','ᤁ')
                WA7 = text.replace('a','ُِꪖ').replace('b','َِႦ').replace('c','َِᥴ').replace('d','ُِᦔ').replace('e','ُِ꧖').replace('f','َِƒ').replace('g','ُِᧁ').replace('h','َِꫝ').replace('i','ُِᎥ').replace('j','َِ᧒').replace('k','ُِƙ').replace('l','َِᥣ').replace('m','َِ᧗').replace('n','َِᥒ').replace('o','َِ᥆').replace('p','َِρ').replace('q','ُِᑫ').replace('r','َِᖇ').replace('s','َِ᥉').replace('t','َِﾋ').replace('u','َِꪊ').replace('v','ُِꪜ').replace('w','ُِꪝ').replace('x','َِꪎ').replace('y','ُِꪗ').replace('z','ُِᤁ').replace('A','ُِꪖ').replace('B','َِႦ').replace('C','َِᥴ').replace('D','ُِᦔ').replace('E','ُِ꧖').replace('F','َِƒ').replace('G','ُِᧁ').replace('H','َِꫝ').replace('I','ُِᎥ').replace('J','َِ᧒').replace('K','ُِƙ').replace('L','َِᥣ').replace('M','َِ᧗').replace('N','َِᥒ').replace('O','َِ᥆').replace('P','َِρ').replace('Q','ُِᑫ').replace('R','َِᖇ').replace('S','َِ᥉').replace('T','َِﾋ').replace('U','َِꪊ').replace('V','ُِꪜ').replace('W','ُِꪝ').replace('X','َِꪎ').replace('Y','ُِꪗ').replace('Z','ُِᤁ')
                WA8 = text.replace('a','ᗩ').replace('b','ᗷ').replace('c','ᑕ').replace('d','ᗪ').replace('e','ᗴ').replace('f','ᖴ').replace('g','ᘜ').replace('h','ᕼ').replace('i','I').replace('j','ᒍ').replace('k','K').replace('l','ᒪ').replace('m','ᗰ').replace('n','ᑎ').replace('o','O').replace('p','ᑭ').replace('q','ᑫ').replace('r','ᖇ').replace('s','Տ').replace('t','T').replace('u','ᑌ').replace('v','ᐯ').replace('w','ᗯ').replace('x','᙭').replace('y','Y').replace('z','ᘔ').replace('A','ᗩ').replace('B','ᗷ').replace('C','ᑕ').replace('D','ᗪ').replace('E','ᗴ').replace('F','ᖴ').replace('G','ᘜ').replace('H','ᕼ').replace('I','I').replace('J','ᒍ').replace('K','K').replace('L','ᒪ').replace('M','ᗰ').replace('N','ᑎ').replace('O','O').replace('P','ᑭ').replace('Q','ᑫ').replace('R','ᖇ').replace('S','Տ').replace('T','T').replace('U','ᑌ').replace('V','ᐯ').replace('W','ᗯ').replace('X','᙭').replace('Y','Y').replace('Z','ᘔ')
                WA9 = text.replace('a','𝚊').replace('b','𝚋').replace('c','𝚌').replace('d','𝚍').replace('e','𝚎').replace('f','𝚏').replace('g','𝚐').replace('h','𝚑').replace('i','𝚒').replace('j','𝚓').replace('k','𝚔').replace('l','𝚕').replace('m','𝚖').replace('n','𝚗').replace('o','𝚘').replace('p','𝚙').replace('q','𝚚').replace('r','𝚛').replace('s','𝚜').replace('t','𝚝').replace('u','𝚞').replace('v','𝚟').replace('w','𝚠').replace('x','𝚡').replace('y','𝚢').replace('z','𝚣').replace('A','𝙰').replace('B','𝙱').replace('C','𝙲').replace('D','𝙳').replace('E','𝙴').replace('F','𝙵').replace('G','𝙶').replace('H','𝙷').replace('I','𝙸').replace('J','𝙹').replace('K','𝙺').replace('L','𝙻').replace('M','𝙼').replace('N','𝙽').replace('O','𝙾').replace('P','𝙿').replace('Q','𝚀').replace('R','𝚁').replace('S','𝚂').replace('T','𝚃').replace('U','𝚄').replace('V','𝚅').replace('W','𝚆').replace('X','𝚇').replace('Y','𝚈').replace('Z','𝚉')
                WA10 = text.replace('a','α').replace('b','𝖻').replace('c','ᥴ').replace('d','ძ').replace('e','𝖾').replace('f','𝖿').replace('g','𝗀').replace('h','h').replace('i','Ꭵ').replace('j','𝖩').replace('k','𝗄').replace('l','𝗅').replace('m','𝗆').replace('n','ᥒ').replace('o','᥆').replace('p','𝗉').replace('q','𝗊').replace('r','𝗋').replace('s','𝗌').replace('t','𝗍').replace('u','ᥙ').replace('v','᥎').replace('w','ᥕ').replace('x','ꪎ').replace('y','𝗒').replace('z','ᤁ').replace('A','α').replace('B','𝖻').replace('C','ᥴ').replace('D','ძ').replace('E','𝖾').replace('F','𝖿').replace('G','𝗀').replace('H','h').replace('I','Ꭵ').replace('J','𝖩').replace('K','𝗄').replace('L','𝗅').replace('M','𝗆').replace('N','ᥒ').replace('O','᥆').replace('P','𝗉').replace('Q','𝗊').replace('R','𝗋').replace('S','𝗌').replace('T','𝗍').replace('U','ᥙ').replace('V','᥎').replace('W','ᥕ').replace('X','ꪎ').replace('Y','𝗒').replace('Z','ᤁ')
                WA11 = text.replace('a','𝖺').replace('b','𝖻').replace('c','𝖼').replace('d','𝖽').replace('e','𝖾').replace('f','𝖿').replace('g','𝗀').replace('h','𝗁').replace('i','𝗂').replace('j','𝗃').replace('k','𝗄').replace('l','𝗅').replace('m','𝗆').replace('n','𝗇').replace('o','𝗈').replace('p','𝗉').replace('q','𝗊').replace('r','𝗋').replace('s','𝗌').replace('t','𝗍').replace('u','𝗎').replace('v','𝗏').replace('w','𝗐').replace('x','x').replace('y','𝗒').replace('z','ᴢ').replace('A','𝖠').replace('B','𝖡').replace('C','𝖢').replace('D','𝖣').replace('E','𝖤').replace('F','𝖥').replace('G','𝖦').replace('H','𝖧').replace('I','𝖨').replace('J','𝖩').replace('K','𝖪').replace('L','𝖫').replace('M','𝖬').replace('N','𝖭').replace('O','𝖮').replace('P','𝖯').replace('Q','𝖰').replace('R','𝖱').replace('S','𝖲').replace('T','𝖳').replace('U','𝖴').replace('V','𝖵').replace('W','𝖶').replace('X','𝖷').replace('Y','𝖸').replace('Z','𝖹')
                WA12 = text.replace('a','𝙰').replace('b','𝙱').replace('c','𝙲').replace('d','𝙳').replace('e','𝙴').replace('f','𝙵').replace('g','𝙶').replace('h','𝙷').replace('i','𝙸').replace('j','𝚓').replace('k','𝙺').replace('l','𝙻').replace('m','𝙼').replace('n','𝙽').replace('o','𝙾').replace('p','𝙿').replace('q','𝚀').replace('r','𝚁').replace('s','𝚂').replace('t','𝚃').replace('u','𝚄').replace('v','??').replace('w','𝚆').replace('x','𝚇').replace('y','𝚈').replace('z','𝚉').replace('A','𝙰').replace('B','𝙱').replace('C','𝙲').replace('D','𝙳').replace('E','𝙴').replace('F','𝙵').replace('G','𝙶').replace('H','𝙷').replace('I','𝙸').replace('J','𝚓').replace('K','𝙺').replace('L','𝙻').replace('M','𝙼').replace('N','𝙽').replace('O','𝙾').replace('P','𝙿').replace('Q','𝚀').replace('R','𝚁').replace('S','𝚂').replace('T','𝚃').replace('U','𝚄').replace('V','𝚅').replace('W','𝚆').replace('X','𝚇').replace('Y','𝚈').replace('Z','𝚉')
                WA13 = text.replace('a','🇦 ').replace("b","🇧 ").replace("c","🇨 ").replace("d","🇩 ").replace("e","🇪 ").replace("f","🇫 ").replace("g","🇬 ").replace("h","🇭 ").replace("i","🇮 ").replace("j","🇯 ").replace("k","🇰 ").replace("l","🇱 ").replace("m","🇲 ").replace("n","🇳 ").replace("o","🇴 ").replace("p","🇵 ").replace("q","🇶 ").replace("r","🇷 ").replace("s","🇸 ").replace("t","🇹 ").replace("u","🇻 ").replace("v","🇺 ").replace("w","🇼 ").replace("x","🇽 ").replace("y","🇾 ").replace("z","🇿 ").replace("A","🇦 ").replace("B","🇧 ").replace("C","🇨 ").replace("D","🇩 ").replace("E","🇪 ").replace("F","🇫 ").replace("G","🇬 ").replace("H","🇭 ").replace("I","🇮 ").replace("J","🇯 ").replace("K","🇰 ").replace("L","🇱 ").replace("M","🇲 ").replace("N","🇳 ").replace("O","🇴 ").replace("P","🇵 ").replace("Q","🇶 ").replace("R","🇷 ").replace("S","🇸 ").replace("T","🇹 ").replace("U","🇻 ").replace("V","🇺 ").replace("W","🇼 ").replace("X","🇽 ").replace("Y","🇾 ").replace("Z","🇿 ")
                WA14 = text.replace('a','ⓐ').replace("b","ⓑ").replace("c","ⓒ").replace("d","ⓓ").replace("e","ⓔ").replace("f","ⓕ").replace("g","ⓖ").replace("h","ⓗ").replace("i","ⓘ").replace("j","ⓙ").replace("k","ⓚ").replace("l","ⓛ").replace("m","ⓜ").replace("n","ⓝ").replace("o","ⓞ").replace("p","ⓟ").replace("q","ⓠ").replace("r","ⓡ").replace("s","ⓢ").replace("t","ⓣ").replace("u","ⓤ").replace("v","ⓥ").replace("w","ⓦ").replace("x","ⓧ").replace("y","ⓨ").replace("z","ⓩ").replace("A","Ⓐ").replace("B","Ⓑ").replace("C","Ⓒ").replace("D","Ⓓ").replace("E","Ⓔ").replace("F","Ⓕ").replace("G","Ⓖ").replace("H","Ⓗ").replace("I","Ⓘ").replace("J","Ⓙ").replace("K","Ⓚ").replace("L","Ⓛ").replace("M","🄼").replace("N","Ⓝ").replace("O","Ⓞ").replace("P","Ⓟ").replace("Q","Ⓠ").replace("R","Ⓡ").replace("S","Ⓢ").replace("T","Ⓣ").replace("U","Ⓤ").replace("V","Ⓥ").replace("W","Ⓦ").replace("X","Ⓧ").replace("Y","Ⓨ").replace("Z","Ⓩ")
                WA15 = text.replace('a','🅐').replace("b","🅑").replace("c","🅒").replace("d","🅓").replace("e","🅔").replace("f","🅕").replace("g","🅖").replace("h","🅗").replace("i","🅘").replace("j","🅙").replace("k","🅚").replace("l","🅛").replace("m","🅜").replace("n","🅝").replace("o","🅞").replace("p","🅟").replace("q","🅠").replace("r","🅡").replace("s","🅢").replace("t","🅣").replace("u","🅤").replace("v","🅥").replace("w","🅦").replace("x","🅧").replace("y","🅨").replace("z","🅩").replace("A","🅐").replace("B","🅑").replace("C","🅒").replace("D","🅓").replace("E","🅔").replace("F","🅕").replace("G","🅖").replace("H","🅗").replace("I","🅘").replace("J","🅙").replace("K","🅚").replace("L","🅛").replace("M","🅜").replace("N","🅝").replace("O","🅞").replace("P","🅟").replace("Q","🅠").replace("R","🅡").replace("S","🅢").replace("T","🅣").replace("U","🅤").replace("V","🅥").replace("W","🅦").replace("X","🅧").replace("Y","🅨").replace("Z","🅩")
                WA16 = text.replace('a','🄰').replace("b","🄱").replace("c","🄲").replace("d","🄳").replace("e","🄴").replace("f","🄵").replace("g","🄶").replace("h","🄷").replace("i","🄸").replace("j","🄹").replace("k","🄺").replace("l","🄻").replace("m","🄼").replace("n","🄽").replace("o","🄾").replace("p","🄿").replace("q","🅀").replace("r","🅁").replace("s","🅂").replace("t","🅃").replace("u","🅄").replace("v","🅅").replace("w","🅆").replace("x","🅇").replace("y","🅈").replace("z","🅉").replace("A","🄰").replace("B","🄱").replace("C","🄲").replace("D","🄳").replace("E","🄴").replace("F","🄵").replace("G","🄶").replace("H","🄷").replace("I","🄸").replace("J","🄹").replace("K","🄺").replace("L","🄻").replace("M","🄼").replace("N","🄽").replace("O","🄾").replace("P","🄿").replace("Q","🅀").replace("R","🅁").replace("S","🅂").replace("T","🅃").replace("U","🅄").replace("V","🅅").replace("W","🅆").replace("X","🅇").replace("Y","🅈").replace("Z","🅉")
                WA17 = text.replace('a','🅐').replace("b","🅑").replace("c","🅲").replace("d","🅳").replace("e","🅴").replace("f","🅵").replace("g","🅶").replace("h","🅷").replace("i","🅸").replace("j","🅹").replace("k","🅺").replace("l","🅻").replace("m","🅼").replace("n","🅽").replace("o","🅞").replace("p","🅟").replace("q","🆀").replace("r","🆁").replace("s","🆂").replace("t","🆃").replace("u","🆄").replace("v","🆅").replace("w","🆆").replace("x","🆇").replace("y","🆈").replace("z","🆉").replace("A","🅐").replace("B","🅑").replace("C","🅲").replace("D","🅳").replace("E","🅴").replace("F","🅵").replace("G","🅶").replace("H","🅷").replace("I","🅸").replace("J","🅹").replace("K","🅺").replace("L","🅻").replace("M","🅼").replace("N","🅽").replace("O","🅞").replace("P","🅟").replace("Q","🆀").replace("R","🆁").replace("S","🆂").replace("T","🆃").replace("U","🆄").replace("V","🆅").replace("W","🆆").replace("X","🆇").replace("Y","🆈").replace("Z","🆉")
                WA18 = text.replace('a','𝘢').replace('b','𝘣').replace('c','𝘤').replace('d','𝘥').replace('e','𝘦').replace('f','𝘧').replace('g','𝘨').replace('h','𝘩').replace('i','𝘪').replace('j','𝘫').replace('k','𝘬').replace('l','𝘭').replace('m','𝘮').replace('n','𝘯').replace('o','𝘰').replace('p','𝘱').replace('q','𝘲').replace('r','𝘳').replace('s','𝘴').replace('t','𝘵').replace('u','𝘶').replace('v','𝘷').replace('w','𝘸').replace('x','𝘹').replace('y','𝘺').replace('z','𝘻').replace('A','𝘈').replace('B','𝘉').replace('C','𝘊').replace('D','𝘋').replace('E','𝘌').replace('F','𝘍').replace('G','𝘎').replace('H','𝘏').replace('I','𝘐').replace('J','𝘑').replace('K','𝘒').replace('L','𝘓').replace('M','𝘔').replace('N','𝘕').replace('O','𝘖').replace('P','𝘗').replace('Q','𝘘').replace('R','𝘙').replace('S','𝘚').replace('T','𝘛').replace('U','𝘜').replace('V','𝘝').replace('W','𝘞').replace('X','𝘟').replace('Y','𝘠').replace('Z','𝘡')

                # إرسال النتائج
                reply_text = f"**1-** {WA1}\n\n**2-** {WA2}\n\n**3-** {WA3}\n\n**4-** {WA4}\n\n**5-** {WA5}\n\n**6-** {WA6}\n\n**7-** {WA7}\n\n**8-** {WA8}\n\n**9-** {WA9}\n\n**10-** {WA10}\n\n**11-** {WA11}\n\n**12-** {WA12}\n\n**13-** {WA13}\n\n**14-** {WA14}\n\n**15-** {WA15}\n\n**16-** {WA16}\n\n**17-** {WA17}\n\n**18-** {WA18}"
                await client.send_message(chat.id, reply_text, reply_to=reply_to)
                return

    # === معالجات الأزرار (Callbacks) ===
    @client.on(events.CallbackQuery())
    async def callback_handler(event):
        data = event.data.decode()
        chat_id = event.chat_id
        if data == "decor_main_menu":
            # تفعيل وضع الزخرفة
            if chat_id not in dd:
                dd.append(chat_id)
                await event.answer("✅ تم تفعيل وضع الزخرفة. أرسل النص المراد زخرفته.")
            else:
                dd.remove(chat_id)
                await event.answer("❌ تم تعطيل وضع الزخرفة.")
        elif data == "zzk_bot-5":
            # حذف الحساب (رابط خارجي)
            await event.answer("سيتم توجيهك لصفحة حذف الحساب", alert=True)
            await client.send_message(chat_id, "https://my.telegram.org/auth?to=delete")
        elif data == "ttk_bot-1":
            # تفعيل وضع التواصل
            if chat_id not in tt:
                tt.append(chat_id)
                await event.answer("✅ تم تفعيل وضع التواصل. أرسل رسالتك.")
            else:
                tt.remove(chat_id)
                await event.answer("❌ تم تعطيل وضع التواصل.")
        elif data == "whisper_menu":
            # تفعيل وضع الفضفضة
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

    LOGS.info("✅ تم تحميل موديول start.py بنجاح وتوافقه مع السورس الجديد.")
