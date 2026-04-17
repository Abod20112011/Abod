import os
import zipfile
import sys
import asyncio
from telethon import events

# إعدادات القناة والملفات
UPDATE_CHANNEL = "vsouer"  # تم التغيير إلى معرف قناتك الجديد
LAST_UPDATE_FILE = "last_update.txt"

def get_last_saved_id():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as f:
            return f.read().strip()
    return "0"

def save_last_id(message_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(message_id))

def restart_host():
    # إعادة تشغيل السورس لتطبيق التحديثات
    python = sys.executable
    os.execl(python, python, *sys.argv)

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث$"))
    async def smart_update(event):
        await event.edit("🔍 **جاري فحص التحديثات من قناة السورس...**")
        
        try:
            # جلب آخر رسالة من القناة المحددة
            async for message in client.iter_messages(UPDATE_CHANNEL, limit=1):
                # التأكد من وجود ملف مضغوط
                if not message.file or not message.file.name.endswith(".zip"):
                    return await event.edit("⚠️ **لم يتم العثور على تحديث (ملف ZIP) في القناة.**")

                # التحقق إذا كان التحديث مُثبتاً مسبقاً
                if str(message.id) == get_last_saved_id():
                    return await event.edit("✅ **سورسك يعمل على آخر إصدار متوفر بالفعل.**")

                await event.edit("📥 **تم العثور على إصدار جديد! جاري التحميل...**")
                
                # تحميل الملف
                zip_path = await client.download_media(message)
                
                await event.edit("📦 **جاري فك الضغط واستبدال الملفات القديمة...**")
                
                # استخراج الملفات واستبدال الموجود
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.getcwd())

                # حفظ رقم التحديث وحذف الملف المؤقت
                save_last_id(message.id)
                if os.path.exists(zip_path):
                    os.remove(zip_path)

                await event.edit("✨ **تم تحديث السورس بنجاح! جاري إعادة التشغيل الآن...**")
                await asyncio.sleep(2)
                restart_host()

        except Exception as e:
            await event.edit(f"❌ **فشل التحديث بسبب خطأ فني:**\n`{str(e)}`")

    print(f"✅ تم تحميل موديول التحديث بنجاح (القناة: {UPDATE_CHANNEL})")
