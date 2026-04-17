import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تحديث المكتبات الإجباري ] ---
def force_update_requirements():
    try:
        print("🚀 جاري تهيئة البيئة وتحديث المكتبات...")
        # تحديث Telethon لإصدار يدعم طلبات الانضمام
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "telethon==1.31.0"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "pydantic", "pytz"])
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي (قد يكون بسبب قيود الاستضافة): {e}")

force_update_requirements()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import HideChatJoinRequestRequest

# حل مشكلة ImportError في الصور الأخيرة
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    HAS_JOIN_TYPES = True
except ImportError:
    HAS_JOIN_TYPES = False
    print("⚠️ تحذير: مكتبة Telethon قديمة، تم تفعيل نظام التوافق التلقائي.")

# --- [ 2. حل مشكلة اللوج (Log) ] ---
LOG_FILENAME = "سجل_الأخطاء.txt"

def initialize_logger():
    # تصفير السجل عند كل تشغيل جديد لحل مشكلة التعليق
    try:
        with open(LOG_FILENAME, "w", encoding="utf-8") as f:
            f.write(f"=== سجل تشغيل سورس عبود - {time.ctime()} ===\n")
    except: pass

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ABOOD_SYSTEM")

logger = initialize_logger()

# --- [ 3. الإعدادات والمعلومات ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
CHANNEL_USERNAME = 'lAYAI' 
FORWARD_GROUP_ID = -1001234567890 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, "clients")
PLUGINS_PATH = os.path.join(BASE_DIR, "Plugins")
ASSISTANT_PATH = os.path.join(PLUGINS_PATH, "assistant")

for d in [CLIENTS_DIR, PLUGINS_PATH, ASSISTANT_PATH]:
    os.makedirs(d, exist_ok=True)

running_clients = []

# --- [ 4. موديول التوافق البرمجي ] ---
def apply_compatibility(client, module):
    # ربط الكائنات البرمجية لضمان عمل ملفات Plugins بدون تعديل
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']
    for a in aliases: setattr(module, a, client)
    
    # محاكاة قاعدة البيانات لتجنب AttributeError
    if not hasattr(module, 'database'):
        db = types.ModuleType("database")
        db.update_stats = lambda *args, **kwargs: None
        db.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db)

    # ربط الفلاتر والأوامر
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الملفات ] ---
async def start_plugins_engine(client, path, tag):
    loaded = 0
    if not os.path.exists(path): return
    if path not in sys.path: sys.path.append(path)

    for root, _, files in os.walk(path):
        if "assistant" in root and tag != "مساعد": continue
        for f in files:
            if f.endswith(".py") and not f.startswith("__"):
                name = f[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(name, os.path.join(root, f))
                    mod = importlib.util.module_from_spec(spec)
                    
                    # بيئة PHOENIX
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    apply_compatibility(client, mod)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, 'setup'): mod.setup(client)
                    loaded += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في {f} [{tag}]: {e}")
    logger.info(f"✨ {tag}: تم تحميل {loaded} ملف بنجاح.")

# --- [ 6. الأوامر والوظائف الذكية ] ---
def setup_handlers(client, is_bot=False):
    # تعريف فلتر الأوامر
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    client.ar_cmd = ar_cmd

    # حماية من انهيار طلبات الانضمام (Raw Update)
    @client.on(events.Raw)
    async def raw_join_handler(update):
        if not HAS_JOIN_TYPES: return
        if isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except: pass

    # ميزة ZIP Auto-Forward
    @client.on(events.NewMessage(incoming=True))
    async def on_zip_received(event):
        if event.file and event.file.ext == ".zip":
            try: await client.send_file(FORWARD_GROUP_ID, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except: pass

    # أمر اللوج (تم تصحيح مشكلة invalid file parts)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def send_logs(event):
        await event.edit("⏳ جاري تحضير السجل...")
        if not os.path.exists(LOG_FILENAME) or os.path.getsize(LOG_FILENAME) < 10:
            return await event.edit("⚠️ السجل فارغ حالياً.")
        
        # استخدام ملف مؤقت لتفادي قفل الملف
        tmp = f"log_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILENAME, tmp)
            await client.send_file(event.chat_id, tmp, caption="📊 سجل عمليات السورس")
            await event.delete()
        except Exception as e: await event.edit(f"❌ فشل: {e}")
        finally: 
            if os.path.exists(tmp): os.remove(tmp)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot(event):
        await event.edit("♻️ جاري إعادة التشغيل وتحديث المكتبات...")
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [ 7. تشغيل الجلسات ] ---
async def boot_instance(session, token, name):
    try:
        if session:
            c = TelegramClient(StringSession(session), API_ID, API_HASH)
            await c.start()
            setup_handlers(c)
            await start_plugins_engine(c, PLUGINS_PATH, f"حساب-{name}")
            try: await c(JoinChannelRequest(CHANNEL_USERNAME))
            except: pass
            running_clients.append(c)

        if token:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=token)
            setup_handlers(b, is_bot=True)
            await start_plugins_engine(b, ASSISTANT_PATH, "مساعد")
            running_clients.append(b)
    except Exception as e: logger.error(f"❌ فشل {name}: {e}")

async def main():
    logger.info("--- [ PHOENIX HOSTING v3.5 ] ---")
    files = [f for f in os.listdir(CLIENTS_DIR) if f.endswith(".txt")]
    
    if not files:
        # إذا لم توجد ملفات، يطلب البيانات من الكونسول لأول مرة
        s = input("Session: ").strip()
        t = input("Token: ").strip()
        if s:
            with open(os.path.join(CLIENTS_DIR, "admin.txt"), "w") as f: f.write(f"{s}\n{t}")
            files = ["admin.txt"]
        else: return

    for f in files:
        with open(os.path.join(CLIENTS_DIR, f), "r") as fl:
            data = fl.read().splitlines()
            if data: await boot_instance(data[0], data[1] if len(data)>1 else None, f)

    if running_clients:
        logger.info(f"💎 النظام يعمل الآن بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try: asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass

