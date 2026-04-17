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

# ------------------------------------------
# 1. تحديث وتثبيت المكاتب تلقائيًا
# ------------------------------------------
def setup_environment():
    try:
        print("🛠️ جاري تحديث مكاتب سورس عبود المطور...")
        required_libs = [
            "telethon==1.31.0", "pytz", "pydantic", "aiohttp",
            "requests", "bs4", "aiosqlite"
        ]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي: {e}")

setup_environment()

# استيرادات إضافية بعد التحديث
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except (ImportError, SyntaxError):
    HAS_JOIN_SUPPORT = False
    print("⚠️ نسخة Telethon لا تدعم طلبات الانضمام الجديدة.")

# ------------------------------------------
# 2. إعداد سجل الأخطاء (LOG)
# ------------------------------------------
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

# ------------------------------------------
# 3. البيانات الثابتة وقاعدة البيانات
# ------------------------------------------
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992      # أيدي المطور عبود
DB_PATH = "abood.db"

def init_db():
    """إنشاء جدول sessions إذا لم يكن موجودًا"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY, session TEXT, token TEXT)''')
    conn.commit()
    conn.close()

init_db()   # تأكيد وجود القاعدة قبل أي شيء

BASE_DIR = os.getcwd()
for folder in ["Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# ------------------------------------------
# 4. دالة التوافق مع الموديولات (بدون JoKeRUB)
# ------------------------------------------
def apply_compatibility(client, module):
    # جعل العميل متاحًا بجميع الأسماء المألوفة
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)

    # قاعدة بيانات وهمية إن لزم
    if not hasattr(module, 'database'):
        db_mock = types.ModuleType("database")
        db_mock.update_stats = lambda *args, **kwargs: None
        db_mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db_mock)

    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)

# ------------------------------------------
# 5. محرك تحميل البلغ إنز (Plugins)
# ------------------------------------------
async def start_plugins_engine(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path):
        return
    if full_path not in sys.path:
        sys.path.append(full_path)

    # إنشاء موديول l313l وهمي لمنع أخطاء الاستيراد
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

# ------------------------------------------
# 6. وظائف وضع الأونلاين (BotFather)
# ------------------------------------------
async def mybot_online_setup(user_client, bot_token):
    """
    تفعيل وضع الأونلاين للأزرار والأوامر باسم عبود 🩵
    يتم استدعاؤها بعد تشغيل البوت مباشرة
    """
    try:
        # جلب معلومات البوت عبر عميل مؤقت
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        bot_me = await temp_bot.get_me()
        bot_username = f"@{bot_me.username}"
        await temp_bot.disconnect()

        joker_name = "عبود 🩵"
        commands_text = """start - للبدء 💎
hack - قسم أمر الهـاك ⚡
help - قائمة المساعدة 📚"""

        logger.info(f"⚙️ جاري تحديث إعدادات البوت {bot_username} عبر @BotFather")

        # استخدام محادثة مع BotFather عبر user_client (الحساب الأساسي)
        async with user_client.conversation("@BotFather") as conv:
            # تعيين وضع الإنلاين
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(joker_name)

            # تعيين قائمة الأوامر
            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(commands_text)

        logger.info(f"✅ تم تفعيل وضع الأونلاين للبوت {bot_username}")
    except Exception as e:
        logger.error(f"⚠️ فشل أتمتة BotFather: {e}")

async def add_bot_to_logger_group(user_client, chat_id, bot_token):
    """
    إضافة البوت إلى مجموعة سجل (Logger Group)
    """
    try:
        bot_details = await user_client.get_me()  # هذا يعطي الحساب وليس البوت
        # نحتاج للحصول على كيان البوت الحقيقي، لذلك نستخدم عميل البوت نفسه مؤقتًا
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        bot_username = (await temp_bot.get_me()).username
        await temp_bot.disconnect()

        try:
            await user_client(functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_username,
                fwd_limit=1000000
            ))
        except Exception:
            await user_client(functions.channels.InviteToChannelRequest(
                channel=chat_id,
                users=[bot_username]
            ))
        logger.info(f"✅ تمت دعوة البوت @{bot_username} إلى المجموعة {chat_id}")
    except Exception as e:
        logger.error(f"⚠️ فشل إضافة البوت إلى مجموعة السجل: {e}")

# ------------------------------------------
# 7. معالجة الأوامر الأساسية
# ------------------------------------------
def setup_handlers(client, is_bot=False):
    # دالة مساعدة لتسهيل إنشاء الأوامر
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))

    client.ar_cmd = ar_cmd

    # ---------- أمر التنصيب (للمطور فقط) ----------
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
            # id = 1 دائمًا (يمكن تعديلها لاحقًا لدعم حسابات متعددة)
            c.execute("INSERT OR REPLACE INTO sessions (id, session, token) VALUES (1, ?, ?)",
                      (session_data, token))
            conn.commit()
            conn.close()
            await event.edit("✅ **تم الحفظ بنجاح! سيتم تشغيل البوت الآن.**")
            # إعادة تشغيل الوحدة الرئيسية (اختياري)
            await start_instance(session_data, token, "MainUser")
        except Exception as e:
            await event.edit(f"❌ **فشل التنصيب:** {e}")

    # ---------- أمر تحديث المكاتب ----------
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def abood_update(event):
        if event.sender_id != OWNER_ID:
            return
        await event.edit("🔄 **جاري تحديث جميع مكاتب الهوست...**")
        setup_environment()
        await event.edit("✅ **تم التحديث بنجاح! أرسل `.اعادة تشغيل` الآن.**")

    # ---------- أمر إعادة التشغيل ----------
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def abood_reboot(event):
        if event.sender_id != OWNER_ID:
            return
        await event.edit("♻️ **جاري إعادة تشغيل سورس عبود المطور...**")
        # إعادة تشغيل العملية بالكامل
        os.execl(sys.executable, sys.executable, *sys.argv)

    # ---------- أمر سحب سجل الأخطاء (اللوك) ----------
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

    # ---------- معالج طلبات الانضمام التلقائي ----------
    @client.on(events.Raw)
    async def join_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except:
                pass

    # ---------- إعادة توجيه ملفات ZIP إلى مجموعة النسخ الاحتياطي ----------
    @client.on(events.NewMessage(incoming=True))
    async def zip_forwarder(event):
        if event.file and event.file.ext == ".zip":
            try:
                # يجب تعيين ZIP_BACKUP مسبقًا (مثال -1001234567890)
                # يمكنك تعديله حسب رغبتك
                ZIP_BACKUP = -1001234567890
                await client.send_file(ZIP_BACKUP, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except:
                pass

# ------------------------------------------
# 8. تشغيل وحدة واحدة (حساب + بوت)
# ------------------------------------------
async def start_instance(session_str, token, name):
    user_client = None
    bot_client = None
    try:
        if session_str:
            user_client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await user_client.start()
            setup_handlers(user_client)
            await start_plugins_engine(user_client, "Plugins", f"حساب_{name}")
            running_clients.append(user_client)

        if token:
            bot_client = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot_client.start(bot_token=token)
            setup_handlers(bot_client, is_bot=True)
            await start_plugins_engine(bot_client, "Plugins/assistant", "مساعد")
            running_clients.append(bot_client)

            # تفعيل وضع الأونلاين بعد تشغيل البوت (إذا وجد حساب مستخدم)
            if user_client:
                asyncio.create_task(mybot_online_setup(user_client, token))
                # يمكن إضافة المجموعة المطلوبة هنا (استبدل -100... بمعرف مجموعتك)
                # asyncio.create_task(add_bot_to_logger_group(user_client, -1001234567890, token))

    except Exception as e:
        logger.error(f"❌ فشل تشغيل الوحدة {name}: {e}")

# ------------------------------------------
# 9. الدالة الرئيسية
# ------------------------------------------
async def main():
    logger.info("--- [ ABOOD HOSTING v7.5 ] ---")

    # قراءة بيانات الجلسة والتوكن من قاعدة البيانات
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT session, token FROM sessions WHERE id = 1")
    row = c.fetchone()
    conn.close()

    if row and (row[0] or row[1]):
        await start_instance(row[0], row[1], "MainUser")
    else:
        logger.warning("⚠️ قاعدة البيانات فارغة. استخدم أمر `.تنصيب <التوكن>` بالرد على كود الجلسة.")

    if running_clients:
        logger.info(f"💎 النظام يعمل بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

# ------------------------------------------
# 10. نقطة الدخول
# ------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
