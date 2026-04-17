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
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.errors import AccessTokenInvalidError, ApiIdInvalidError

# -------------------------------------------------------------------
# 1. التثبيت القسري للإصدار الصحيح من Telethon
# -------------------------------------------------------------------
def force_install_requirements():
    try:
        print("🛠️ جاري تثبيت Telethon 1.31.0...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--user",
            "--upgrade", "--force-reinstall",
            "telethon==1.31.0", "pytz", "pydantic", "aiohttp",
            "requests", "bs4", "aiosqlite"
        ])
        print("✅ تم التثبيت بنجاح.")
    except Exception as e:
        print(f"⚠️ فشل التثبيت: {e}")

force_install_requirements()

import telethon
print(f"✅ Telethon version: {telethon.__version__}")

try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except (ImportError, SyntaxError):
    HAS_JOIN_SUPPORT = False

# -------------------------------------------------------------------
# 2. إعداد السجل
# -------------------------------------------------------------------
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def initialize_logger():
    if os.path.exists(LOG_FILE_PATH):
        try:
            os.remove(LOG_FILE_PATH)
        except:
            pass
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"سورس عبود | السجل: {time.ctime()}\n")
        f.write("-" * 50 + "\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("ABOOD")

logger = initialize_logger()

# -------------------------------------------------------------------
# 3. قاعدة البيانات
# -------------------------------------------------------------------
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
DB_PATH = "abood.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY, session TEXT, token TEXT)''')
    conn.commit()
    conn.close()

init_db()

BASE_DIR = os.getcwd()
for folder in ["Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# -------------------------------------------------------------------
# 4. التوافق مع الموديولات
# -------------------------------------------------------------------
def apply_compatibility(client, module):
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)

    if not hasattr(module, 'database'):
        db_mock = types.ModuleType("database")
        db_mock.update_stats = lambda *args, **kwargs: None
        db_mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db_mock)

    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)

# -------------------------------------------------------------------
# 5. تحميل الموديولات
# -------------------------------------------------------------------
async def start_plugins_engine(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path):
        return
    if full_path not in sys.path:
        sys.path.append(full_path)

    if "l313l" not in sys.modules:
        mock_l313l = types.ModuleType("l313l")
        mock_l313l.l313l = client
        sys.modules["l313l"] = mock_l313l

    for root, _, files in os.walk(full_path):
        if "assistant" in root and label != "مساعد":
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                try:
                    spec = importlib.util.spec_from_file_location(file[:-3], os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    apply_compatibility(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"خطأ في {file}: {e}")
    logger.info(f"{label}: تم تشغيل {count} موديول.")

# -------------------------------------------------------------------
# 6. تفعيل وضع الأونلاين
# -------------------------------------------------------------------
async def mybot_online_setup(user_client, bot_token):
    try:
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        bot_me = await temp_bot.get_me()
        bot_username = f"@{bot_me.username}"
        await temp_bot.disconnect()

        commands_text = "start - للبدء\nhack - الهاك\nhelp - المساعدة"
        
        async with user_client.conversation("@BotFather") as conv:
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message("عبود 🩵")
            
            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(commands_text)
        
        logger.info(f"تم تفعيل البوت {bot_username}")
    except Exception as e:
        logger.error(f"فشل تفعيل البوت: {e}")

# -------------------------------------------------------------------
# 7. الأوامر الرئيسية
# -------------------------------------------------------------------
def setup_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def install_cmd(event):
        if event.sender_id != OWNER_ID:
            return
        
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ الرد على كود الجلسة بـ: .تنصيب <التوكن>")
        
        session_data = reply.text.strip()
        await event.edit("⏳ جاري الحفظ...")
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO sessions (id, session, token) VALUES (1, ?, ?)",
                  (session_data, token))
        conn.commit()
        conn.close()
        
        await event.edit("✅ تم الحفظ! إعادة التشغيل...")
        await asyncio.sleep(1)
        sys.exit(0)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_cmd(event):
        if event.sender_id != OWNER_ID:
            return
        await event.edit("🔄 جاري التحديث...")
        force_install_requirements()
        await event.edit("✅ تم التحديث! استخدم .اعادة تشغيل")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_cmd(event):
        if event.sender_id != OWNER_ID:
            return
        await event.edit("♻️ جاري إعادة التشغيل...")
        await asyncio.sleep(1)
        sys.exit(0)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def log_cmd(event):
        if not os.path.exists(LOG_FILE_PATH):
            return await event.edit("⚠️ لا يوجد سجل")
        
        temp = f"log_{int(time.time())}.txt"
        shutil.copy2(LOG_FILE_PATH, temp)
        await client.send_file(event.chat_id, temp, caption="📊 سجل الهوست")
        os.remove(temp)
        if not is_bot:
            await event.delete()

    @client.on(events.Raw)
    async def auto_approve(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except:
                pass

# -------------------------------------------------------------------
# 8. تشغيل الوحدات
# -------------------------------------------------------------------
async def start_instance(session_str, token, name):
    user_client = None
    bot_client = None
    
    if session_str and session_str.strip():
        try:
            logger.info(f"بدء تشغيل الحساب: {name}")
            user_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await user_client.start()
            setup_handlers(user_client)
            await start_plugins_engine(user_client, "Plugins", f"حساب_{name}")
            running_clients.append(user_client)
            logger.info(f"✅ تم تشغيل الحساب")
        except Exception as e:
            logger.error(f"فشل الحساب {name}: {e}")
    
    if token and token.strip():
        try:
            logger.info(f"بدء تشغيل البوت: {name}")
            bot_client = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot_client.start(bot_token=token)
            setup_handlers(bot_client, is_bot=True)
            await start_plugins_engine(bot_client, "Plugins/assistant", "مساعد")
            running_clients.append(bot_client)
            logger.info(f"✅ تم تشغيل البوت")
            
            if user_client:
                asyncio.create_task(mybot_online_setup(user_client, token))
        except Exception as e:
            logger.error(f"فشل البوت {name}: {e}")

# -------------------------------------------------------------------
# 9. التشغيل الرئيسي
# -------------------------------------------------------------------
async def main():
    logger.info("--- سورس عبود المطور v8.0 ---")
    
    # قراءة من قاعدة البيانات
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT session, token FROM sessions WHERE id = 1")
    row = c.fetchone()
    conn.close()
    
    session_str = row[0] if row and row[0] else ""
    token = row[1] if row and row[1] else ""
    
    # إذا كانت فارغة، جرب متغيرات البيئة
    if not session_str and not token:
        session_str = os.environ.get("SESSION_STRING", "")
        token = os.environ.get("BOT_TOKEN", "")
        if session_str or token:
            logger.info("تم العثور على بيانات في متغيرات البيئة. جاري الحفظ...")
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO sessions (id, session, token) VALUES (1, ?, ?)",
                      (session_str, token))
            conn.commit()
            conn.close()
    
    if session_str or token:
        logger.info("✅ توجد بيانات. جاري التشغيل...")
        await start_instance(session_str, token, "Main")
    else:
        logger.warning("=" * 50)
        logger.warning("⚠️ لا توجد جلسة ولا توكن!")
        logger.warning("يمكنك إضافتهما عبر:")
        logger.warning("1. متغيرات البيئة: SESSION_STRING و BOT_TOKEN")
        logger.warning("2. أو بعد تشغيل حسابك الأول، استخدم أمر .تنصيب")
        logger.warning("=" * 50)
        logger.info("⏳ انتظار...")
        
        # انتظر إلى أجل غير مسمى
        while True:
            await asyncio.sleep(60)
    
    if running_clients:
        logger.info(f"💎 يعمل {len(running_clients)} وحدة")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

# -------------------------------------------------------------------
# 10. البدء
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("تم الإيقاف")
    except Exception as e:
        logger.critical(f"خطأ: {e}")
        sys.exit(1)
