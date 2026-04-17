import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام التحديث الإجباري للمكتبات ] ---
def update_environment():
    try:
        print("🛠️ جاري فحص وتحديث المكتبات الأساسية لضمان أعلى أداء...")
        # تحديث المكتبات في مجلد المستخدم لتجنب قيود الاستضافة
        libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "bs4"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + libs)
    except Exception as e:
        print(f"⚠️ فشل التحديث التلقائي (سيتم استخدام الإصدارات الحالية): {e}")

update_environment()

from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession

# معالجة أخطاء الاستيراد (ChatJoinRequest) التي ظهرت في صورك
try:
    from telethon.tl.types import UpdateBotChatJoinRequest, UpdateChatJoinRequest
    from telethon.tl.functions.messages import HideChatJoinRequestRequest
    JOIN_SUPPORTED = True
except ImportError:
    JOIN_SUPPORTED = False
    print("⚠️ تحذير: الإصدار الحالي لا يدعم ميزة الانضمام التلقائي مباشرة.")

# --- [ 2. إعدادات سجل الأخطاء (Log) - حل مشكلة الـ Invalid Parts ] ---
LOG_FILE = "سجل_الأخطاء.txt"

def initialize_master_logger():
    # تصفير الملف عند التشغيل لحل مشكلة التعليق في الاستضافة
    if os.path.exists(LOG_FILE):
        try: os.remove(LOG_FILE)
        except: pass
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"🚀 سورس عبود - بدء التشغيل: {time.ctime()}\n")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ABOOD_MASTER")

logger = initialize_master_logger()

# --- [ 3. البيانات الأساسية - الثوابت ] ---
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992
CHANNEL_LINK = 'lAYAI' 
ZIP_FORWARD_GROUP = -1001234567890 

# إنشاء المجلدات الضرورية
BASE_PATH = os.getcwd()
DIRECTORIES = ["clients", "Plugins", "Plugins/assistant"]
for folder in DIRECTORIES:
    os.makedirs(os.path.join(BASE_PATH, folder), exist_ok=True)

all_active_clients = []

# --- [ 4. موديول التوافق (Compatibility Layer) ] ---
def make_modules_compatible(client, module):
    # ربط جميع الأسماء البرمجية الشائعة لضمان عمل الموديولات الخارجية
    aliases = ['l313l', 'zedub', 'joker', 'bot', 'tgbot', 'ph_bot']
    for alias in aliases:
        setattr(module, alias, client)
    
    # حل مشكلة AttributeError: database (ظاهرة في صورك)
    if not hasattr(module, 'database'):
        mock_db = types.ModuleType("database")
        mock_db.update_stats = lambda *args, **kwargs: None
        mock_db.get_db = lambda *args, **kwargs: None
        setattr(module, 'database', mock_db)

    # ربط الفلاتر الخاصة بالأوامر
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)

# --- [ 5. محرك تحميل الموديولات (Plugins Engine) ] ---
async def load_plugins_from_folder(client, folder_name, tag):
    count = 0
    full_folder_path = os.path.join(BASE_PATH, folder_name)
    if not os.path.exists(full_folder_path): return
    if full_folder_path not in sys.path:
        sys.path.append(full_folder_path)

    for root, dirs, files in os.walk(full_folder_path):
        # منع تحميل موديولات المساعد داخل الحسابات العادية
        if "assistant" in root and tag != "مساعد":
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    
                    # بيئة عمل PHOENIX
                    if "JoKeRUB" not in sys.modules:
                        sys.modules["JoKeRUB"] = types.ModuleType("JoKeRUB")
                    sys.modules["JoKeRUB"].l313l = client
                    
                    make_modules_compatible(client, module)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'setup'):
                        module.setup(client)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في تحميل {file} [{tag}]: {e}")
    
    logger.info(f"✅ {tag}: تم تشغيل {count} موديول بنجاح.")

# --- [ 6. معالج الأحداث والأوامر الأساسية ] ---
def initialize_handlers(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

    # [أ] ميزة قبول طلبات الانضمام (نسخة الحماية)
    @client.on(events.Raw)
    async def join_request_handler(update):
        if JOIN_SUPPORTED and isinstance(update, (UpdateBotChatJoinRequest, UpdateChatJoinRequest)):
            try:
                peer = update.peer if hasattr(update, 'peer') else update.chat_id
                await client(HideChatJoinRequestRequest(peer=peer, user_id=update.user_id, approve=True))
            except: pass

    # [ب] ميزة تحويل ملفات الـ ZIP تلقائياً
    @client.on(events.NewMessage(incoming=True))
    async def zip_auto_forward(event):
        if event.file and event.file.ext == ".zip":
            try:
                await client.send_file(ZIP_FORWARD_GROUP, event.media, caption=f"📦 ملف ZIP جديد\n👤 المرسل: `{event.sender_id}`")
            except: pass

    # [ج] أمر اللوج (حل مشكلة الـ Invalid parts)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوج$"))
    async def logs_sender(event):
        await event.edit("⏳ جاري سحب سجل العمليات من السيرفر...")
        if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) < 10:
            return await event.edit("⚠️ السجل فارغ حالياً.")
        
        # استخدام ملف مؤقت لتجنب قفل الملف الأصلي
        temp_log_name = f"log_{int(time.time())}.txt"
        try:
            shutil.copy2(LOG_FILE, temp_log_name)
            await client.send_file(event.chat_id, temp_log_name, caption="📊 سجل أخطاء سورس عبود المطور")
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ فشل إرسال السجل: {e}")
        finally:
            if os.path.exists(temp_log_name): os.remove(temp_log_name)

    # [د] أمر إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def restart_system(event):
        await event.edit("♻️ جاري إعادة تشغيل النظام وتحديث البيئة...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # [هـ] ميزة التنصيب السريع
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?:\s+(.*))?"))
    async def install_account(event):
        if not event.is_reply:
            return await event.edit("⚠️ يرجى الرد على كود الجلسة (Session).")
        
        reply_msg = await event.get_reply_message()
        session_str = reply_msg.text.strip()
        bot_token = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""
        
        user_id = reply_msg.sender_id
        file_path = os.path.join(BASE_PATH, f"clients/user_{user_id}.txt")
        
        with open(file_path, "w") as f:
            f.write(f"{session_str}\n{bot_token}")
        
        await event.edit(f"✅ تم حفظ البيانات. جاري محاولة تشغيل الحساب {user_id}...")
        await start_new_instance(session_str, bot_token, f"user_{user_id}")

# --- [ 7. مشغل الجلسات ] ---
async def start_new_instance(session, token, name):
    try:
        if session:
            client = TelegramClient(StringSession(session), API_ID, API_HASH)
            await client.start()
            initialize_handlers(client)
            await load_plugins_from_folder(client, "Plugins", f"حساب_{name}")
            try: await client(JoinChannelRequest(CHANNEL_LINK))
            except: pass
            all_active_clients.append(client)
            logger.info(f"🚀 تم تشغيل الحساب: {name}")

        if token:
            bot = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await bot.start(bot_token=token)
            initialize_handlers(bot, is_bot=True)
            await load_plugins_from_folder(bot, "Plugins/assistant", "مساعد")
            all_active_clients.append(bot)
    except Exception as e:
        logger.error(f"❌ فشل تشغيل الجلسة {name}: {e}")

# --- [ 8. الإقلاع الرئيسي (Main) ] ---
async def main():
    logger.info("--- [ PHOENIX HOSTING v5.0 - ABOOD ] ---")
    
    # البحث عن ملفات الجلسات في مجلد clients
    client_files = [f for f in os.listdir("clients") if f.endswith(".txt")]
    
    if not client_files:
        print("🆕 لا توجد حسابات مضافة. يرجى إدخال البيانات:")
        s = input("Session String: ").strip()
        t = input("Bot Token: ").strip()
        if s:
            with open("clients/admin.txt", "w") as f: f.write(f"{s}\n{t}")
            client_files = ["admin.txt"]
        else: return

    for file in client_files:
        with open(f"clients/{file}", "r") as f:
            lines = f.read().splitlines()
            if lines:
                await start_new_instance(lines[0], lines[1] if len(lines) > 1 else None, file)

    if all_active_clients:
        logger.info(f"💎 النظام يعمل الآن بـ {len(all_active_clients)} جلسة نشطة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in all_active_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 تم إيقاف النظام.")
