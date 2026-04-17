# -*- coding: utf-8 -*-
# ملف اللوك - سورس عبود المطور
import os
import time
import shutil
from telethon import events

# نظام استدعاء مخصص لسورس فينيكس المعدل
try:
    from .. import l313l
except:
    try:
        from zedthon import l313l # تعديل الاسم من zthon إلى zedthon
    except:
        import l313l

client = l313l

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
async def abood_log_sender(event):
    # التأكد من اسم ملف السجل كما يظهر في صورتك
    log_file = "سجل_الأخطاء.txt" 
    
    if not os.path.exists(log_file):
        return await event.edit("⚠️ **عذراً عبود، ملف السجل غير موجود حالياً.**")

    await event.edit("⏳ **جاري سحب السجل من الهوست...**")
    
    temp_log = f"log_{int(time.time())}.txt"
    try:
        shutil.copy2(log_file, temp_log)
        await client.send_file(
            event.chat_id,
            temp_log,
            caption=f"📊 **سجل عمليات الهوست**\n👤 **المطور:** aBooD",
            reply_to=event.id
        )
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **فشل الإرسال:**\n`{str(e)}`")
    finally:
        if os.path.exists(temp_log):
            os.remove(temp_log)
