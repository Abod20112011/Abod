# -*- coding: utf-8 -*-
# ملف أمر اللوك - سورس عبود المطور
import os
import time
import shutil
from telethon import events

# استدعاء العميل بأكثر من طريقة لضمان التشغيل
try:
    from .. import l313l
except:
    try:
        import l313l
    except:
        from zthon import l313l

client = l313l

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
async def abood_log_sender(event):
    # اسم ملف السجل في الهوست
    log_file = "سجل_الأخطاء.txt" 
    
    if not os.path.exists(log_file):
        return await event.edit("⚠️ **عذراً، ملف السجل غير موجود حالياً.**")

    await event.edit("⏳ **جاري جلب السجل من الهوست...**")
    
    # نسخة مؤقتة لتجنب مشاكل القفل
    temp_log = f"log_{int(time.time())}.txt"
    try:
        shutil.copy2(log_file, temp_log)
        await client.send_file(
            event.chat_id,
            temp_log,
            caption=f"📊 **سجل عمليات الهوست**\n👤 **المطور:** عبود",
            reply_to=event.id
        )
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **فشل الإرسال:**\n`{str(e)}`")
    finally:
        if os.path.exists(temp_log):
            os.remove(temp_log)
