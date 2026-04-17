import os
import time
import shutil
from telethon import events
from . import l313l # استدعاء العميل الأساسي من السورس

# تعريف المتغيرات إذا لم تكن موجودة في ملف الإعدادات
name = "aBooD" # اسم المطور كما في السجل
client = l313l # العميل المستخدم في سورس ويكا/فينيكس
is_bot = False # اجعله True إذا كنت تستخدم توكن بوت

# [ أمر لوك المطور لجلب سجل الاستضافة ]
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
async def abood_log_sender(event):
    # تحديد رسالة الحالة
    status_text = "⏳ جاري سحب سجل العمليات من الهوست..."
    try:
        if is_bot: 
            msg = await event.respond(status_text)
        else: 
            await event.edit(status_text)
    except: 
        pass

    # التأكد من مسار ملف السجل الصحيح
    # ملاحظة: تأكد أن ملف السجل في الهوست اسمه "سجل_الأخطاء.txt" فعلاً
    log_file = "سجل_الأخطاء.txt" 
    
    if not os.path.exists(log_file):
        error_msg = "⚠️ عذراً عبود، ملف السجل غير موجود حالياً في الهوست."
        if is_bot:
            return await event.respond(error_msg)
        else:
            return await event.edit(error_msg)

    # إنشاء نسخة مؤقتة لتجنب مشاكل الوصول للملف
    temp_log = f"temp_abood_{int(time.time())}.txt"
    try:
        shutil.copy2(log_file, temp_log)
        
        # إرسال الملف إلى التليجرام
        await client.send_file(
            event.chat_id,
            temp_log,
            caption=f"📊 **سجل عمليات السورس (الهوست)**\n👤 **المطور:** {name}",
            reply_to=event.id
        )
        
        # حذف رسالة الانتظار في حساب المستخدم
        if not is_bot: 
            await event.delete()
            
    except Exception as e:
        err_res = f"❌ فشل إرسال السجل: {str(e)}"
        if is_bot: 
            await event.respond(err_res)
        else: 
            await event.edit(err_res)
            
    finally:
        # تنظيف الملفات المؤقتة من الهوست
        if os.path.exists(temp_log):
            os.remove(temp_log)
