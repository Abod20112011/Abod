import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تحديث البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    try:
        print("🛠️ جاري فحص المكتبات لضمان عمل أمر 'اللوك' وسحب السجلات...")
        # تحديث المكتبات الأساسية لضمان عدم حدوث ImportError
        required_libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "requests", "bs4"]
        # استخدام نسخة Pip المناسبة للبيئة
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي، سيتم استخدام النسخ الحالية: {e}")

# استدعاء دالة التجهيز قبل أي استيراد آخر
setup_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة استيراد ميزات طلبات الانضمام (بشكل آمن لضمان عدم توقف الموديول)
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except (ImportError, SyntaxError):
    HAS_JOIN_SUPPORT = False
    print("⚠️ تحذير: نسخة Telethon لا تدعم ميزات طلبات الانضمام الجديدة.")


# --- [ 2. إعدادات سجل العمليات (LOG) ] ---
# ملاحظة: هذا هو الملف الذي سيتم إرساله عند كتابة .لوك
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def initialize_logger():
    # تصفير السجل عند بداية كل تشغيل لحل مشكلة الملفات التالفة
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

# إعداد المجلدات
BASE_DIR = os.getcwd()
for folder in ["clients", "Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

running_clients = []

# --- [ 4. موديول التوافق البرمجي ] ---
def apply_compatibility(client, module):
    # دعم التسميات المختلفة لضمان عمل موديولات Plugins بدون تعديل
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']
    for alias in aliases:
        setattr(module, alias, client)
    
    # حل مشكلة AttributeError: database
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

# --- [ 6. معالجة الأوامر - إصلاح أمر اللوك ] ---
def setup_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # [أ] أمر اللوك المصلح - يرسل السجل كملف فوراً
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def abood_log_lock(event):
        # محاولة تعديل الرسالة للانتظار
        try:
            if not is_bot: await event.edit("⏳ جاري سحب سجل الهوست...")
        except: pass

        if not os.path.exists(LOG_FILE_PATH):
            err = "⚠️ السجل غير موجود حالياً."
            return await event.respond(err) if is_bot else await event.edit(err)
        
        # إنشاء نسخة مؤقتة لتجنب NameError و Invalid parts
        temp_name = f"log_fix_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE_PATH, temp_name)
            await client.send_file(
                event.chat_id, 
                temp_name, 
                caption=f"📊 **سجل عمليات السورس (الهوست)**",
                reply_to=event.id
            )
            if not is_bot: await event.delete()
        except Exception as e:
            await event.respond(f"❌ خطأ في الإرسال: {e}")
        finally:
            if os.path.exists(temp_name): os.remove(temp_name)

    # [ب] ميزة طلبات الانضمام
    @client.on(events.Raw)
    async def join_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except: pass

    # [ج] تحويل ملفات ZIP
    @client.on(events.NewMessage(incoming=True))
    async def zip_forwarder(event):
        if event.file and event.file.ext == ".zip":
            try: await client.send_file(ZIP_BACKUP, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except: pass

    # [د] إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot(event):
        msg = "♻️ جاري إعادة التشغيل..."
        await event.respond(msg) if is_bot else await event.edit(msg)
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [ 7. مشغل الوحدات ] ---
async def start_instance(s, t, name):
    try:
        if s:
            c = TelegramClient(StringSession(s), API_ID, API_HASH)
            await c.start()
            setup_handlers(c)
            await start_plugins_engine(c, "Plugins", f"حساب_{name}")
            try: await c(JoinChannelRequest(OFFICIAL_CH))
            except: pass
            running_clients.append(c)

        if t:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=t)
            setup_handlers(b, is_bot=True)
            await start_plugins_engine(b, "Plugins/assistant", "مساعد")
            running_clients.append(b)
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {name}: {e}")

async def main():
    logger.info("--- [ ABOOD HOSTING v6.5 ] ---")
    files = [f for f in os.listdir("clients") if f.endswith(".txt")]
    
    if not files:
        s = input("Session: ").strip()
        t = input("Token: ").strip()
        if s:
            with open("clients/admin.txt", "w") as f: f.write(f"{s}\n{t}")
            files = ["admin.txt"]
        else: return

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
