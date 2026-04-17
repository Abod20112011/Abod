# -*- coding: utf-8 -*-
# Plugins/developer.py
# أمر .المطور يشرح كيفية استخدام الوضع المضمن

from telethon import events, Button

OWNER_USERNAME = "BD_0I"

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        bot_username = "@xxscnbot"  # غيّره إلى يوزر بوتك
        text = (
            "**📢 لإرسال رسالة المطور مع أزرار ملونة من حسابك:**\n\n"
            f"1️⃣ اكتب في أي محادثة: `{bot_username} المطور`\n"
            "2️⃣ اختر النتيجة التي تظهر.\n"
            "3️⃣ ستُرسل الرسالة باسمك مع أزرار ملونة! 🎉"
        )
        await event.edit(text, parse_mode="markdown")
