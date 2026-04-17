import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ نظام التحديث التلقائي للمكتبات ] ---
def update_libraries():
    try:
        print("🔄 جاري التحقق من تحديثات المكتبات...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "telethon", "pytz", "pydantic"])
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي، سيتم الاستمرار بالإصدار الحالي: {e}")

update_libraries()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import HideChatJoinRequestRequest
from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest

# --- [ إعدادات السجل وحل مشكلة عدم العمل إلا بعد الريستارت ] ---
LOG_FILENAME = "سجل_الأخطاء.txt"

# دالة لتصفير السجل عند بداية التشغيل الحقيقي فقط
def clear_logs():
    try:
        with open(LOG_FILENAME, "w", encoding="utf-8") as f:
            f.write(f"--- بداية جلسة التشغيل: {time.ctime()} ---\n")
    except: pass

clear_logs()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PHOENIX_MASTER")

# --- الإعدادات الثابتة ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
CHANNEL_USERNAME = 'lAYAI' 
FORWARD_GROUP_ID = -1001234567890 

# --- مسارات النظام ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, "clients")
PLUGINS_PATH = os.path.join(BASE_DIR, "Plugins")
ASSISTANT_PATH = os.path.join(PLUGINS_PATH, "assistant")

for path in [CLIENTS_DIR, PLUGINS_PATH, ASSISTANT_PATH]:
    os.makedirs(path, exist_ok=True)

running_clients = []

# --- [ طبقة التوافق مع السورسات الأخرى ] ---
def make_compatible(client, module):
    # دعم جميع الأسماء البرمجية الشائعة
    for alias in ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']:
        setattr(module, alias, client)
    
    # حل مشكلة AttributeError: module 'database' has no attribute 'update_stats'
    if not hasattr(module, 'database'):
        mock_db = types.ModuleType("database")
        mock_db.update_stats = lambda *args, **kwargs: None
        mock_db.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', mock_db)
    
    # ربط أوامر التحكم
    if hasattr(client, 'ar_cmd'):
        for cmd_alias in ['ar_cmd', 'zed_cmd', 'admin_cmd', 'ph_cmd']:
            setattr(module, cmd_alias, client.ar_cmd)

# --- نظام تحميل الموديولات المطور ---
async def load_plugins(client, folder_path, label):
    count = 0
    if not os.path.exists(folder_path): return
    if folder_path not in sys.path:
        sys.path.append(folder_path)

    for root, dirs, files in os.walk(folder_path):
        # تخطي مجلد المساعد إذا كنا نشحن حساباً عادياً والعكس
        if "assistant" in root and label != "بوت_المساعد":
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                file_path = os.path.join(root, file)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    
                    # إنشاء بيئة وهمية لبعض السورسات التي تتطلب وجود موديول رئيسي
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    make_compatible(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خلل في {file} ({label}): {e}")
    
    logger.info(f"✅ {label}: تم تفعيل {count} موديول.")

# --- نظام المعالجة والتحكم (Handlers) ---
def add_handler_to_client(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # [1] حل مشكلة طلبات الانضمام (نسخة الحماية القصوى)
    @client.on(events.Raw)
    async def join_handler(update):
        if isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                peer = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=peer, user_id=update.user_id, approve=True))
            except: pass

    # [2] تحويل ملفات ZIP تلقائياً
    @client.on(events.NewMessage(incoming=True))
    async def zip_forwarder(event):
        if event.file and event.file.ext == ".zip":
            try:
                await client.send_file(FORWARD_GROUP_ID, event.media, caption=f"📦 ملف جديد من: {event.sender_id}")
            except: pass

    # [3] أمر إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def restart_handler(event):
        await event.edit("🔄 جارٍ إعادة تشغيل النظام بالكامل...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # [4] أمر اللوج (تم حل مشكلة التوقف)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def logs_handler(event):
        await event.edit("⏳ جاري سحب سجل العمليات...")
        temp_log = f"temp_{int(time.time())}.txt"
        try:
            if os.path.exists(LOG_FILENAME) and os.path.getsize(LOG_FILENAME) > 0:
                shutil.copyfile(LOG_FILENAME, temp_log)
                await client.send_file(event.chat_id, temp_log, caption="📊 سجل أخطاء سورس عبود المطور")
                await event.delete()
            else:
                await event.edit("⚠️ لا توجد أخطاء مسجلة حالياً.")
        except Exception as e:
            await event.edit(f"❌ حدث خطأ أثناء سحب السجل: {e}")
        finally:
            if os.path.exists(temp_log): os.remove(temp_log)

    # [5] أمر التنصيب
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?:\s+(.*))?"))
    async def deploy_handler(event):
        if not event.is_reply:
            return await event.edit("⚠️ يرجى الرد على كود الجلسة أولاً.")
        
        reply_msg = await event.get_reply_message()
        session_text = reply_msg.text.strip()
        bot_token = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        
        user_id = reply_msg.sender_id
        path = os.path.join(CLIENTS_DIR, f"user_{user_id}.txt")
        
        with open(path, "w") as f:
            f.write(f"{session_text}\n{bot_token}")
        
        await event.edit(f"✅ تم الحفظ. جاري تشغيل الحساب {user_id}...")
        await start_instance(session_text, bot_token, f"user_{user_id}")

# --- مشغل الجلسات ---
async def start_instance(session_str, bot_token, identifier):
    try:
        if session_str:
            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await client.start()
            add_handler_to_client(client, is_bot=False)
            await load_plugins(client, PLUGINS_PATH, f"حساب_{identifier}")
            try: await client(JoinChannelRequest(CHANNEL_USERNAME))
            except: pass
            running_clients.append(client)
            logger.info(f"🚀 تشغيل: {identifier}")

        if bot_token:
            bot = TelegramClient(f"bot_{identifier}", API_ID, API_HASH)
            await bot.start(bot_token=bot_token)
            add_handler_to_client(bot, is_bot=True)
            await load_plugins(bot, ASSISTANT_PATH, "بوت_المساعد")
            try: await bot(JoinChannelRequest(CHANNEL_USERNAME))
            except: pass
            running_clients.append(bot)
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {identifier}: {e}")

# --- نقطة الانطلاق ---
async def main():
    logger.info("--- [ PHOENIX HOSTING SYSTEM v3.0 ] ---")
    
    files = [f for f in os.listdir(CLIENTS_DIR) if f.endswith(".txt")]
    if not files:
        logger.warning("🆕 لم يتم العثور على حسابات. يرجى إدخال البيانات يدوياً:")
        s = input("Session: ").strip()
        t = input("Token: ").strip()
        if s:
            with open(os.path.join(CLIENTS_DIR, "admin.txt"), "w") as f: f.write(f"{s}\n{t}")
            files = ["admin.txt"]
        else: return

    for file in files:
        with open(os.path.join(CLIENTS_DIR, file), "r") as f:
            lines = f.read().splitlines()
            if lines:
                await start_instance(lines[0], lines[1] if len(lines) > 1 else None, file)

    if running_clients:
        logger.info(f"💎 النظام يعمل الآن بـ {len(running_clients)} جلسة نشطة.")
        await asyncio.gather(*[c.run_until_disconnected() for c in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 تم إيقاف المحرك بنجاح.")
