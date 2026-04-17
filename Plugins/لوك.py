    # [ أمر لوك المطور لجلب سجل الاستضافة ]
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك$"))
    async def abood_log_sender(event):
        # تحديد رسالة الحالة بناءً على نوع الحساب
        status_text = "⏳ جاري سحب سجل العمليات من الهوست..."
        try:
            if is_bot: 
                msg = await event.respond(status_text)
            else: 
                await event.edit(status_text)
        except: 
            pass

        # التأكد من مسار ملف السجل الصحيح (تأكد أن الاسم يطابق ملفك)
        log_file = "سجل_الأخطاء.txt" 
        
        if not os.path.exists(log_file):
            error_msg = "⚠️ عذراً عبود، ملف السجل غير موجود حالياً في الهوست."
            return await event.respond(error_msg) if is_bot else await event.edit(error_msg)

        # إنشاء نسخة مؤقتة لتجنب مشاكل الوصول للملف (Invalid file parts)
        temp_log = f"temp_abood_{int(time.time())}.txt"
        try:
            import shutil
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
            if is_bot: await event.respond(err_res)
            else: await event.edit(err_res)
            
        finally:
            # تنظيف الملفات المؤقتة
            if os.path.exists(temp_log):
                os.remove(temp_log)
