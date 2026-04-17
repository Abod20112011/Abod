# -*- coding: utf-8 -*-
# ملف الستارت - سورس عبود المطور
from telethon import events, Button

try:
    import l313l
    client = l313l.l313l
except Exception:
    from .. import l313l as client

@client.on(events.NewMessage(pattern="/start", incoming=True))
async def bot_start(event):
    if event.is_private:
        # جلب الاسم بشكل آمن
        try:
            sender = await event.get_sender()
            name = sender.first_name if sender else "عبود"
        except:
            name = "عبود"
            
        msg = f"**مرحباً بك عزيـزي {name} ✨**\n\n"
        msg += "أنا البوت المساعد الخاص بـ **سورس عبود**\n"
        msg += "البوت يعمل الآن بنجاح ✅"
        
        buttons = [
            [Button.url("🧑🏻‍💻 قـناة المـطور", url="https://t.me/aqhvv")],
            [Button.url("💬 مراسـلة المـطور", url="https://t.me/BD_0I")]
        ]
        
        await event.reply(msg, buttons=buttons)
