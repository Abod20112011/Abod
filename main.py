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

# --- [ 1. نظام تحديث البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    """تحديث المكتبات لضمان عمل كافة الأوامر بدون نقص"""
    try:
        print("🛠️ جاري فحص وتحديث مكاتب سورس عبود المطور...")
        # المكتبات الأساسية المطلوبة للتشغيل
        required_libs = [
            "telethon==1.31.0", "pytz", "pydantic", "aiohttp", 
            "requests", "bs4", "aiosqlite"
        ]
        # تنفيذ التحديث عبر pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
        print("✅ تم تحديث المكتبات بنجاح.")
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي للمكتبات، قد يكون بسبب الهوست: {e}")

# استدعاء التحديث فور بدء التشغيل
setup_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة ميزات طلبات الانضمام الجديدة (لحماية السورس من الكراش في النسخ القديمة)
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except (ImportError, SyntaxError):
    HAS_JOIN_SUPPORT = False
    print("⚠️ تحذير: نسخة Telethon لا تدعم ميزات طلبات الانضمام التلقائي.")

# --- [ 2. إعدادات سجل العمليات (LOG) ] ---
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def initialize_logger():
    """تهيئة نظام تسجيل الأخطاء لضمان عمل أمر .لوك"""
    if os.path.exists(LOG_FILE_PATH):
        try: os.remove(LOG_FILE_PATH)
        except: pass
    
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"📊 سورس عبود المطور | سجل الهوست: {time.ctime()}\n")
        f.write("--------------------------------------------------\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ABOOD_SYSTEM")

logger = initialize_logger()

# --- [ 3. إدارة قاعدة البيانات والبيانات الثابتة ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992  # أيدي المطور عبود
DB_PATH = "abood_database.db"

def init_db():
    """حل مشكلة (no such table) عبر تهيئة قاعدة البيانات قبل التشغيل"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # إنشاء جدول الجلسات إذا لم يكن موجوداً
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      session_string TEXT UNIQUE, 
                      bot_token TEXT)''')
    conn.commit()
    conn.close()
    logger.info("✅ تم تهيئة قاعدة البيانات وجداول الجلسات بنجاح.")

# تنفيذ التهيئة فوراً
init_db()

BASE_DIR = os.getcwd()
# التأكد من وجود المجلدات المطلوبة
for folder in ["Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# --- [ 4. موديول التوافق البرمجي ] ---
def apply_compatibility(client, module):
    """ربط الإضافات القديمة بالعميل الجديد لضمان عمل الأوامر"""
    # حذف JoKeRUB وحقن المسميات الأخرى
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    
    # محاكاة كلاس قاعدة البيانات لبعض السورسات القديمة
    if not hasattr(module, 'database'):
        db_mock = types.ModuleType("database")
        db_mock.update_stats = lambda *args, **kwargs: None
        db_mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db_mock)

# --- [ 5. محرك تحميل الإضافات ومساعد التشغيل ] ---
async def start_plugins_engine(client, folder_name, label):
    """تحميل الموديولات برمجياً من المجلدات المحددة"""
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

    # تعريف l313l في النظام لكسر أخطاء الاستيراد (ImportError)
    if "l313l" not in sys.modules:
        mock_l = types.ModuleType("l313l")
        mock_l.l313l = client
        sys.modules["l313l"] = mock_l

    for root, _, files in os.walk(full_path):
        # منع تحميل إضافات المساعد داخل الحساب الرئيسي والعكس
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
                    
                    if hasattr(module, 'setup'): 
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في تحميل الموديول {file}: {e}")
    
    logger.info(f"✨ {label}: تم تشغيل {count} موديول بنجاح.")

# --- [ 6. نظام الأونلاين (BotFather Automation) ] ---
async def abood_online_setup(client, bot_token):
    """تفعيل ميزات الأونلاين تلقائياً باسم عبود 🩵"""
    try:
        # عميل مؤقت لجلب يوزر البوت
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        bot_info = await temp_bot.get_me()
        bot_user = f"@{bot_info.username}"
        await temp_bot.disconnect()

        name_to_set = "عبود 🩵"
        commands_to_set = "start - للبدء 💎\nhack - قسم أمر الهـاك ⚡\nhelp - قائمة المساعدة 📚"
        
        logger.info(f"⚙️ جاري تحديث إعدادات {bot_user} في BotFather...")
        
        async with client.conversation("@BotFather") as conv:
            # تفعيل وضع الإنلاين (Inline Mode)
            await conv.send_message("/setinline")
            await asyncio.sleep(1.5)
            await conv.send_message(bot_user)
            await asyncio.sleep(1.5)
            await conv.send_message(name_to_set)
            
            # ضبط قائمة الأوامر التلقائية
            await conv.send_message("/setcommands")
            await asyncio.sleep(1.5)
            await conv.send_message(bot_user)
            await asyncio.sleep(1.5)
            await conv.send_message(commands_to_set)
        
        logger.info(f"✅ تم تفعيل وضع الأونلاين بنجاح لـ {bot_user}")
    except Exception as e:
        logger.error(f"⚠️ فشل أتمتة BotFather: {e}")

# --- [ 7. معالجة الأوامر البرمجية (Core Handlers) ] ---
def setup_handlers(client, is_bot=False):
    """إعداد الأوامر الأساسية للتحكم في الهوست"""
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # [ أمر التنصيب الجديد بالرد ]
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def abood_install(event):
        if event.sender_id != OWNER_ID: return
        
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        
        if not reply or not reply.text:
            return await event.edit("⚠️ **يجب الرد على (كود الجلسة) بالأمر:** `.تنصيب <توكن_البوت>`")
        
        session_str = reply.text.strip()
        await event.edit("⏳ **جاري حفظ البيانات وتجهيز الهوست...**")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO sessions (session_string, bot_token) VALUES (?, ?)", (session_str, token))
            conn.commit()
            conn.close()
            
            await event.edit("✅ **تم التنصيب بنجاح! سيتم تشغيل السورس الآن.**")
            await start_instance(session_str, token, "New_User")
        except Exception as e:
            await event.edit(f"❌ **فشل التنصيب:**\n`{str(e)}`")

    # [ أوامر التحكم بالسجل والمكاتب ]
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_libs_cmd(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("🔄 **جاري تحديث كافة مكاتب الهوست...**")
        setup_environment()
        await event.edit("✅ **تم التحديث! يرجى إرسال `.اعادة تشغيل` لضمان العمل.**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_cmd(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة تشغيل سورس عبود بالكامل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # [ معالجة طلبات الانضمام ]
    @client.on(events.Raw)
    async def join_auto_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                chat_p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=chat_p, user_id=update.user_id, approve=True))
            except: pass

# --- [ 8. مشغل الوحدات (Boot Engine) ] ---
async def start_instance(session, token, name):
    """بدء تشغيل الحساب والبوت المساعد كـ Instance واحد"""
    try:
        main_user = None
        if session:
            main_user = TelegramClient(StringSession(session), API_ID, API_HASH)
            await main_user.start()
            setup_handlers(main_user)
            # تحميل مكاتب Plugins
            await start_plugins_engine(main_user, "Plugins", f"حساب_{name}")
            running_clients.append(main_user)

        if token:
            assistant_bot = TelegramClient(f"bot_session_{name}", API_ID, API_HASH)
            await assistant_bot.start(bot_token=token)
            setup_handlers(assistant_bot, is_bot=True)
            # تحميل مكاتب Plugins/assistant
            await start_plugins_engine(assistant_bot, "Plugins/assistant", "المساعد")
            running_clients.append(assistant_bot)
            
            # تفعيل الأونلاين عبر الحساب الرئيسي
            if main_user:
                asyncio.create_task(abood_online_setup(main_user, token))

    except Exception as e:
        logger.error(f"❌ فشل تشغيل الوحدة {name}: {e}")

async def main():
    """الدالة الأساسية لبدء السورس"""
    logger.info("--- [ ABOOD SYSTEM v7.5 STARTING ] ---")
    
    # القراءة من قاعدة البيانات
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # التأكد مرة أخرى من وجود الجدول لتجنب خطأ الصور
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
    if not cursor.fetchone():
        init_db()
        
    cursor.execute("SELECT session_string, bot_token FROM sessions")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            await start_instance(row[0], row[1], "Main")
    else:
        logger.warning("⚠️ لا توجد جلسات في قاعدة البيانات. استخدم أمر .تنصيب")

    if running_clients:
        logger.info(f"💎 النظام يعمل الآن بـ {len(running_clients)} عملاء.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
