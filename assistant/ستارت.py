# -*- coding: utf-8 -*-
# موديول الستارت المطور - سحب التوكن تلقائياً
from telethon import events, Button
import sys

# محاولة جلب العميل (البوت) من النظام الأساسي
try:
    import l313l
    client = l313l.l313l
except Exception:
    # البحث في الوحدات المشغلة داخل ملف التشغيل
    if 'main' in sys.modules:
        from __main__ import bot as client
    else:
        client = None

if client:
    @client.on(events.NewMessage(pattern="/start", incoming=True))
    async def assistant_start(event):
        if event.is_private:
            # جلب الاسم المسجل في قاعدة البيانات
            user = await event.get_sender()
            name = user.first_name if user else "عبود"
            
            msg = f"**مرحباً بك عزيـزي {name} ✨**\n"
            msg += "أنا بوت المساعد الخاص بسورس عبود\n"
            msg += "تم تفعيل الجلسة والتوكن بنجاح ✅"
            
            buttons = [
                [Button.url("قناة المطور", url="https://t.me/aqhvv")],
                [Button.url("الدعم الفني", url="https://t.me/BD_0I")]
            ]
            await event.reply(msg, buttons=buttons)
