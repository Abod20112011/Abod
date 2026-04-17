# -*- coding: utf-8 -*-
# موديول الستارت لبوت المساعد - سورس عبود
from telethon import events, Button

# جلب العميل (البوت) الذي يعمل بالتوكن من ملف التشغيل الأساسي
try:
    import l313l
    client = l313l.l313l
except Exception:
    # حل احتياطي لضمان التعرف على توكن البوت المسجل
    from __main__ import running_clients
    # البحث عن وحدة البوت داخل الوحدات المشغلة
    client = next((c for c in running_clients if c.is_bot()), None)

@client.on(events.NewMessage(pattern="/start", incoming=True))
async def abood_bot_start(event):
    # الرد فقط في الخاص لضمان الخصوصية
    if event.is_private:
        # جلب معلومات المستخدم بشكل آمن
        user = await event.get_sender()
        name = user.first_name if user else "المستخدم"
        
        msg = f"**مرحباً بك عزيـزي {name} في سورس عبود المطور 📊**\n\n"
        msg += "البوت يعمل الآن بنجاح عبر التوكن المسجل في الهوست ✅\n"
        msg += "يمكنك استخدام الأوامر المتاحة لك."
        
        buttons = [
            [Button.url("قناة السورس 📡", url="https://t.me/lAYAI")],
            [Button.url("المطور 🧑🏻‍💻", url="https://t.me/BD_0I")]
        ]
        
        await event.reply(msg, buttons=buttons)
