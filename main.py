# -*- coding: utf-8 -*-
import os, sys, asyncio, importlib.util, subprocess, types, logging, shutil, time

# --- [ 1. نظام تحديث البيئة وتثبيت المتطلبات ] ---
def setup_environment():
    try:
        print("🛠️ جاري فحص وتحديث مكتبات السورس لضمان أعلى أداء...")
        # إضافة المكتبات اللازمة للـ Inline وقاعدة البيانات
        required_libs = ["telethon==1.31.0", "pytz", "pydantic", "aiohttp", "requests", "bs4", "aiosqlite"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + required_libs)
    except Exception as e:
        print(f"⚠️ تنبيه: فشل التحديث التلقائي للمكتبات: {e}")

setup_environment()

from telethon import TelegramClient, events, functions, types as tg_types
from telethon.sessions import StringSession

# --- [ 2. إعدادات السجل والبيانات ] ---
LOG_FILE_PATH = "سجل_الأخطاء.txt"
API_ID = 38980666
API_HASH = '561ff5b4953d95c485b17a0bcb121f9c'
OWNER_ID = 6373993992  #

def initialize_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'), logging.StreamHandler()]
    )
    return logging.getLogger("ABOOD_SYSTEM")

logger = initialize_logger()
running_clients = []

# --- [ 3. محرك قاعدة البيانات المبسط ] ---
# يحفظ الجلسات والتوكنات ليعمل السورس تلقائياً عند إعادة التشغيل
DB_PATH = "database_Abod.txt"

def save_to_db(session, token, name):
    with open(f"clients/{name}.txt", "w") as f:
        f.write(f"{session}\n{token}")

# --- [ 4. دوال تفعيل الـ Inline (وضع الأونلاين) ] ---
async def setup_inline_mode(client, bot_username):
    """تفعيل وضع الأونلاين وتلقين بوت فاذر بالأوامر"""
    try:
        joker = "عبود 🩵"
        commands = "start - لبدء البوت\nhack - قسم أوامر الهاك\nhelp - قائمة المساعدة"
        
        logger.info(f"⚙️ جاري محاولة تفعيل الـ Inline لبوت: {bot_username}")
        async with client.conversation("@BotFather") as conv:
            await conv.send_message("/setinline")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(joker)
            
            await conv.send_message("/setcommands")
            await asyncio.sleep(1)
            await conv.send_message(bot_username)
            await asyncio.sleep(1)
            await conv.send_message(commands)
        logger.info("✅ تم تحديث إعدادات الأونلاين والأوامر بنجاح.")
    except Exception as e:
        logger.error(f"⚠️ فشل إعداد الـ Inline: {e}")

# --- [ 5. موديول التوافق وتحميل الموديولات ] ---
def apply_compatibility(client, module, is_bot=False):
    aliases = ['l313l', 'bot', 'tgbot', 'ph_bot', 'zedthon']
    for alias in aliases:
        setattr(module, alias, client)
    # حقن كود المساعد ليعمل داخل الموديولات
    if is_bot:
        setattr(client, 'tgbot', client)

async def start_plugins_engine(client, folder_name, label, is_bot=False):
    count = 0
    full_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(full_path): return
    if full_path not in sys.path: sys.path.append(full_path)

    # كسر خطأ الاستيراد لـ l313l
    if "l313l" not in sys.modules:
        mock = types.ModuleType("l313l")
        mock.l313l = client
        sys.modules["l313l"] = mock

    for root, _, files in os.walk(full_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                try:
                    mod_name = file[:-3]
                    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(root, file))
                    module = importlib.util.module_from_spec(spec)
                    apply_compatibility(client, module, is_bot)
                    spec.loader.exec_module(module)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ خطأ في {file}: {e}")
    logger.info(f"✨ {label}: تم تشغيل {count} موديول.")

# --- [ 6. معالجة الأوامر الأساسية للتحكم ] ---
def setup_handlers(client, is_bot=False):
    
    # 1. أمر إعادة التشغيل
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة تشغيل$"))
    async def reboot(event):
        if event.sender_id != OWNER_ID: return
        await event.edit("♻️ **جاري إعادة تشغيل السورس بالكامل...**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # 2. أمر تحديث المكتبات
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث المكاتب$"))
    async def update_libs(event):
        await event.edit("📦 **جاري تحديث جميع المكتبات، قد يستغرق الأمر دقيقة...**")
        setup_environment()
        await event.edit("✅ **تم تحديث المكتبات بنجاح! سأقوم بإعادة التشغيل الآن..**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # 3. أمر التنصيب لشخص آخر (بالرد على ملف)
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنصيب(?P<id> \d+)?$"))
    async def install_other(event):
        if not event.is_reply:
            return await event.edit("⚠️ **يجب الرد على ملف نصي يحتوي على (الجلسة ثم التوكن).**")
        
        target_id = event.pattern_match.group('id')
        reply_msg = await event.get_reply_message()
        
        if reply_msg.file:
            path = await reply_msg.download_media("clients/temp_setup.txt")
            with open(path, "r") as f:
                data = f.read().splitlines()
            
            if len(data) >= 2:
                new_name = target_id.strip() if target_id else "new_user"
                save_to_db(data[0], data[1], new_name)
                await event.edit(f"✅ **تم حفظ بيانات التنصيب لـ {new_name}.**\nسيتم التشغيل عند إعادة التشغيل القادمة.")
            else:
                await event.edit("❌ **الملف المردود عليه لا يحتوي على بيانات كافية.**")

# --- [ 7. مشغل الوحدات ] ---
async def start_instance(s, t, name):
    try:
        # تشغيل حساب المستخدم (UserBot)
        c = TelegramClient(StringSession(s), API_ID, API_HASH)
        await c.start()
        setup_handlers(c)
        await start_plugins_engine(c, "Plugins", f"حساب_{name}")
        running_clients.append(c)

        # تشغيل بوت المساعد (Assistant)
        if t:
            b = TelegramClient(f"bot_{name}", API_ID, API_HASH)
            await b.start(bot_token=t)
            # تفعيل الأونلاين
            me = await b.get_me()
            await setup_inline_mode(c, me.username) 
            await start_plugins_engine(b, "Plugins/assistant", "مساعد", is_bot=True)
            running_clients.append(b)
            
    except Exception as e:
        logger.error(f"❌ فشل تشغيل {name}: {e}")

async def main():
    logger.info("--- [ ABOOD HOSTING v7.0 ] ---")
    if not os.path.exists("clients"): os.makedirs("clients")
    
    # إذا لم توجد ملفات، يطلب الإدخال لأول مرة
    files = [f for f in os.listdir("clients") if f.endswith(".txt")]
    if not files:
        print("👋 أهلاً بك يا عبود في أول تشغيل!")
        s = input("أدخل كود الجلسة (String Session): ")
        t = input("أدخل توكن البوت (Bot Token): ")
        save_to_db(s, t, "admin")
        files = ["admin.txt"]

    for f in files:
        with open(f"clients/{f}", "r") as fl:
            d = fl.read().splitlines()
            if d: await start_instance(d[0], d[1] if len(d)>1 else None, f)

    if running_clients:
        logger.info(f"💎 النظام يعمل بـ {len(running_clients)} وحدة.")
        await asyncio.gather(*[cl.run_until_disconnected() for cl in running_clients])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
