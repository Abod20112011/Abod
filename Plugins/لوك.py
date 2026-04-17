import os
import asyncio
from telethon import events

# اسم ملف السجل الذي حددناه في main.py
LOG_FILE = "سجل الأخطاء.txt"

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def get_log_file(event):
        await event.edit("**✧︙ جـاري جـلب سـجل الأخطاء وحـذفه...**")
        
        if os.path.exists(LOG_FILE):
            try:
                # إرسال الملف
                await event.client.send_file(
                    event.chat_id,
                    LOG_FILE,
                    caption="**✧︙ سـجل الأخطاء لـسورس عـبود (تـم الـحذف بعد الإرسال) ✅**",
                    reply_to=event.id
                )
                await event.delete()
                
                # حذف الملف فوراً بعد الإرسال كما طلبت
                os.remove(LOG_FILE)
                # إعادة إنشاء ملف فارغ لاستكمال التسجيل
                open(LOG_FILE, 'a').close() 
                
            except Exception as e:
                await event.edit(f"**❌ فشل التعامل مع السجل:**\n`{str(e)}`")
        else:
            await event.edit("**❌ لا يـوجد ملف سجل (سجل الأخطاء.txt) حـالياً.**")

    print("✅ تم تحميل موديول سجل الأخطاء الذكي.")
