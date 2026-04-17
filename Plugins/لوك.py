import os
import time
import shutil
from telethon import events

# تصحيح الاستيراد المباشر بدلاً من الاستيراد النسبي (.)
try:
    from . import l313l, Config
except (ImportError, ValueError):
    # إذا فشل الاستيراد النسبي، نسحب العميل من المسار الأعلى (طريقة سورس ويكا/فينيكس)
    try:
        from .. import l313l, Config
    except:
        # حل أخير لضمان التشغيل
        import l313l
        import Config

# إعدادات المطور
client = l313l
name = "aBooD"

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
async def abood_log_sender(event):
    # السجل يقرأ ملف "سجل_الأخطاء.txt" أو "bot.log" حسب تسميتك له في الهوست
    log_file = "سجل_الأخطاء.txt" 
    
    if not os.path.exists(log_file):
        return await event.edit("⚠️ ملف السجل غير موجود بعد.")

    await event.edit("⏳ جاري سحب السجل...")
    temp_log = f"temp_log_{int(time.time())}.txt"
    
    try:
        shutil.copy2(log_file, temp_log)
        await client.send_file(
            event.chat_id,
            temp_log,
            caption=f"📊 سجل الهوست للمطور {name}",
            reply_to=event.id
        )
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ خطأ: {str(e)}")
    finally:
        if os.path.exists(temp_log):
            os.remove(temp_log)
