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
# 1. التثبيت القسري للإصدار الصحيح من Telethon والمكتبات
# -------------------------------------------------------------------
def force_install_requirements():
    try:
        print("🛠️ جاري تثبيت Telethon 1.31.0 والمكتبات الضرورية...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--user",
            "--upgrade", "--force-reinstall",
            "telethon==1.31.0", "pytz", "pydantic", "aiohttp",
            "requests", "bs4", "aiosqlite"
        ])
        print("✅ تم تثبيت جميع المكتبات بنجاح.")
    except Exception as e:
        print(f"⚠️ تحذير: فشل التثبيت القسري: {e}")

force_install_requirements()

import telethon
print(f"✅ Telethon version: {telethon.__version__}")

try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except (ImportError, SyntaxError):
    HAS_JOIN_SUPPORT = False
    print("⚠️ تحذير: نسخة Telethon لا تدعم طلبات الانضمام الجديدة.")

# -------------------------------------------------------------------
# 2. إعداد سجل الأخطاء (LOG)
# -------------------------------------------------------------------
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def initialize_logger():
    if os.path.exists(LOG_FILE_PATH):
        try:
            os.remove(LOG_FILE_PATH)
        except:
            pass
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"📊 سورس عبود المطور | سجل الهوست: {time.ctime()}\n")
        f.write("-" * 50 + "\n")

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

# -------------------------------------------------------------------
# 3. البيانات الثابتة وقاعدة البيانات
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
    # للتأكد من وجود صف افتراضي فارغ (اختياري)
    c.execute("INSERT OR IGNORE INTO sessions (id, session, token) VALUES (1, '', '')")
    conn.commit()
    conn.close()

init_db()

BASE_DIR = os.getcwd()
for folder in ["Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# -------------------------------------------------------------------
# 4. دالة التوافق مع الموديولات (بدون JoKeRUB)
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
# 5. محرك تحميل البلغ إنز (Plugins)
# -------------------------------------------------------------------
async def start_plugins_engine(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path):
        logger.warning(f"⚠️ المجلد {folder_name} غير موجود.")
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
                    logger.error(f"❌ خطأ في {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# -------------------------------------------------------------------
# 6. وظائف وضع الأونلاين (BotFather)
# -------------------------------------------------------------------
async def mybot_online_setup(user_client, bot_token):
    try:
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        bot_me = await temp_bot.get_me()
        bot_username = f"@{bot_me.username}"
        await temp_bot.disconnect()

        joker_name = "عبود 🩵"
        commands_text = "start - للبدء 💎\nhack - قسم أمر الهـاك ⚡\nhelp - قائمة المساعدة 📚"

        logger.info(f"⚙️ جاري تحديث إعدادات البوت {bot_username} عبر @BotFather")
        async with user_client.conversation("@BotFather") as conv:
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(joker_name)

            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(commands_text)

        logger.info(f"✅ تم تفعيل وضع الأونلاين للبوت {bot_username}")
    except Exception as e:
        logger.error(f"⚠️ فشل أتمتة BotFather: {e}")

# -------------------------------------------------------------------
# 7. معالجة الأوامر الأساسية
# -------------------------------------------------------------------
def setup_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))

    client.ar_cmd = ar_cmd

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def abood_install(event):
        if event.sender_id != OWNER_ID:
            return
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ **يجب الرد على كود الجلسة بالأمر:** `.تنصيب <التوكن>`")

        session_data = reply.text.strip()
        await event.edit("⏳ **جاري حفظ البيانات في قاعدة بيانات عبود...**")

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO sessions (id, session, token) VALUES (1, ?, ?)",
                      (session_data, token))
            conn.commit()
            conn.close()
            await event.edit("✅ **تم الحفظ بنجاح! سيتم تشغيل البوت الآن.**")
            asyncio.create_task(restart_main_instance(session_data, token))
        except Exception as e:
            await event.edit(f"❌ **فشل التنصيب:** {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def abood_update(event):
        if event.sender_id != OWNER_ID:
            return
        await event.edit("🔄 **جاري تحديث جميع مكاتب الهوست...**")
        force_install_requirements()
        await event.edit("✅ **تم التحديث بنجاح! أرسل `.اعادة تشغيل` الآن.**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def abood_reboot(event):
        if event.sender_id != OWNER_ID:
            return
        await event.edit("♻️ **جاري إعادة تشغيل سورس عبود المطور...**")
        await asyncio.sleep(1)
        sys.exit(0)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def abood_log_lock(event):
        try:
            if not is_bot:
                await event.edit("⏳ جاري سحب سجل الهوست...")
        except:
            pass

        if not os.path.exists(LOG_FILE_PATH):
            err = "⚠️ السجل غير موجود حالياً."
            if is_bot:
                return await event.respond(err)
            else:
                return await event.edit(err)

        temp_name = f"log_fix_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE_PATH, temp_name)
            await client.send_file(
                event.chat_id,
                temp_name,
                caption=f"📊 **سجل عمليات السورس (الهوست)**\n👤 **المطور:** عبود",
                reply_to=event.id
            )
            if not is_bot:
                await event.delete()
        except Exception as e:
            if is_bot:
                await event.respond(f"❌ خطأ: {e}")
            else:
                await event.edit(f"❌ خطأ: {e}")
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    @client.on(events.Raw)
    async def join_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except:
                pass

    @client.on(events.NewMessage(incoming=True))
    async def zip_forwarder(event):
        if event.file and event.file.ext == ".zip":
            try:
                ZIP_BACKUP = -1001234567890
                await client.send_file(ZIP_BACKUP, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except:
                pass

# -------------------------------------------------------------------
# 8. تشغيل وحدة واحدة (حساب + بوت)
# -------------------------------------------------------------------
async def start_instance(session_str, token, name):
    user_client = None
    bot_client = None
    try:
        if session_str and session_str.strip():
            logger.info(f"🚀 بدء تشغيل الحساب لـ {name}...")
            user_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await user_client.start()
            setup_handlers(user_client)
            await start_plugins_engine(user_client, "Plugins", f"حساب_{name}")
            running_clients.append(user_client)
            logger.info(f"✅ تم تشغيل الحساب لـ {name}")
        else:
            logger.warning(f"⚠️ لا توجد جلسة لحساب {name}، لن يتم تشغيل حساب.")

        if token and token.strip():
            logger.info(f"🚀 بدء تشغيل البوت لـ {name}...")
            bot_client = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot_client.start(bot_token=token)
            setup_handlers(bot_client, is_bot=True)
            await start_plugins_engine(bot_client, "Plugins/assistant", "مساعد")
            running_clients.append(bot_client)
            logger.info(f"✅ تم تشغيل البوت لـ {name}")

            if user_client:
                asyncio.create_task(mybot_online_setup(user_client, token))
        else:
            logger.warning(f"⚠️ لا يوجد توكن للبوت {name}، لن يتم تشغيل بوت.")

    except (AccessTokenInvalidError, ApiIdInvalidError) as e:
        logger.error(f"❌ خطأ في التوكن أو الجلسة للوحدة {name}: {e}")
    except Exception as e:
        logger.error(f"❌ فشل تشغيل الوحدة {name}: {e}")

async def restart_main_instance(session_str, token):
    for cl in running_clients:
        await cl.disconnect()
    running_clients.clear()
    await start_instance(session_str, token, "MainUser")

# -------------------------------------------------------------------
# 9. الدالة الرئيسية مع معالجة الصبر
# -------------------------------------------------------------------
async def main():
    logger.info("--- [ ABOOD HOSTING v7.6 ] ---")
    logger.info("⏳ جاري قراءة البيانات من قاعدة البيانات...")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT session, token FROM sessions WHERE id = 1")
    row = c.fetchone()
    conn.close()

    session_str = row[0] if row and row[0] else ""
    token = row[1] if row and row[1] else ""

    if session_str or token:
        logger.info("✅ تم العثور على بيانات. جاري تشغيل الوحدات...")
        await start_instance(session_str, token, "MainUser")
    else:
        logger.warning("⚠️ قاعدة البيانات فارغة تمامًا (لا جلسة ولا توكن).")
        logger.warning("📌 يرجى استخدام أمر `.تنصيب <التوكن>` بالرد على كود الجلسة لحفظ البيانات.")
        logger.warning("⏳ السورس سيبقى قيد التشغيل حتى يتم التنصيب...")
        # ننتظر هنا إلى أجل غير مسمى (لن يتوقف السورس)
        while True:
            await asyncio.sleep(60)

    if running_clients:
        logger.info(f"💎 النظام يعمل بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])
    else:
        logger.error("❌ لا توجد وحدات عاملة. تأكد من صحة الجلسة والتوكن.")
        # ننتظر قليلاً ثم نخرج بشكل نظيف (سيُعيد Pterodactyl التشغيل تلقائيًا)
        await asyncio.sleep(5)
        sys.exit(1)

# -------------------------------------------------------------------
# 10. نقطة الدخول
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 تم إيقاف السورس يدويًا.")
    except SystemExit:
        pass
    except Exception as e:
        logger.critical(f"🔥 خطأ غير متوقع: {e}")
        sys.exit(1)
