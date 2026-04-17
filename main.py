# -*- coding: utf-8 -*-
# سورس عبود المطور - الإصدار العاشر المحسن
# مبرمج ليكون مستقراً بالكامل مع قاعدة بيانات SQLAlchemy

import os
import sys
import asyncio
import importlib.util
import subprocess
import types
import logging
import shutil
import time
from datetime import datetime

# --- [ 1. إعداد قاعدة البيانات المدمجة (SQLAlchemy) ] ---
# قمت بوضع الكود الخاص بك هنا بالكامل مع الترتيب المطلوب

from sqlalchemy import create_engine, Column, String, BigInteger, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# إعداد قاعدة البيانات (تستخدم SQLite افتراضياً)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///phoenix.db")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# --- تعريف الجداول ---

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

# إنشاء الجداول فور تشغيل الملف لضمان عدم وجود أخطاء
Base.metadata.create_all(engine)

# --- دوال الإعدادات (Config) ---

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

# --- دوال الكتم (Mute System) ---

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

# --- أسطر إضافية لدعم موديول التخزين المحسن ---

def is_storage_on():
    """التحقق من حالة تشغيل نظام التخزين"""
    return get_config("STORAGE_MASTER") == "on"

def get_storage_chat():
    """جلب آيدي مجموعة التخزين"""
    chat_id = get_config("STORAGE_CHAT_ID")
    return int(chat_id) if chat_id else None

# --- الوظيفة المطلوبة لحل خطأ الكونسول (Update Stats) ---

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

# --- [ 2. نظام تحديث المكاتب واللوجر ] ---

LOG_FILE = "abood_source_log.txt"

def update_reqs():
    """تحديث مكاتب السورس آلياً"""
    print("🛠️ جاري فحص وتحديث مكاتب عبود المطور...")
    libs = ["telethon==1.31.0", "sqlalchemy", "requests", "pydantic", "aiohttp", "pytz", "bs4"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + libs)
        print("✅ تم تحديث المكاتب بنجاح.")
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي: {e}")

def init_logger():
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
    )
    return logging.getLogger("ABOOD_SYSTEM")

logger = init_logger()

# --- [ 3. إعدادات التيليثون والمحرك الأساسي ] ---

from telethon import TelegramClient, events, functions, types as tl_types
from telethon.sessions import StringSession

API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992 

PLUGINS_DIR = "Plugins"
ASSISTANT_DIR = os.path.join(PLUGINS_DIR, "assistant")

# إنشاء المجلدات إذا لم تكن موجودة
for d in [PLUGINS_DIR, ASSISTANT_DIR]:
    if not os.path.exists(d): os.makedirs(d)

clients = []

def inject_deps(client, module):
    """حقن التبعيات لضمان عمل الموديولات القديمة"""
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    # ربط قاعدة البيانات بالموديولات
    setattr(module, 'database', sys.modules[__name__])

async def load_all_plugins(client, folder, label):
    """محرك تحميل الإضافات التلقائي"""
    count = 0
    if not os.path.exists(folder): return
    if folder not in sys.path: sys.path.append(folder)

    for root, _, files in os.walk(folder):
        # فصل موديولات البوت عن الحساب
        if "assistant" in root and label != "ASSISTANT": continue
        
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                path = os.path.join(root, file)
                name = f"mod_{label}_{file[:-3]}_{int(time.time())}"
                try:
                    spec = importlib.util.spec_from_file_location(name, path)
                    module = importlib.util.module_from_spec(spec)
                    inject_deps(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'): module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ فشل تحميل {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# --- [ 4. أتمتة BotFather (الأونلاين والاختصارات) ] ---

async def bot_father_automation(client, bot_token):
    """ضبط وضع الأونلاين والأوامر مع انتظار 2 ثانية"""
    try:
        # جلب يوزر البوت
        temp = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp.start(bot_token=bot_token)
        me = await temp.get_me()
        bot_user = f"@{me.username}"
        await temp.disconnect()

        logger.info(f"⚙️ جاري ضبط ميزات {bot_user} في BotFather...")
        
        async with client.conversation("@BotFather") as conv:
            # 1. تفعيل وضع الأونلاين (Inline Mode) باسم عبود
            await conv.send_message("/setinline")
            await asyncio.sleep(2)
            await conv.send_message(bot_user)
            await asyncio.sleep(2)
            await conv.send_message("عبود 🩵") # اسم زر الأونلاين
            await asyncio.sleep(2)
            
            # 2. ضبط قائمة الأوامر
            await conv.send_message("/setcommands")
            await asyncio.sleep(2)
            await conv.send_message(bot_user)
            await asyncio.sleep(2)
            # الاختصارات المطلوبة
            commands = "start - للبدء\nhack - قسم أمر الهـاك"
            await conv.send_message(commands)
            await asyncio.sleep(2)
            
        logger.info(f"✅ تم تفعيل ميزات الأونلاين لـ {bot_user}")
    except Exception as e:
        logger.error(f"⚠️ فشل ضبط BotFather: {e}")

# --- [ 5. الأوامر الأساسية ] ---

def setup_core_cmds(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def install_api(event):
        if event.sender_id != OWNER_ID: return
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ **رد على الجلسة واكتب:** `.تنصيب <توكن>`")
        
        set_config("SESSION", reply.text.strip())
        set_config("TOKEN", token)
        await event.edit("✅ **تم حفظ البيانات! السورس سيعمل الآن.**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_api(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة التشغيل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_api(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("🔄 **جاري التحديث...**")
        update_reqs()
        await event.edit("✅ **تم تحديث المكاتب بنجاح!**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def send_log_api(event):
        if event.sender_id != OWNER_ID: return
        if not os.path.exists(LOG_FILE):
            return await event.edit("⚠️ **لا يوجد سجل.**")
        
        await event.edit("⏳ **جاري جلب السجل...**")
        me = await client.get_me()
        user = f"@{me.username}" if me.username else me.first_name
        
        cap = (
            f"📊 **سجل سورس عبود**\n"
            f"👤 **المطور:** {user}\n"
            f"📅 **الوقت:** `{datetime.now().strftime('%H:%M:%S')}`"
        )
        await client.send_file(event.chat_id, LOG_FILE, caption=cap, reply_to=event.id)
        await event.delete()

# --- [ 6. المشغل والدالة الرئيسية ] ---

async def run_abood_instance(s_str, t_str):
    try:
        # تشغيل الحساب
        main_cl = TelegramClient(StringSession(s_str), API_ID, API_HASH)
        await main_cl.start()
        setup_core_cmds(main_cl)
        await load_all_plugins(main_cl, PLUGINS_DIR, "MAIN")
        clients.append(main_cl)

        # تشغيل المساعد
        bot_cl = TelegramClient("assistant_session", API_ID, API_HASH)
        await bot_cl.start(bot_token=t_str)
        setup_core_cmds(bot_cl, is_bot=True)
        await load_all_plugins(bot_cl, ASSISTANT_DIR, "ASSISTANT")
        clients.append(bot_cl)

        # تفعيل الأتمتة
        asyncio.create_task(bot_father_automation(main_cl, t_str))
        
        logger.info("💎 النظام يعمل الآن بكافة طاقته.")
    except Exception as e:
        logger.error(f"❌ خطأ فادح في التشغيل: {e}")

async def main():
    logger.info("--- [ ABOOD START ] ---")
    
    s = get_config("SESSION")
    t = get_config("TOKEN")

    if not s or not t:
        print("👤 مرحباً عبود، السورس يحتاج للبيانات لأول مرة:")
        s_in = input("أدخل الجلسة (String Session): ").strip()
        t_in = input("أدخل توكن البوت (Bot Token): ").strip()
        if s_in and t_in:
            set_config("SESSION", s_in)
            set_config("TOKEN", t_in)
            s, t = s_in, t_in
        else:
            print("❌ البيانات مطلوبة!")
            return

    # التحديث عند الإقلاع
    update_reqs()
    
    await run_abood_instance(s, t)
    
    if clients:
        await asyncio.gather(*[c.run_until_disconnected() for c in clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
