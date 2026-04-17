import os
import time
import shutil
from telethon import events

# مسار اللوج المحدد في main.py
LOG_FILE = "سجل_الأخطاء.txt"

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def abood_log_handler(event):
        """سحب سجل العمليات للهوست"""
        if not os.path.exists(LOG_FILE):
            return await event.edit("⚠️ **السجل فارغ حالياً يا عبود.**")
        
        await event.edit("⏳ **جاري تحضير السجل وإرساله...**")
        
        temp_name = f"log_abood_{int(time.time())}.txt"
        try:
            # نسخ الملف لتجنب مشاكل الوصول
            shutil.copy2(LOG_FILE, temp_name)
            me = await client.get_me()
            # جلب اليوزر مع @
            user_tag = f"@{me.username}" if me.username else me.first_name
            
            await client.send_file(
                event.chat_id,
                temp_file=temp_name,
                caption=(
                    f"📊 **سجل أخطاء سورس عبود المطور**\n"
                    f"👤 **المطور:** {user_tag}\n"
                    f"⏰ **الوقت:** `{time.ctime()}`\n"
                    f"💎 **الحالة:** مستقر"
                ),
                reply_to=event.id
            )
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ أثناء سحب اللوك:**\n`{e}`")
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تصفير اللوك$"))
    async def clear_log(event):
        """مسح محتويات ملف السجل"""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(f"📊 تم تصفير السجل بواسطة عبود | {time.ctime()}\n")
            await event.edit("✅ **تم تصفير سجل الأخطاء بنجاح.**")
        else:
            await event.edit("⚠️ **لا يوجد ملف سجل لحذفه.**")

# موديول اللوك v8.0 - خاص بسورس عبود 🩵
