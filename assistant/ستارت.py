# -*- coding: utf-8 -*-
# ملف أمر الستارت - سورس عبود المطور
from telethon import events, Button

try:
    from .. import l313l
except:
    try:
        import l313l
    except:
        from zthon import l313l

client = l313l

@client.on(events.NewMessage(pattern="/start", incoming=True))
async def bot_start(event):
    # نتحقق أن الرسالة في الخاص فقط
    if event.is_private:
        name = (await event.get_sender()).first_name
        msg = f"**مرحباً بك عزيـزي {name} ✨**\n\n"
        msg += "أنا البوت المساعد الخاص بـ **سورس عبود**\n"
        msg += "يمكنك التواصل مع المطور أو استخدام الخدمات بالأسفل."
        
        buttons = [
            [Button.url("🧑🏻‍💻 قـناة المـطور", url="https://t.me/aqhvv")],
            [Button.url("💬 مراسـلة المـطور", url="https://t.me/BD_0I")]
        ]
        
        await event.reply(msg, buttons=buttons)

