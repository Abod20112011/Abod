import random
import time
import asyncio
from telethon import events, functions
import database

# إعدادات ثابتة
StartTime = time.time()
# أضف أيديك هنا أيضاً لضمان التحكم الكامل
PROGS = [6373993992] 

def setup(l313l):
    # --- 1. أمر المطور ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_info(event):
        # صورة المطور
        PIC = "https://files.catbox.moe/k4fxu0.jpg"
        
        cat_caption = (
            "**مطورين سورس فينيكس**\n"
            "✛━━━━━━━━━━━━━✛\n"
            f"**• المطور الأساسي :** @BD_0I\n"
            f"**• قناة السورس :** @lAYAI\n"
            "✛━━━━━━━━━━━━━✛\n"
            "**• النظام :** يعمل الآن بنجاح 🚀"
        )
        
        try:
            await event.client.send_file(
                event.chat_id, 
                PIC, 
                caption=cat_caption, 
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
        except:
            await event.edit(cat_caption)

    # --- 2. نظام التحكم والحظر (تم الإصلاح هنا) ---
    @l313l.on(events.NewMessage(incoming=True))
    async def developer_control(event):
        # التحقق من وجود رد وأن المرسل مطور
        if event.is_reply and event.sender_id in PROGS:
            reply_msg = await event.get_reply_message()
            
            # التأكد من أن الرسالة التي يتم الرد عليها تخصك
            if reply_msg and reply_msg.out:
                
                # جلب أيدي الشخص الذي أرسل الأمر (المطور الذي يريد الحظر)
                user_to_block = event.sender_id 
                
                if event.message.message == "حظر من السورس":
                    # تخزين الحظر بشكل صحيح (يفضل استخدام ID المطور هنا أو منطق مخصص)
                    database.set_config("is_blocked", "yes")
                    await event.reply("**✅ حاضر مطوري، تم تفعيل وضع الحظر العام.**")
                
                elif event.message.message == "الغاء الحظر من السورس":
                    database.set_config("is_blocked", "no")
                    await event.reply("**✅ حاضر مطوري، تم إلغاء وضع الحظر.**")

    # --- 3. منع الاستخدام للمحظورين ---
    @l313l.on(events.NewMessage(outgoing=True))
    async def check_blocked(event):
        # منع الأوامر فقط إذا كان الحظر مفعل
        if database.get_config("is_blocked") == "yes":
            if event.text and event.text.startswith("."):
                # استثناء المطورين من الحظر حتى لو كان الوضع مفعل
                if event.sender_id not in PROGS:
                    await event.edit("**⚠️ عذراً، الحساب محظور من استخدام الأوامر حالياً.**")
                    await asyncio.sleep(3)
                    await event.delete()
                    raise events.StopPropagation
