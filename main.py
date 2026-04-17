import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time, sqlite3

# --- [ 1. نظام تحديث البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    try:
        print("🛠️ جاري فحص وتحديث المكتبات لضمان عمل السورس بأعلى كفاءة...")
        # قائمة المكاتب المطلوبة للسورس
        required_libs = [
            "telethon==1.31.0", "pytz", "pydantic", "aiohttp", 
            "requests", "bs4", "aiosqlite"
        ]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي، سيتم استخدام النسخ الموجودة: {e}")

setup_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة استيراد ميزات طلبات الانضمام
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except (ImportError, SyntaxError):
    HAS_JOIN_SUPPORT = False
    print("⚠️ تحذير: نسخة Telethon لا تدعم ميزات طلبات الانضمام الجديدة.")

# --- [ 2. إعدادات سجل العمليات (LOG) ] ---
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def initialize_logger():
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

# --- [ 3. البيانات الثابتة وإدارة قاعدة البيانات ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992  # أيدي عبود
DB_PATH = "abood.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions 
                     (id INTEGER PRIMARY KEY, session TEXT, token TEXT)''')
    conn.commit()
    conn.close()

init_db()

BASE_DIR = os.getcwd()
for folder in ["Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# --- [ 4. موديول التوافق البرمجي ] ---
def apply_compatibility(client, module):
    # إتاحة العميل داخل الموديولات لضمان عمل الإضافات القديمة
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

# --- [ 5. محرك تحميل الموديولات ] ---
async def start_plugins_engine(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

    # تعريف الموديول الوهمي لكسر أخطاء الاستيراد (l313l)
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
                    if hasattr(module, 'setup'): module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# --- [ 6. وظيفة الأونلاين وBotFather ] ---
async def mybot_online_setup(client, bot_token):
    """وظيفة لضبط وضع الأونلاين والأوامر تلقائياً باسم عبود"""
    try:
        # إنشاء عميل مؤقت للبوت لجلب معلوماته
        bot_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await bot_client.start(bot_token=bot_token)
        me = await bot_client.get_me()
        bot_username = f"@{me.username}"
        await bot_client.disconnect()

        joker_name = "عبود 🩵"
        commands_text = "start - للبدء 💎\nhack - قسم أمر الهـاك ⚡\nhelp - قائمة المساعدة 📚"
        
        logger.info(f"⚙️ جاري تحديث إعدادات البوت {bot_username} في BotFather...")
        
        async with client.conversation("@BotFather") as conv:
            # ضبط الأونلاين (Inline)
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(joker_name)
            
            # ضبط الأوامر
            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(commands_text)
        
        logger.info(f"✅ تم تفعيل وضع الأونلاين للبوت {bot_username}")
    except Exception as e:
        logger.error(f"⚠️ فشل في إعدادات BotFather: {e}")

# --- [ 7. معالجة الأوامر الرئيسية ] ---
def setup_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # أمر التنصيب الجديد (بالرد على الجلسة + التوكن)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def install_bot(event):
        if event.sender_id != OWNER_ID: return
        
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ **يجب الرد على كود الجلسة بالأمر:** `.تنصيب <التوكن>`")
        
        session = reply.text.strip()
        await event.edit("⏳ **جاري حفظ البيانات في قاعدة البيانات وتشغيل البوت...**")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO sessions (id, session, token) VALUES (1, ?, ?)", (session, token))
            conn.commit()
            conn.close()
            
            await event.edit("✅ **تم الحفظ بنجاح! جاري التشغيل...**")
            await start_instance(session, token, "MainUser")
        except Exception as e:
            await event.edit(f"❌ **فشل التنصيب:** {e}")

    # أمر تحديث المكاتب
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_libs(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("🔄 **جاري تحديث جميع مكاتب الهوست...**")
        try:
            setup_environment()
            await event.edit("✅ **تم التحديث بنجاح! أرسل `.اعادة تشغيل` الآن.**")
        except Exception as e:
            await event.edit(f"❌ **فشل التحديث:** {e}")

    # أمر إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_server(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة تشغيل سورس عبود...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # معالج طلبات الانضمام
    @client.on(events.Raw)
    async def join_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except: pass

# --- [ 8. مشغل الوحدات الاستنساخي ] ---
async def start_instance(s, t, name):
    try:
        user_c = None
        if s:
            user_c = TelegramClient(StringSession(s), API_ID, API_HASH)
            await user_c.start()
            setup_handlers(user_c)
            await start_plugins_engine(user_c, "Plugins", f"حساب_{name}")
            running_clients.append(user_c)

        if t:
            bot_c = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot_c.start(bot_token=t)
            setup_handlers(bot_c, is_bot=True)
            await start_plugins_engine(bot_c, "Plugins/assistant", "مساعد")
            running_clients.append(bot_c)
            
            # تشغيل أتمتة BotFather في الخلفية
            if user_c:
                asyncio.create_task(mybot_online_setup(user_c, t))

    except Exception as e:
        logger.error(f"❌ فشل تشغيل {name}: {e}")

async def main():
    logger.info("--- [ ABOOD HOSTING v7.0 ] ---")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT session, token FROM sessions")
    row = cursor.fetchone()
    conn.close()

    if row:
        await start_instance(row[0], row[1], "AboodBot")
    else:
        logger.warning("⚠️ لا توجد بيانات في قاعدة البيانات. استخدم أمر .تنصيب")

    if running_clients:
        logger.info(f"💎 النظام يعمل بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
