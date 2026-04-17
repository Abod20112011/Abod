import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تحديث البيئة الإجباري ] ---
def update_requirements():
    try:
        print("🔄 جاري تحديث المكتبات لضمان عمل نظام 'اللوك' والتشغيل...")
        libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "requests"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + libs)
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي: {e}")

update_requirements()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# تعريف القفل البرمجي (Lock) عالمياً لحل مشكلة NameError
lock = asyncio.Lock()

try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SYS = True
except ImportError:
    HAS_JOIN_SYS = False

# --- [ 2. إعدادات السجل المطور ] ---
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def setup_master_logging():
    if os.path.exists(LOG_FILE_PATH):
        try: os.remove(LOG_FILE_PATH)
        except: pass
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"🚀 سورس عبود - نظام التشغيل v6.0 | {time.ctime()}\n")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'), logging.StreamHandler()]
    )
    return logging.getLogger("PHOENIX")

logger = setup_master_logging()

# --- [ 3. البيانات والثوابت ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OFFICIAL_CHANNEL = 'lAYAI'
ZIP_LOG_CHAT = -1001234567890 

# المجلدات
BASE_DIR = os.getcwd()
for folder in ["clients", "Plugins", "Plugins/assistant"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

active_sessions = []

# --- [ 4. طبقة التوافق البرمجي ] ---
def apply_core_compatibility(client, module):
    # ربط المتغير lock بالموديولات لضمان عدم ظهور NameError
    setattr(module, 'lock', lock)
    
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']
    for a in aliases: setattr(module, a, client)
    
    if not hasattr(module, 'database'):
        db = types.ModuleType("database")
        db.update_stats = lambda *args, **kwargs: None
        setattr(module, 'database', db)

    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الموديولات ] ---
async def load_all_plugins(client, folder_path, tag):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_path)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

    for root, _, files in os.walk(full_path):
        if "assistant" in root and tag != "مساعد": continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                mod_name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    sys.modules["JoKeRUB"].lock = lock
                    
                    apply_core_compatibility(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'): module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ موديول {file}: {e}")
    logger.info(f"✨ {tag}: تم تحميل {count} ملف.")

# --- [ 6. معالجة الأوامر ونظام اللوك ] ---
def setup_core_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    client.ar_cmd = ar_cmd

    # [أ] أمر اللوك (Lock) المصلح - تم تعريفه هنا ليتوافق مع نظام التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def lock_cmd_handler(event):
        # استخدام القفل العالمي لمنع تداخل العمليات
        async with lock:
            status = "🔐 **تم تفعيل نظام القفل البرمجي (Lock) بنجاح.**"
            try:
                if is_bot: await event.respond(status)
                else: await event.edit(status)
            except: pass

    # [ب] أمر اللوج (Log) المصلح
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def log_cmd_handler(event):
        if is_bot: await event.respond("⏳ جاري سحب السجل...")
        else: await event.edit("⏳ جاري سحب السجل...")
        
        if not os.path.exists(LOG_FILE_PATH):
            return await event.respond("⚠️ لا يوجد سجل.") if is_bot else await event.edit("⚠️ لا يوجد سجل.")
        
        tmp = f"log_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE_PATH, tmp)
            await client.send_file(event.chat_id, tmp, caption="📊 سجل سورس عبود")
            if not is_bot: await event.delete()
        except Exception as e: await event.respond(f"❌ خطأ: {e}")
        finally:
            if os.path.exists(tmp): os.remove(tmp)

    # [ج] قبول طلبات الانضمام
    @client.on(events.Raw)
    async def on_join_request(update):
        if HAS_JOIN_SYS and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                p = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=p, user_id=update.user_id, approve=True))
            except: pass

    # [د] إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot_system(event):
        if is_bot: await event.respond("♻️ جاري إعادة التشغيل...")
        else: await event.edit("♻️ جاري إعادة التشغيل...")
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [ 7. مشغل النظام ] ---
async def start_instance(s, t, name):
    try:
        if s:
            c = TelegramClient(StringSession(s), API_ID, API_HASH)
            await c.start()
            setup_core_handlers(c)
            await load_all_plugins(c, "Plugins", f"حساب_{name}")
            try: await c(JoinChannelRequest(OFFICIAL_CHANNEL))
            except: pass
            active_sessions.append(c)

        if t:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=t)
            setup_core_handlers(b, is_bot=True)
            await load_all_plugins(b, "Plugins/assistant", "مساعد")
            active_sessions.append(b)
    except Exception as e: logger.error(f"❌ فشل {name}: {e}")

async def main():
    logger.info("--- [ PHOENIX v6.0 - ABOOD ] ---")
    acc_files = [f for f in os.listdir("clients") if f.endswith(".txt")]
    
    for f in acc_files:
        with open(f"clients/{f}", "r") as fl:
            d = fl.read().splitlines()
            if d: await start_instance(d[0], d[1] if len(d)>1 else None, f)

    if active_sessions:
        await asyncio.gather(*[cl.run_until_disconnected() for cl in active_sessions])

if __name__ == "__main__":
    try: asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass

