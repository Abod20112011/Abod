import os
import sys
import asyncio
import importlib.util
import subprocess
import types
import logging
import shutil
import time
import sqlite3

# استيراد مكتبات قاعدة البيانات المطلوبة
try:
    from sqlalchemy import create_engine, Column, String, BigInteger, Integer
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
except ImportError:
    print("📦 جاري تثبيت المكتبات الأساسية لأول مرة...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy", "telethon==1.31.0", "aiosqlite"])
    from sqlalchemy import create_engine, Column, String, BigInteger, Integer
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

# --- [ 1. إعداد قاعدة البيانات المدمجة (SQLAlchemy) ] ---

DB_URL = "sqlite:///abood_system.db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db_session = Session()
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

# إنشاء الجداول فوراً لضمان عدم حدوث خطأ "no such table"
Base.metadata.create_all(engine)

# --- [ 2. دوال قاعدة البيانات (حسب طلبك - دون حذف) ] ---

def get_config(variable_name):
    res = db_session.query(Config).filter(Config.variable == variable_name).first()
    return res.value if res else None

def set_config(variable_name, value):
    res = db_session.query(Config).filter(Config.variable == variable_name).first()
    if res:
        res.value = str(value)
    else:
        res = Config(variable=variable_name, value=str(value))
        db_session.add(res)
    db_session.commit()

def del_config(variable_name):
    res = db_session.query(Config).filter(Config.variable == variable_name).first()
    if res:
        db_session.delete(res)
        db_session.commit()

def is_muted(user_id):
    res = db_session.query(MutedUsers).filter(MutedUsers.user_id == user_id).first()
    return True if res else False

def add_muted(user_id, full_name=None, username=None):
    if not is_muted(user_id):
        new_mute = MutedUsers(user_id=user_id, full_name=full_name, username=username)
        db_session.add(new_mute)
        db_session.commit()

def remove_muted(user_id):
    res = db_session.query(MutedUsers).filter(MutedUsers.user_id == user_id).first()
    if res:
        db_session.delete(res)
        db_session.commit()

def get_all_muted():
    muted = db_session.query(MutedUsers).all()
    return [(user.user_id, user.full_name, user.username) for user in muted]

def update_stats(plugin_name):
    res = db_session.query(Stats).filter(Stats.plugin_name == plugin_name).first()
    if res:
        res.count += 1
    else:
        res = Stats(plugin_name=plugin_name, count=1)
        db_session.add(res)
    db_session.commit()

# --- [ 3. نظام تحديث البيئة واللوج ] ---

LOG_FILE = "سجل_الأخطاء.txt"

def setup_environment():
    """تحديث كافة مكاتب السورس"""
    try:
        print("🛠️ جاري فحص وتحديث مكاتب سورس عبود المطور...")
        required = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "requests", "bs4"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required)
    except Exception as e:
        print(f"⚠️ فشل تحديث المكاتب: {e}")

def init_logger():
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
    )
    return logging.getLogger("ABOOD_DEV")

logger = init_logger()

# --- [ 4. إعدادات التيليثون والمحرك ] ---

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992 

BASE_DIR = os.getcwd()
running_clients = []

def apply_compatibility(client, module):
    """نظام التوافق البرمجي وحقن المتغيرات"""
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    
    # حقن قاعدة البيانات داخل الموديولات
    setattr(module, 'database', sys.modules[__name__])
    
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)

async def start_plugins_engine(client, folder_name, label):
    """محرك تحميل الإضافات ومجلد المساعد"""
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)
        return

    if full_path not in sys.path: sys.path.append(full_path)

    # تعريف موديول l313l الوهمي
    if "l313l" not in sys.modules:
        mock_l = types.ModuleType("l313l")
        mock_l.l313l = client
        sys.modules["l313l"] = mock_l

    for root, _, files in os.walk(full_path):
        # فصل موديولات المساعد عن الحساب الرئيسي
        if "assistant" in root and label != "المساعد":
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                mod_name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    apply_compatibility(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'): module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# --- [ 5. نظام الأونلاين وأوامر BotFather ] ---

async def abood_online_automation(client, bot_token):
    """تفعيل وضع الأونلاين باسم عبود 🩵"""
    try:
        # عميل مؤقت لجلب يوزر البوت
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        bot_me = await temp_bot.get_me()
        bot_username = f"@{bot_me.username}"
        await temp_bot.disconnect()

        name = "عبود 🩵"
        commands = "start - للبدء\nhack - قسم أمر الهـاك"
        
        logger.info(f"⚙️ جاري ضبط {bot_username} في BotFather...")
        async with client.conversation("@BotFather") as conv:
            # ضبط الاسم والإنلاين
            await conv.send_message("/setinline")
            await asyncio.sleep(1.5)
            await conv.send_message(bot_username)
            await asyncio.sleep(1.5)
            await conv.send_message(name)
            
            # ضبط الأوامر
            await conv.send_message("/setcommands")
            await asyncio.sleep(1.5)
            await conv.send_message(bot_username)
            await asyncio.sleep(1.5)
            await conv.send_message(commands)
        logger.info(f"✅ تم تفعيل الأونلاين بنجاح لـ {bot_username}")
    except Exception as e:
        logger.error(f"⚠️ فشل أتمتة البوت: {e}")

# --- [ 6. معالجة الأوامر الرئيسية ] ---

def setup_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def abood_install(event):
        """أمر التنصيب بالرد على الجلسة"""
        if event.sender_id != OWNER_ID: return
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ **رد على كود الجلسة واكتب .تنصيب مع التوكن**")
        
        session_str = reply.text.strip()
        set_config("STRING_SESSION", session_str)
        set_config("BOT_TOKEN", token)
        await event.edit("✅ **تم حفظ البيانات في قاعدة بيانات عبود! جاري إعادة التشغيل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def abood_update(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("🔄 **جاري تحديث كافة المكاتب...**")
        setup_environment()
        await event.edit("✅ **تم التحديث بنجاح!**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def abood_reboot(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة التشغيل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [ 7. مشغل الوحدات والدالة الرئيسية ] ---

async def start_instance(s, t, name):
    try:
        user_cl = None
        if s:
            user_cl = TelegramClient(StringSession(s), API_ID, API_HASH)
            await user_cl.start()
            setup_handlers(user_cl)
            await start_plugins_engine(user_cl, "Plugins", f"حساب_{name}")
            running_clients.append(user_cl)

        if t:
            bot_cl = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot_cl.start(bot_token=t)
            setup_handlers(bot_cl, is_bot=True)
            await start_plugins_engine(bot_cl, "Plugins/assistant", "المساعد")
            running_clients.append(bot_cl)
            
            if user_cl:
                asyncio.create_task(abood_online_automation(user_cl, t))
    except Exception as e:
        logger.error(f"❌ فشل في {name}: {e}")

async def main():
    logger.info("--- [ ABOOD SYSTEM v8.0 START ] ---")
    
    # جلب البيانات من قاعدة البيانات
    s_db = get_config("STRING_SESSION")
    t_db = get_config("BOT_TOKEN")

    if not s_db or not t_db:
        print("👤 مرحباً عبود، السورس يحتاج للبيانات لأول مرة:")
        s_input = input("أدخل الجلسة (String Session): ").strip()
        t_input = input("أدخل توكن البوت (Bot Token): ").strip()
        set_config("STRING_SESSION", s_input)
        set_config("BOT_TOKEN", t_input)
        s_db, t_db = s_input, t_input

    await start_instance(s_db, t_db, "MainInstance")

    if running_clients:
        logger.info(f"💎 النظام يعمل بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    setup_environment()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
