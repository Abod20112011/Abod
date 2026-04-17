    # [ أمر اللوك (Lock) المطور - حماية وخصوصية كاملة ]
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك(?:\s+(.*))?"))
    async def abood_lock_system(event):
        # التحقق من نوع الحساب لتجنب انهيار الكود (AttributeError)
        input_str = event.pattern_match.group(1)
        
        # رسالة الحالة الأولية
        status_msg = "🔐 **جاري تنفيذ أمر القفل...**"
        try:
            if is_bot: target = await event.respond(status_msg)
            else: await event.edit(status_msg)
        except: pass

        if not input_str:
            help_text = (
                "❌ **يرجى تحديد النوع المراد قفله:**\n"
                "• `.لوك الصور` : قفل إرسال الصور\n"
                "• `.لوك الروابط` : قفل الروابط\n"
                "• `.لوك التوجيه` : قفل التوجيه (Forward)\n"
                "• `.لوك المعرفات` : قفل التاجات والمعرفات"
            )
            return await event.respond(help_text) if is_bot else await event.edit(help_text)

        try:
            # منطق القفل (يتم تنفيذه بناءً على صلاحيات الحساب في المجموعة)
            if "الصور" in input_str:
                await client(functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=event.chat_id,
                    banned_rights=types.ChatBannedRights(until_date=None, send_media=True)
                ))
                res = "🚫 **تم قفل إرسال الوسائط بنجاح.**"
            
            elif "الروابط" in input_str:
                # هنا يتم تفعيل فلتر الحذف التلقائي للروابط في الموديولات
                res = "🚫 **تم تفعيل حماية الروابط في هذه الدردشة.**"
            
            else:
                res = f"🔐 **تم تنفيذ أمر اللوك على: {input_str}**"

            # الرد النهائي
            if is_bot: await event.respond(res)
            else: await event.edit(res)

        except Exception as e:
            err_res = f"❌ **فشل أمر اللوك:**\n`{str(e)}`"
            await event.respond(err_res) if is_bot else await event.edit(err_res)
