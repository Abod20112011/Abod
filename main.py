import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time, sqlite3

# --- [ 1. نظام تحديث البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    try:
        print("🛠️ جاري فحص وتحديث مكاتب سورس عبود المطور...")
        # المكاتب الأساسية لضمان عمل السورس بدون كراش
        required_libs = [
            "telethon==1.31.0", "pytz", "pydantic", "aiohttp", 
            "requests", "bs4", "aiosqlite"
        ]
        # تنفيذ التحديث الصامت للمكتبات
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي للمكتبات: {e}")

# استدعاء تحديث البيئة عند بدء التشغيل
setup_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة ميزات طلبات الانضمام الجديدة في تيليثون
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
    # تصفير الملف القديم لبدء جلسة جديدة
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
OWNER_ID = 6373993992  # أيدي عبود المطور
DB_PATH = "abood.db"

def init_db():
    """تهيئة قاعدة البيانات وحل مشكلة OperationalError"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # إنشاء الجدول فوراً إذا لم يكن موجوداً
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions 
                     (id INTEGER PRIMARY KEY, session TEXT, token TEXT)''')
    conn.commit()
    conn.close()
    logger.info("✅ تم تهيئة قاعدة البيانات بنجاح.")

# تنفيذ التهيئة قبل أي شيء آخر
init_db()

BASE_DIR = os.getcwd()
# إنشاء المجلدات اللازمة
for folder in ["Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# --- [ 4. موديول التوافق (للموديلات القديمة) ] ---
def apply_compatibility(client, module):
    # حقن العميل بمسميات متعددة لضمان عمل الأكواد الخارجية
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    
    # محاكاة قاعدة البيانات للإضافات التي تطلبها
    if not hasattr(module, 'database'):
        db_mock = types.ModuleType("database")
        db_mock.update_stats = lambda *args, **kwargs: None
        db_mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db_mock)

    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الإضافات ] ---
async def start_plugins_engine(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

    # تعريف الموديول الوهمي لكسر أخطاء الاستيراد
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
                    logger.error(f"❌ خطأ في تحميل {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# --- [ 6. وظيفة وضع الأونلاين (أتمتة BotFather) ] ---
async def abood_online_setup(client, bot_token):
    """تفعيل وضع الأونلاين والأوامر تلقائياً باسم عبود 🩵"""
    try:
        # جلب معلومات البوت
        temp_bot = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_bot.start(bot_token=bot_token)
        me = await temp_bot.get_me()
        bot_username = f"@{me.username}"
        await temp_bot.disconnect()

        joker_name = "عبود 🩵"
        commands_list = "start - للبدء 💎\nhack - قسم أمر الهـاك ⚡\nhelp - قائمة المساعدة 📚"
        
        logger.info(f"⚙️ جاري ضبط إعدادات {bot_username} في BotFather...")
        
        async with client.conversation("@BotFather") as conv:
            # وضع الأونلاين (Inline Mode)
            await conv.send_message("/setinline")
            await asyncio.sleep(1.5)
            await conv.send_message(bot_username)
            await asyncio.sleep(1.5)
            await conv.send_message(joker_name)
            
            # ضبط قائمة الأوامر
            await conv.send_message("/setcommands")
            await asyncio.sleep(1.5)
            await conv.send_message(bot_username)
            await asyncio.sleep(1.5)
            await conv.send_message(commands_list)
        
        logger.info(f"✅ تم تفعيل وضع الأونلاين للبوت {bot_username}")
    except Exception as e:
        logger.error(f"⚠️ فشل في إعدادات BotFather: {e}")

# --- [ 7. معالجة الأوامر والمساعد ] ---
def setup_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # أمر التنصيب الاحترافي (للمطور فقط)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب (.*)$"))
    async def install_proc(event):
        if event.sender_id != OWNER_ID: return
        
        token = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not reply or not reply.text:
            return await event.edit("⚠️ **يجب الرد على كود الجلسة بالأمر:** `.تنصيب <التوكن>`")
        
        session_text = reply.text.strip()
        await event.edit("⏳ **جاري حفظ البيانات في قاعدة بيانات عبود...**")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO sessions (id, session, token) VALUES (1, ?, ?)", (session_text, token))
            conn.commit()
            conn.close()
            
            await event.edit("✅ **تم التنصيب والحفظ بنجاح! سيتم التشغيل الآن.**")
            await start_instance(session_text, token, "SubClient")
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ أثناء التنصيب:** {e}")

    # أوامر التحكم في الهوست
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_all(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("🔄 **جاري تحديث كافة مكاتب السورس...**")
        setup_environment()
        await event.edit("✅ **تم التحديث! أرسل `.اعادة تشغيل` الآن.**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_abood(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة تشغيل السورس بالكامل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # معالجة طلبات الانضمام التلقائية
    @client.on(events.Raw)
    async def join_manager(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except: pass

# --- [ 8. مشغل الوحدات (Instances) ] ---
async def start_instance(s, t, name):
    try:
        user_client = None
        if s:
            user_client = TelegramClient(StringSession(s), API_ID, API_HASH)
            await user_client.start()
            setup_handlers(user_client)
            await start_plugins_engine(user_client, "Plugins", f"حساب_{name}")
            running_clients.append(user_client)

        if t:
            bot_client = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot_client.start(bot_token=t)
            setup_handlers(bot_client, is_bot=True)
            await start_plugins_engine(bot_client, "Plugins/assistant", "مساعد")
            running_clients.append(bot_client)
            
            # تشغيل وضع الأونلاين إذا كان الحساب والبوت متوفرين
            if user_client:
                asyncio.create_task(abood_online_setup(user_client, t))

    except Exception as e:
        logger.error(f"❌ فشل تشغيل {name}: {e}")

async def main():
    logger.info("--- [ ABOOD HOSTING v7.5 ] ---")
    
    # القراءة الآمنة من قاعدة البيانات
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT session, token FROM sessions")
    row = cursor.fetchone()
    conn.close()

    if row:
        # تشغيل البيانات المخزنة
        await start_instance(row[0], row[1], "Main")
    else:
        logger.warning("⚠️ قاعدة البيانات فارغة. استخدم أمر .تنصيب لإضافة بياناتك.")

    if running_clients:
        logger.info(f"💎 سورس عبود يعمل الآن بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass

