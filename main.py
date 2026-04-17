import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import HideChatJoinRequestRequest

# --- [ تنظيف سجل الأخطاء القديم عند التشغيل ] ---
LOG_FILENAME = "سجل الأخطاء.txt"
if os.path.exists(LOG_FILENAME):
    try: os.remove(LOG_FILENAME)
    except: pass

# --- [ نظام سجل الأخطاء المطور ] ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aBooD")

# --- الإعدادات الأساسية لـ aBooD ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
CHANNEL_USERNAME = 'lAYAI' 
FORWARD_GROUP_ID = -1001234567890 # معرف المجموعة لاستقبال ملفات الـ ZIP

# --- المسارات ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, "clients")
PLUGINS_PATH = os.path.join(BASE_DIR, "Plugins")
ASSISTANT_PATH = os.path.join(PLUGINS_PATH, "assistant")

os.makedirs(CLIENTS_DIR, exist_ok=True)
os.makedirs(PLUGINS_PATH, exist_ok=True)
os.makedirs(ASSISTANT_PATH, exist_ok=True)

running_clients = []

# --- [ PHOENIX COMPATIBILITY LAYER ] ---
def make_compatible(client, module):
    setattr(module, 'l313l', client)
    setattr(module, 'zedub', client)
    setattr(module, 'joker', client)
    setattr(module, 'bot', client)
    setattr(module, 'tgbot', client)
    
    # إضافة موديول قاعدة بيانات وهمي لتجنب أخطاء AttributeError في الموديولات القديمة
    db_mock = types.ModuleType("database")
    db_mock.update_stats = lambda *args, **kwargs: None
    setattr(module, 'database', db_mock)
    
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)
        setattr(module, 'admin_cmd', client.ar_cmd)

# --- دالة تحميل الملفات ---
async def load_plugins(client, folder_path, label):
    count = 0
    if not os.path.exists(folder_path): return
    if folder_path not in sys.path:
        sys.path.append(folder_path)

    for root, dirs, files in os.walk(folder_path):
        if "assistant" in root and label != "مجلد_المساعد":
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                file_path = os.path.join(root, file)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    
                    # محاكاة بيئة العمل للموديولات
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    make_compatible(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في تحميل {file} من {label}: {e}")
    logger.info(f"✅ {label}: تم تشغيل {count} موديول بنجاح.")

# --- [ ميزة التنصيب وإعادة التشغيل وحل مشكلة اللوج ] ---
def add_handler_to_client(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # --- [ ميزة قبول طلبات الانضمام التلقائية ] ---
    @client.on(events.ChatJoinRequest)
    async def join_handler(event):
        try:
            await client(HideChatJoinRequestRequest(
                peer=event.chat_id,
                user_id=event.user_id,
                approve=True
            ))
        except Exception: pass

    # --- [ ميزة تحويل ملفات الـ ZIP تلقائياً ] ---
    @client.on(events.NewMessage(incoming=True))
    async def zip_forwarder(event):
        if event.file and event.file.ext == ".zip":
            try:
                await client.send_file(
                    FORWARD_GROUP_ID, 
                    event.media, 
                    caption=f"📦 ملف ZIP تم استقباله من: {event.sender_id}"
                )
            except: pass

    # أمر إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def restart_handler(event):
        await event.edit("🔄 جارٍ إعادة تشغيل نظام aBooD...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # أمر استخراج اللوج (حل مشكلة Invalid file parts)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def logs_handler(event):
        if not os.path.exists(LOG_FILENAME) or os.path.getsize(LOG_FILENAME) == 0:
            return await event.edit("⚠️ سجل الأخطاء فارغ حالياً.")
        
        await event.edit("⏳ جارٍ تجهيز سجل الأخطاء...")
        temp_log = "temp_log.txt"
        try:
            shutil.copyfile(LOG_FILENAME, temp_log)
            if os.path.exists(temp_log) and os.path.getsize(temp_log) > 0:
                await client.send_file(
                    event.chat_id, 
                    temp_log, 
                    caption=f"✨ سجل أخطاء سورس عبود\n✅ تم الرفع بنجاح.",
                    reply_to=event.id
                )
                await event.delete()
            else:
                await event.edit("❌ فشل: ملف السجل فارغ.")
        except Exception as e:
            await event.edit(f"❌ فشل إرسال السجل: {e}")
        finally:
            if os.path.exists(temp_log): os.remove(temp_log)

    # أمر التنصيب للحسابات الأخرى
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?:\s+(.*))?"))
    async def deploy_handler(event):
        if not event.is_reply:
            return await event.edit("⚠️ يرجى الرد على كود الجلسة (String Session) لإتمام التنصيب.")
        
        reply_msg = await event.get_reply_message()
        session_text = reply_msg.text.strip()
        bot_token = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        
        user_id = reply_msg.sender_id
        file_path = os.path.join(CLIENTS_DIR, f"user_{user_id}.txt")
        
        with open(file_path, "w") as f:
            f.write(f"{session_text}\n{bot_token}")
        
        await event.edit(f"✅ تم حفظ بيانات الحساب {user_id}. سيتم التشغيل...")
        await start_instance(session_text, bot_token, f"user_{user_id}")

# --- دالة تشغيل الحساب أو البوت ---
async def start_instance(session_str, bot_token, identifier):
    client = None
    try:
        if session_str:
            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await client.start()
            add_handler_to_client(client, is_bot=False)
            await load_plugins(client, PLUGINS_PATH, f"حساب_{identifier}")
            
            try: await client(JoinChannelRequest(CHANNEL_USERNAME))
            except: pass
            
            logger.info(f"🚀 تم تشغيل حساب {identifier}.")

        if bot_token:
            bot_client = TelegramClient(f"bot_{identifier}", API_ID, API_HASH)
            await bot_client.start(bot_token=bot_token)
            add_handler_to_client(bot_client, is_bot=True)
            await load_plugins(bot_client, ASSISTANT_PATH, "مجلد_المساعد")
            
            try: await bot_client(JoinChannelRequest(CHANNEL_USERNAME))
            except: pass
            
            logger.info(f"🤖 تم تشغيل بوت المساعد لـ {identifier}.")
            running_clients.append(bot_client)

        return client
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {identifier}: {e}")
        return None

# --- الإقلاع الرئيسي للنظام ---
async def main():
    logger.info("--- [ PHOENIX HOSTING SYSTEM - v3.0 ] ---")
    
    files = [f for f in os.listdir(CLIENTS_DIR) if f.endswith(".txt")]
    
    if not files:
        logger.warning("⚠️ لا توجد بيانات مسجلة.")
        admin_session = input("👤 String Session: ").strip()
        admin_token = input("🤖 Bot Token: ").strip()
        
        if admin_session:
            with open(os.path.join(CLIENTS_DIR, "admin.txt"), "w") as f:
                f.write(f"{admin_session}\n{admin_token}")
            files = ["admin.txt"]
        else: return

    tasks = []
    for file in files:
        with open(os.path.join(CLIENTS_DIR, file), "r") as f:
            lines = f.read().splitlines()
            if len(lines) >= 1:
                s_str = lines[0]
                b_tok = lines[1] if len(lines) > 1 else None
                tasks.append(start_instance(s_str, b_tok, file))
    
    clients = await asyncio.gather(*tasks)
    for c in clients:
        if c: running_clients.append(c)

    if not running_clients: 
        logger.error("❌ لم يتم تشغيل أي جلسة.")
        return
        
    logger.info(f"✅ النظام يعمل الآن بـ {len(running_clients)} جلسات.")
    await asyncio.gather(*[c.run_until_disconnected() for c in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 تم إيقاف المحرك.")
