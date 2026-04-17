import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تهيئة البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    try:
        print("🛠️ جاري التحقق من المكتبات الأساسية لضمان عمل كافة الأوامر...")
        # تحديث المكتبات في مجلد المستخدم لتجاوز قيود الاستضافة (Pterodactyl)
        required_libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "requests", "bs4"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي، سيتم الاعتماد على النسخ الموجودة: {e}")

setup_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة استيراد ميزات طلبات الانضمام لضمان استقرار التشغيل
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    HAS_JOIN_SUPPORT = True
except ImportError:
    HAS_JOIN_SUPPORT = False

# --- [ 2. حل مشكلة اللوج (Log) الشاملة ] ---
LOG_FILE_PATH = "سجل_الأخطاء.txt"

def initialize_logger():
    # تصفير الملف عند كل بداية تشغيل لضمان عدم حدوث تداخل بيانات (Invalid Parts)
    if os.path.exists(LOG_FILE_PATH):
        try: os.remove(LOG_FILE_PATH)
        except: pass
    
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"📊 سورس عبود المطور | سجل التشغيل: {time.ctime()}\n")
        f.write("--------------------------------------------------\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("PHOENIX_MASTER")

logger = initialize_logger()

# --- [ 3. الإعدادات والثوابت البرمجية ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
OFFICIAL_CHANNEL = 'lAYAI' 
ZIP_BACKUP_GROUP = -1001234567890 

# إعداد المسارات والمجلدات
ROOT_PATH = os.getcwd()
DIRECTORIES = ["clients", "Plugins", "Plugins/assistant"]
for folder in DIRECTORIES:
    os.makedirs(os.path.join(ROOT_PATH, folder), exist_ok=True)

loaded_instances = []

# --- [ 4. موديول التوافق البرمجي (Compatibility) ] ---
def inject_compatibility(client, module):
    # دعم الموديولات التي تعتمد على تسميات مختلفة (zedub, joker, ph_bot)
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']
    for alias in aliases:
        setattr(module, alias, client)
    
    # حل مشكلة نقص موديول database لضمان عمل الموديولات القديمة
    if not hasattr(module, 'database'):
        mock_db = types.ModuleType("database")
        mock_db.update_stats = lambda *args, **kwargs: None
        mock_db.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', mock_db)

    # ربط فلاتر الأوامر المخصصة
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الملفات والموديولات ] ---
async def plugin_launcher(client, folder_dir, label_tag):
    count = 0
    target_path = os.path.join(ROOT_PATH, folder_dir)
    if not os.path.exists(target_path): return
    if target_path not in sys.path:
        sys.path.append(target_path)

    for root, _, files in os.walk(target_path):
        # منع تداخل موديولات المساعد مع الحسابات الشخصية
        if "assistant" in root and label_tag != "مساعد":
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    
                    # بيئة عمل مخصصة لبعض السورسات الشائعة
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    inject_compatibility(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خلل في الموديول {file}: {e}")
    logger.info(f"✨ {label_tag}: تم تفعيل {count} موديول بنجاح.")

# --- [ 6. الوظائف الأساسية ومعالجة الأوامر ] ---
def attach_handlers(client, is_bot=False):
    # تعريف فلتر الأوامر الذكي
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # [1] قبول طلبات الانضمام تلقائياً
    @client.on(events.Raw)
    async def join_requests_auto(update):
        if HAS_JOIN_SUPPORT and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                peer = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=peer, user_id=update.user_id, approve=True))
            except: pass

    # [2] تحويل ملفات ZIP الواردة
    @client.on(events.NewMessage(incoming=True))
    async def auto_forward_zip(event):
        if event.file and event.file.ext == ".zip":
            try:
                await client.send_file(ZIP_BACKUP_GROUP, event.media, caption=f"📦 مستلم من: `{event.sender_id}`")
            except: pass

    # [3] إصلاح أمر اللوج (حل مشكلة AttributeError: edit و Invalid Parts)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def log_fetcher(event):
        # التحقق إذا كان المرسل بوت أو مستخدم لتجنب خطأ .edit
        status_msg = "⏳ جاري جلب السجل..."
        try:
            if is_bot: await event.respond(status_msg)
            else: await event.edit(status_msg)
        except: pass

        if not os.path.exists(LOG_FILE_PATH) or os.path.getsize(LOG_FILE_PATH) < 10:
            return await event.respond("⚠️ السجل فارغ حالياً.") if is_bot else await event.edit("⚠️ السجل فارغ.")
        
        # استخدام تقنية النسخ الفيزيائي للملف لتجاوز قفل السيستم
        temp_log = f"abood_log_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE_PATH, temp_log)
            await client.send_file(event.chat_id, temp_log, caption="📊 سجل عمليات سورس عبود المطور")
            if not is_bot: await event.delete()
        except Exception as e:
            await event.respond(f"❌ فشل الإرسال: {e}")
        finally:
            if os.path.exists(temp_log): os.remove(temp_log)

    # [4] أمر إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def restart_proc(event):
        msg = "♻️ جاري إعادة التشغيل وتحديث البيئة..."
        if is_bot: await event.respond(msg)
        else: await event.edit(msg)
        os.execl(sys.executable, sys.executable, *sys.argv)

    # [5] ميزة التنصيب السريع
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?:\s+(.*))?"))
    async def quick_deploy(event):
        if not event.is_reply:
            return await event.respond("⚠️ رد على كود الجلسة أولاً.") if is_bot else await event.edit("⚠️ رد على الجلسة.")
        
        reply = await event.get_reply_message()
        session_data = reply.text.strip()
        bot_token = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        
        uid = reply.sender_id
        save_path = f"clients/user_{uid}.txt"
        with open(save_path, "w") as f:
            f.write(f"{session_data}\n{bot_token}")
        
        success_msg = f"✅ تم الحفظ. جاري تشغيل الحساب {uid}..."
        await event.respond(success_msg) if is_bot else await event.edit(success_msg)
        await start_instance(session_data, bot_token, f"user_{uid}")

# --- [ 7. مشغل الحسابات والبوتات ] ---
async def start_instance(session_str, token_str, name_tag):
    try:
        if session_str:
            c = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await c.start()
            attach_handlers(c)
            await plugin_launcher(c, "Plugins", f"حساب_{name_tag}")
            try: await c(JoinChannelRequest(OFFICIAL_CHANNEL))
            except: pass
            loaded_instances.append(c)
            logger.info(f"🚀 تم تشغيل الجلسة بنجاح: {name_tag}")

        if token_str:
            b = TelegramClient(f"bot_{name_tag}", API_ID, API_HASH)
            await b.start(bot_token=token_str)
            attach_handlers(b, is_bot=True)
            await plugin_launcher(b, "Plugins/assistant", "مساعد")
            loaded_instances.append(b)
    except Exception as e:
        logger.error(f"❌ خطأ إقلاع {name_tag}: {e}")

async def main():
    logger.info("--- [ PHOENIX HOSTING v5.0 | ABOOD ] ---")
    
    # فحص الحسابات المسجلة في مجلد clients
    account_files = [f for f in os.listdir("clients") if f.endswith(".txt")]
    
    if not account_files:
        print("🆕 لا توجد حسابات. يرجى إدخال البيانات:")
        s = input("Session String: ").strip()
        t = input("Bot Token: ").strip()
        if s:
            with open("clients/admin.txt", "w") as f: f.write(f"{s}\n{t}")
            account_files = ["admin.txt"]
        else: return

    for file_name in account_files:
        with open(f"clients/{file_name}", "r") as f:
            lines = f.read().splitlines()
            if lines:
                await start_instance(lines[0], lines[1] if len(lines) > 1 else None, file_name)

    if loaded_instances:
        logger.info(f"💎 النظام يعمل الآن بـ {len(loaded_instances)} جلسات نشطة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in loaded_instances])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 تم إغلاق النظام.")

