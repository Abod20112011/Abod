# -*- coding: utf-8 -*-
# ملف اللوك - مخصص للعمل مع المساعد في سورس عبود v6.5
import os
import time
import shutil
from telethon import events

# نظام الاستدعاء المتوافق مع محرك التشغيل المحقون
try:
    import l313l
    # سحب العميل من داخل الموديول لضمان عمل getattr و on
    client = l313l.l313l 
except Exception:
    # حل احتياطي في حال تم التشغيل خارج نظام المساعد
    try:
        from .. import l313l as client
    except:
        import l313l as client

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
async def abood_log_sender(event):
    # المسار الصحيح للسجل حسب ملف التشغيل الخاص بك
    log_file = "سجل_الأخطاء.txt" 
    
    if not os.path.exists(log_file):
        return await event.edit("⚠️ **السجل غير موجود حالياً يا عبود.**")

    await event.edit("⏳ **جاري جلب سجل الهوست...**")
    
    # نسخة مؤقتة لتفادي خطأ "الملف قيد الاستخدام"
    temp_log = f"log_fix_{int(time.time())}.txt"
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
        await event.edit(f"❌ **فشل الإرسال:** `{str(e)}`")
    finally:
        if os.path.exists(temp_log):
            os.remove(temp_log)
