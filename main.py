import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تحديث البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    try:
        print("🛠️ جاري فحص المكتبات لضمان عمل أمر 'اللوك' وسحب السجلات...")
        # تم إضافة aiosqlite هنا لتعمل مع قاعدة البيانات بدون مشاكل
        required_libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "requests", "bs4", "aiosqlite"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي، سيتم استخدام النسخ الحالية: {e}")

setup_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة استيراد ميزات طلبات الانضمام (لم يتم المساس بها)
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

# --- [ 3. البيانات والثوابت ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
OFFICIAL_CH = 'lAYAI' 
ZIP_BACKUP = -1001234567890 

BASE_DIR = os.getcwd()
for folder in ["clients", "Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# --- [ إضافة جديدة: نظام قاعدة البيانات لحفظ الجلسة والتوكن ] ---
def save_to_db(session, token, name):
    with open(f"clients/{name}.txt", "w") as f:
        f.write(f"{session}\n{token}")

# --- [ إضافة جديدة: نظام الأونلاين (Inline) كما طلبته ] ---
async def setup_inline(client, bot_username):
    try:
        joker = "عبود 🩵"
        commands_aRRaS = "start - للبدء\nhack - قسم أمر الهـاك"
        logger.info(f"⚙️ جاري تفعيل الـ Inline لبوت: {bot_username}")
        
        async with client.conversation("@BotFather") as conv:
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(joker)
            
            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(commands_aRRaS)
    except Exception as e:
        logger.error(f"⚠️ فشل تفعيل الأونلاين: {e}")

# --- [ 4. موديول التوافق البرمجي (تم إرجاع ar_cmd لضمان عمل ملفاتك القديمة) ] ---
def apply_compatibility(client, module):
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    
    if not hasattr(module, 'database'):
        db_mock = types.ModuleType("database")
        db_mock.update_stats = lambda *args, **kwargs: None
        db_mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db_mock)

    # هذا السطر هو الذي يضمن عمل أوامرك القديمة!
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الموديولات (كما هو بالضبط) ] ---
async def start_plugins_engine(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

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
                    
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    apply_compatibility(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'): module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# --- [ 6. معالجة الأوامر (دوالك الأساسية + الأوامر الجديدة) ] ---
def setup_handlers(client, is_bot=False):
    # دالتك الأساسية لعمل الأوامر القديمة
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # دالة اللوك الخاصة بك
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def abood_log_lock(event):
        try:
            if not is_bot: await event.edit("⏳ جاري سحب سجل الهوست...")
        except: pass

        if not os.path.exists(LOG_FILE_PATH):
            err = "⚠️ السجل غير موجود حالياً."
            return await event.respond(err) if is_bot else await event.edit(err)
        
        temp_name = f"log_fix_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE_PATH, temp_name)
            await client.send_file(
                event.chat_id, 
                temp_name, 
                caption=f"📊 **سجل عمليات السورس (الهوست)**\n👤 **المطور:** عبود",
                reply_to=event.id
            )
            if not is_bot: await event.delete()
        except Exception as e:
            if is_bot: await event.respond(f"❌ خطأ: {e}")
            else: await event.edit(f"❌ خطأ: {e}")
        finally:
            if os.path.exists(temp_name): os.remove(temp_name)

    # معالجة طلبات الانضمام (دالتك)
    @client.on(events.Raw)
    async def join_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except: pass

    # توجيه ملفات الـ zip (دالتك)
    @client.on(events.NewMessage(incoming=True))
    async def zip_forwarder(event):
        if event.file and event.file.ext == ".zip":
            try: await client.send_file(ZIP_BACKUP, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except: pass

    # أمر إعادة التشغيل (مطور)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot(event):
        if event.sender_id != OWNER_ID: return
        msg = "♻️ جاري إعادة التشغيل على الهوست..."
        await event.respond(msg) if is_bot else await event.edit(msg)
        os.execl(sys.executable, sys.executable, *sys.argv)

    # --- [ الأوامر الجديدة التي طلبتها ] ---
    
    # تحديث المكاتب
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_libs(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("📦 **جاري تحديث جميع المكاتب...**")
        setup_environment()
        await event.edit("✅ **تم التحديث بنجاح! سيتم إعادة التشغيل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # أمر التنصيب بالرد على ملف
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?P<id> \d+)?$"))
    async def install_other(event):
        if event.sender_id != OWNER_ID: return
        if not event.is_reply:
            return await event.edit("⚠️ **يجب الرد على ملف نصي يحتوي على (الجلسة ثم التوكن).**")
        
        target_id = event.pattern_match.group('id')
        reply_msg = await event.get_reply_message()
        
        if reply_msg.file:
            path = await reply_msg.download_media("clients/temp_setup.txt")
            with open(path, "r") as f:
                data = f.read().splitlines()
            
            if len(data) >= 2:
                new_name = target_id.strip() if target_id else "new_user"
                save_to_db(data[0], data[1], new_name)
                await event.edit(f"✅ **تم تنصيب السورس لـ {new_name} بنجاح!**\nسيعمل عند إعادة التشغيل القادمة.")
            else:
                await event.edit("❌ **الملف المردود عليه لا يحتوي على بيانات كافية (يجب أن يكون سطرين: جلسة ثم توكن).**")

# --- [ 7. مشغل الوحدات ] ---
async def start_instance(s, t, name):
    try:
        if s:
            c = TelegramClient(StringSession(s), API_ID, API_HASH)
            await c.start()
            setup_handlers(c)
            await start_plugins_engine(c, "Plugins", f"حساب_{name}")
            running_clients.append(c)

        if t:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=t)
            setup_handlers(b, is_bot=True)
            # استدعاء دالة الأونلاين للبوت
            me = await b.get_me()
            await setup_inline(c, f"@{me.username}") 
            await start_plugins_engine(b, "Plugins/assistant", "مساعد")
            running_clients.append(b)
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {name}: {e}")

async def main():
    logger.info("--- [ ABOOD HOSTING v7.5 ] ---")
    if not os.path.exists("clients"): os.makedirs("clients")
    
    # فحص ملفات التنصيب
    files = [f for f in os.listdir("clients") if f.endswith(".txt")]
    
    # إذا لم يكن هناك ملفات (أول تشغيل)، اطلبها واحفظها في قاعدة البيانات
    if not files:
        print("⚠️ لم يتم العثور على ملفات تنصيب.")
        s = input("أدخل كود الجلسة: ")
        t = input("أدخل توكن البوت: ")
        save_to_db(s, t, "admin")
        files = ["admin.txt"]

    for f in files:
        with open(f"clients/{f}", "r") as fl:
            d = fl.read().splitlines()
            if d: await start_instance(d[0], d[1] if len(d)>1 else None, f)

    if running_clients:
        logger.info(f"💎 النظام يعمل بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
