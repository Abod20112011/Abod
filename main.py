import os, sys, asyncio, importlib.util, subprocess, types, logging
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

# --- [ نظام سجل الأخطاء المطور ] ---
LOG_FILENAME = " @BD_0I  -  aBooD.py"
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

# --- المسارات ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, "clients")
PLUGINS_PATH = os.path.join(BASE_DIR, "Plugins")
ASSISTANT_PATH = os.path.join(PLUGINS_PATH, "assistant") # مسار مجلد المساعد الجديد

os.makedirs(CLIENTS_DIR, exist_ok=True)
os.makedirs(PLUGINS_PATH, exist_ok=True)

running_clients = []

# --- [ PHOENIX COMPATIBILITY LAYER ] ---
def make_compatible(client, module):
    """حقن الوظائف اللازمة لتشغيل ملفات من سورسات مختلفة"""
    setattr(module, 'l313l', client)
    setattr(module, 'zedub', client)
    setattr(module, 'joker', client)
    setattr(module, 'bot', client)
    setattr(module, 'tgbot', client) # دعم إضافي لبوت التوكن
    
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)
        setattr(module, 'admin_cmd', client.ar_cmd)

# --- دالة تحميل الملفات (المطورة لدعم المجلدات الفرعية) ---
async def load_plugins(client, folder_path, label):
    count = 0
    if not os.path.exists(folder_path): return
    
    if folder_path not in sys.path:
        sys.path.append(folder_path)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                file_path = os.path.join(root, file)
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    
                    # محاكاة سورس JoKeRUB للتوافق
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

# --- إضافة وظيفة ar_cmd للمحرك ---
def add_handler_to_client(client, is_bot=False):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        # البوت يستجيب للجميع، المستخدم يستجيب لنفسه فقط
        return client.on(events.NewMessage(outgoing=not is_bot, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

# --- دالة تشغيل الحساب أو البوت ---
async def start_instance(session_str, bot_token, identifier):
    client = None
    try:
        # 1. تشغيل حساب المستخدم (Userbot)
        if session_str:
            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await client.start()
            add_handler_to_client(client, is_bot=False)
            await load_plugins(client, PLUGINS_PATH, f"حساب_{identifier}")
            logger.info(f"🚀 تم تشغيل حساب المطور بنجاح.")

        # 2. تشغيل بوت المساعد (Assistant) إذا وجد توكن
        if bot_token:
            bot_client = TelegramClient(f"bot_{identifier}", API_ID, API_HASH)
            await bot_client.start(bot_token=bot_token)
            add_handler_to_client(bot_client, is_bot=True)
            # تحميل ملفات مجلد assistant حصراً للبوت
            await load_plugins(bot_client, ASSISTANT_PATH, "مجلد_المساعد")
            logger.info(f"🤖 تم تشغيل بوت المساعد بنجاح.")
            running_clients.append(bot_client)

        try:
            await client(JoinChannelRequest(CHANNEL_USERNAME))
        except: pass
        
        return client
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {identifier}: {e}")
        return None

# --- الإقلاع الرئيسي للنظام ---
async def main():
    logger.info("--- [ PHOENIX HOSTING SYSTEM - v3.0 ] ---")
    logger.info("🛡️ طبقة التوافق الشاملة مفعلة (دعم المساعد).")
    
    files = [f for f in os.listdir(CLIENTS_DIR) if f.endswith(".txt")]
    
    if not files:
        logger.error("❌ لا توجد ملفات حسابات في مجلد clients.")
        return

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
        logger.error("❌ لم ينجح تشغيل أي جلسة.")
        return
        
    logger.info(f"✅ النظام يعمل الآن بـ {len(running_clients)} جلسات (حسابات + بوتات).")
    await asyncio.gather(*[c.run_until_disconnected() for c in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 تم إيقاف المحرك.")
