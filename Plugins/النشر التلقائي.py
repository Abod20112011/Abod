import asyncio
from telethon import events
import database

# قاموس لحفظ العمليات الشغالة لإيقافها
RUNNING_POSTS = {}

def setup(l313l):
    # --- 1. النشر التلقائي في جميع المجموعات ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر_كروبات (\d+)(.*)"))
    async def post_to_all(event):
        database.update_stats("نشر_كروبات")
        time_val = int(event.pattern_match.group(1))
        custom_msg = event.pattern_match.group(2).strip()
        reply = await event.get_reply_message()
        
        if not reply and not custom_msg:
            return await event.edit("**⚠️ رد على رسالة أو اكتب نصاً مع الأمر!**")

        RUNNING_POSTS["GLOBAL"] = True
        await event.edit(f"🚀 **بدأ النشر التلقائي في جميع الكروبات كل `{time_val}` ثانية.**\n🚫 لإيقاف كل شيء أرسل `.ايقاف النشر`")

        try:
            while "GLOBAL" in RUNNING_POSTS:
                done, error = 0, 0
                async for dialog in l313l.iter_dialogs():
                    if dialog.is_group:
                        try:
                            if reply: await l313l.send_message(dialog.id, reply)
                            else: await l313l.send_message(dialog.id, custom_msg)
                            done += 1
                        except: error += 1
                await asyncio.sleep(time_val)
        except:
            if "GLOBAL" in RUNNING_POSTS: del RUNNING_POSTS["GLOBAL"]

    # --- 2. أمر الإيقاف الشامل ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف النشر$"))
    async def stop_everything(event):
        RUNNING_POSTS.clear()
        await event.edit("🛑 **تم إيقاف جميع عمليات النشر والإذاعة الجارية.**")

    # --- 3. أمر (وجه) للإذاعة في المجموعات فقط بالرد ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.وجه$"))
    async def gcast(event):
        reply = await event.get_reply_message()
        if not reply: return await event.edit("**⚠️ يجب الرد على رسالة للتوجيه!**")
        
        await event.edit("**᯽︙ جاري التوجيه للمجموعات...**")
        done, error = 0, 0
        async for dialog in l313l.iter_dialogs():
            if dialog.is_group:
                try:
                    await l313l.forward_messages(dialog.id, reply)
                    done += 1
                except: error += 1
        await event.edit(f"✅ **اكتمل التوجيه:**\n• مجموعات: `{done}`\n• فشل: `{error}`")

    # --- 4. أمر (حول) للإذاعة في الخاص فقط بالرد ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.حول$"))
    async def gucast(event):
        reply = await event.get_reply_message()
        if not reply: return await event.edit("**⚠️ يجب الرد على رسالة للتحويل!**")
        
        await event.edit("**᯽︙ جاري التحويل للخاص...**")
        done, error = 0, 0
        async for dialog in l313l.iter_dialogs():
            if dialog.is_user and not dialog.entity.bot:
                try:
                    await l313l.forward_messages(dialog.id, reply)
                    done += 1
                except: error += 1
        await event.edit(f"✅ **اكتمل التحويل للخاص:**\n• مستخدمين: `{done}`\n• فشل: `{error}`")

    # --- 5. أمر (توجيه) للكل (خاص ومجموعات) ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.توجيه$"))
    async def cast_all(event):
        reply = await event.get_reply_message()
        if not reply: return await event.edit("**⚠️ يجب الرد على رسالة!**")
        
        await event.edit("**᯽︙ جاري التوجيه للجميع...**")
        done, error = 0, 0
        async for dialog in l313l.iter_dialogs():
            try:
                await l313l.forward_messages(dialog.id, reply)
                done += 1
            except: error += 1
        await event.edit(f"✅ **تم التوجيه لـ `{done}` من المحادثات.**")
