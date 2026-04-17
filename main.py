# -*- coding: utf-8 -*-
# سورس عبود المطور - النسخة الشاملة v9.0
# مبرمج لدعم ميزات التنصيب التلقائي، تحديث المكاتب، وأتمتة BotFather

import os
import sys
import asyncio
import importlib.util
import subprocess
import types
import logging
import shutil
import time
import re
from datetime import datetime

# --- [ 1. إعدادات قاعدة البيانات (SQLAlchemy) - كما طلبت بدون حذف ] ---
from sqlalchemy import create_engine, Column, String, BigInteger, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# إعداد قاعدة البيانات (تستخدم SQLite افتراضياً)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///abood_data.db")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Config(Base):
    __tablename__ = "config"
    variable = Column(String(255), primary_key=True)
    value = Column(String(255), nullable=False)

class MutedUsers(Base):
    __tablename__ = "muted_users"
    user_id = Column(BigInteger, primary_key=True)
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)

class Stats(Base):
    __tablename__ = "stats"
    plugin_name = Column(String(255), primary_key=True)
    count = Column(Integer, default=0)

# إنشاء الجداول فوراً لضمان عدم حدوث خطأ (no such table)
Base.metadata.create_all(engine)

# --- دوال قاعدة البيانات المدمجة ---

def get_config(variable_name):
    """جلب إعداد معين من قاعدة البيانات"""
    res = session.query(Config).filter(Config.variable == variable_name).first()
    return res.value if res else None

def set_config(variable_name, value):
    """حفظ أو تحديث إعداد"""
    res = session.query(Config).filter(Config.variable == variable_name).first()
    if res:
        res.value = str(value)
    else:
        res = Config(variable=variable_name, value=str(value))
        session.add(res)
    session.commit()

def del_config(variable_name):
    """حذف إعداد معين"""
    res = session.query(Config).filter(Config.variable == variable_name).first()
    if res:
        session.delete(res)
        session.commit()

def is_muted(user_id):
    """التحقق إذا كان المستخدم مكتوماً"""
    res = session.query(MutedUsers).filter(MutedUsers.user_id == user_id).first()
    return True if res else False

def add_muted(user_id, full_name=None, username=None):
    """إضافة مستخدم لقائمة الكتم"""
    if not is_muted(user_id):
        new_mute = MutedUsers(user_id=user_id, full_name=full_name, username=username)
        session.add(new_mute)
        session.commit()

def remove_muted(user_id):
    """إلغاء كتم مستخدم"""
    res = session.query(MutedUsers).filter(MutedUsers.user_id == user_id).first()
    if res:
        session.delete(res)
        session.commit()

def get_all_muted():
    """جلب كل المكتومين بتنسيق قابل للتفكيك"""
    muted = session.query(MutedUsers).all()
    return [(user.user_id, user.full_name, user.username) for user in muted]

def clear_all_muted():
    """مسح قائمة المكتومين بالكامل"""
    session.query(MutedUsers).delete()
    session.commit()

def is_storage_on():
    """التحقق من حالة تشغيل نظام التخزين"""
    return get_config("STORAGE_MASTER") == "on"

def get_storage_chat():
    """جلب آيدي مجموعة التخزين"""
    chat_id = get_config("STORAGE_CHAT_ID")
    return int(chat_id) if chat_id else None

def update_stats(plugin_name):
    """تحديث إحصائيات استخدام الموديولات"""
    res = session.query(Stats).filter(Stats.plugin_name == plugin_name).first()
    if res:
        res.count += 1
    else:
        res = Stats(plugin_name=plugin_name, count=1)
        session.add(res)
    session.commit()

def get_stats(plugin_name):
    """جلب عدد مرات استخدام موديول معين"""
    res = session.query(Stats).filter(Stats.plugin_name == plugin_name).first()
    return res.count if res else 0

# --- [ 2. نظام التحديث التلقائي واللوجر ] ---

LOG_FILE = "abood_logs.txt"

def update_libraries():
    """تحديث المكاتب لضمان عمل السورس بدون نقص"""
    print("🛠️ جاري فحص وتحديث مكاتب عبود المطور...")
    libs = ["telethon==1.31.0", "sqlalchemy", "requests", "pydantic", "aiohttp", "pytz", "bs4"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + libs)
        print("✅ تم تحديث المكاتب بنجاح.")
    except Exception as e:
        print(f"❌ خطأ أثناء تحديث المكاتب: {e}")

def setup_logger():
    """إعداد سجل الأخطاء"""
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ABOOD_SYSTEM")

logger = setup_logger()

# --- [ 3. محرك التيليثون والإعدادات الأساسية ] ---

from telethon import TelegramClient, events, functions, types as tl_types
from telethon.sessions import StringSession

API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992 # أيدي عبود

# المجلدات المطلوبة
PLUGINS_DIR = "Plugins"
ASSISTANT_DIR = os.path.join(PLUGINS_DIR, "assistant")

for folder in [PLUGINS_DIR, ASSISTANT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

running_clients = []

def compatibility_layer(client, module):
    """حقن المتغيرات لضمان عمل الأكواد القديمة"""
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    
    # حقن قاعدة البيانات
    setattr(module, 'database', sys.modules[__name__])

async def load_plugins(client, directory, category):
    """محرك تحميل المجلدات التلقائي"""
    count = 0
    if not os.path.exists(directory): return
    
    if directory not in sys.path:
        sys.path.append(directory)

    for root, _, files in os.walk(directory):
        # منع تحميل مجلد المساعد داخل موديولات الحساب والعكس
        if "assistant" in root and category != "ASSISTANT":
            continue
            
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                path = os.path.join(root, file)
                mod_name = f"mod_{category}_{file[:-3]}_{int(time.time())}"
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, path)
                    module = importlib.util.module_from_spec(spec)
                    compatibility_layer(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في تحميل {file}: {e}")
    
    logger.info(f"✨ {category}: تم تشغيل {count} موديول بنجاح.")

# --- [ 4. أتمتة BotFather (اسم عبود واختصارات البوت) ] ---

async def set_bot_online_features(client, bot_token):
    """تفعيل وضع الأونلاين وتغيير الاسم والأوامر"""
    try:
        # عميل مؤقت لجلب يوزر البوت
        temp = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp.start(bot_token=bot_token)
        me = await temp.get_me()
        bot_user = f"@{me.username}"
        await temp.disconnect()

        target_name = "عبود 🩵"
        target_commands = "start - للبدء\nhack - قسم أمر الهـاك"

        logger.info(f"⚙️ جاري تحديث بيانات {bot_user} في BotFather...")
        
        async with client.conversation("@BotFather") as conv:
            # تحديث الاسم
            await conv.send_message("/setname")
            await asyncio.sleep(1)
            await conv.send_message(bot_user)
            await asyncio.sleep(1)
            await conv.send_message(target_name)
            
            # تحديث الإنلاين (الأونلاين)
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_user)
            await asyncio.sleep(1)
            await conv.send_message("عبود أونلاين 💎")
            
            # تحديث الأوامر
            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_user)
            await asyncio.sleep(1)
            await conv.send_message(target_commands)
            
        logger.info(f"✅ تم ضبط {bot_user} بنجاح.")
    except Exception as e:
        logger.error(f"⚠️ فشل تحديث BotFather: {e}")

# --- [ 5. أوامر التحكم الرئيسية ] ---

def register_core_commands(client, is_bot=False):
    """تسجيل أوامر السورس الأساسية"""
    
    def abood_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = abood_cmd

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def install_handler(event):
        """أمر التنصيب بالرد على الجلسة"""
        if event.sender_id != OWNER_ID: return
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ **يجب الرد على (كود الجلسة) وكتابة:** `.تنصيب <توكن_البوت>`")
        
        session_str = reply.text.strip()
        set_config("MAIN_SESSION", session_str)
        set_config("BOT_TOKEN", token)
        await event.edit("✅ **تم حفظ البيانات! السورس سيعمل الآن.**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_handler(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة تشغيل سورس عبود...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_handler(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("🔄 **جاري التحديث... قد يستغرق الأمر دقيقة.**")
        update_libraries()
        await event.edit("✅ **تم تحديث كافة المكاتب بنجاح!**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def log_handler(event):
        """إرسال ملف السجل"""
        if event.sender_id != OWNER_ID: return
        if not os.path.exists(LOG_FILE):
            return await event.edit("⚠️ **لا يوجد سجل حالياً.**")
        
        await event.edit("⏳ **جاري سحب السجل...**")
        me = await client.get_me()
        user_mention = f"@{me.username}" if me.username else me.first_name
        
        caption = (
            f"📊 **سجل عمليات سورس عبود**\n"
            f"👤 **المطور:** {user_mention}\n"
            f"📅 **الوقت:** `{datetime.now().strftime('%Y-%m-%d %H:%M')}`"
        )
        
        await client.send_file(event.chat_id, LOG_FILE, caption=caption, reply_to=event.id)
        await event.delete()

# --- [ 6. مشغل الخدمات والدالة الرئيسية ] ---

async def start_abood_instance(session_str, token, label):
    """بدء تشغيل الحساب والبوت المساعد"""
    try:
        # تشغيل حساب المستخدم الرئيسي
        main_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await main_client.start()
        register_core_commands(main_client)
        await load_plugins(main_client, PLUGINS_DIR, "MAIN")
        running_clients.append(main_client)

        # تشغيل البوت المساعد
        bot_client = TelegramClient(f"bot_session_{label}", API_ID, API_HASH)
        await bot_client.start(bot_token=token)
        register_core_commands(bot_client, is_bot=True)
        await load_plugins(bot_client, ASSISTANT_DIR, "ASSISTANT")
        running_clients.append(bot_client)

        # تفعيل ميزات BotFather تلقائياً
        asyncio.create_task(set_bot_online_features(main_client, token))
        
        logger.info(f"💎 تم تشغيل كافة الخدمات لـ {label}")
    except Exception as e:
        logger.error(f"❌ كراش في مشغل {label}: {e}")

async def main():
    """نقطة انطلاق السورس"""
    logger.info("--- [ ABOOD SYSTEM STARTING ] ---")
    
    # محاولة جلب البيانات من قاعدة البيانات
    saved_session = get_config("MAIN_SESSION")
    saved_token = get_config("BOT_TOKEN")

    if not saved_session or not saved_token:
        print("👋 مرحباً عبود، يبدو أنك تشغل السورس لأول مرة.")
        print("يرجى إدخال البيانات المطلوبة:")
        new_session = input("👤 أدخل كود الجلسة (String Session): ").strip()
        new_token = input("🤖 أدخل توكن البوت (Bot Token): ").strip()
        
        if new_session and new_token:
            set_config("MAIN_SESSION", new_session)
            set_config("BOT_TOKEN", new_token)
            saved_session, saved_token = new_session, new_token
        else:
            print("❌ يجب إدخال البيانات للتشغيل!")
            return

    # التحديث التلقائي عند الإقلاع
    update_libraries()
    
    # بدء التشغيل
    await start_abood_instance(saved_session, saved_token, "ABOOD_OWNER")

    if running_clients:
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
