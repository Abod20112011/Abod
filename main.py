import os, sys, asyncio, importlib.util, subprocess, types, logging
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

# --- [ نظام سجل الأخطاء المطور ] ---
LOG_FILENAME = "سجل الأخطاء.txt"
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
    
    if hasattr(client, 'ar_cmd'):
        setattr(module, 'ar_cmd', client.ar_cmd)
        setattr(module, 'zed_cmd', client.ar_cmd)
        setattr(module, 'admin_cmd', client.ar_cmd)

# --- دالة تحميل الملفات (المطورة 100%) ---
async def load_plugins(client, label):
    count = 0
    if not os.path.exists(PLUGINS_PATH): return
    
    if PLUGINS_PATH not in sys.path:
        sys.path.append(PLUGINS_PATH)
        sys.path.append(BASE_DIR)

    for file in os.listdir(PLUGINS_PATH):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = file[:-3]
            file_path = os.path.join(PLUGINS_PATH, file)
            
            try:
                if "JoKeRUB" not in sys.modules:
                    mock_joker = types.ModuleType("JoKeRUB")
                    mock_joker.l313l = client
                    sys.modules["JoKeRUB"] = mock_joker
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                
                make_compatible(client, module)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'setup'):
                    module.setup(client)
                
                count += 1
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل {file}: {e}") # تسجيل الخطأ في الملف
                
    logger.info(f"✅ {label}: تم تشغيل {count} موديول بنجاح.")

# --- إضافة وظيفة ar_cmd للمحرك (Universal Handler) ---
def add_handler_to_client(client):
    def ar_cmd(pattern=None, **kwargs):
        if pattern and not pattern.startswith(("^", "\\", "/")):
            pattern = f"^\\.{pattern}"
        return client.on(events.NewMessage(outgoing=True, pattern=pattern, **kwargs))
    
    client.ar_cmd = ar_cmd

# --- دالة تشغيل الحساب ---
async def start_instance(session_str, bot_token, identifier):
    try:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.start()
        
        add_handler_to_client(client)
        await load_plugins(client, f"الحساب_{identifier}")
        
        try:
            await client(JoinChannelRequest(CHANNEL_USERNAME))
        except: pass
        
        me = await client.get_me()
        logger.info(f"🚀 تم تشغيل سورس aBooD بنجاح: {me.first_name}")
        return client
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {identifier}: {e}")
        return None

# --- الإقلاع الرئيسي للنظام ---
async def main():
    logger.info("--- [ PHOENIX HOSTING SYSTEM - v3.0 ] ---")
    logger.info("🛡️ طبقة التوافق الشاملة مفعلة الآن.")
    
    if not os.path.exists(CLIENTS_DIR):
        os.makedirs(CLIENTS_DIR)

    files = [f for f in os.listdir(CLIENTS_DIR) if f.endswith(".txt")]
    
    if not files:
        logger.warning("📥 يرجى إدخال بيانات المطور في الكونسول:")
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
                tasks.append(start_instance(lines[0], lines[1] if len(lines)>1 else "", file))
    
    clients = await asyncio.gather(*tasks)
    global running_clients
    running_clients = [c for c in clients if c]

    if not running_clients: 
        logger.error("❌ لم ينجح تشغيل أي حساب.")
        return
        
    logger.info(f"\n✅ النظام يعمل الآن بـ {len(running_clients)} مستخدمين.")
    await asyncio.gather(*[c.run_until_disconnected() for c in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n👋 تم إيقاف المحرك.")
