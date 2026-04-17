# -*- coding: utf-8 -*-
# Plugins/المطور.py
# أمر .المطور مع أزرار أونلاين من حسابك الشخصي

import random
from telethon import events, Button

# البيانات الخاصة بك
OWNER_USERNAME = "BD_0I"
OWNER_ID = 6373993992
PIC_URLS = ["https://files.catbox.moe/k4fxu0.jpg"]

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        reply_to = event.reply_to_msg_id

        # جلب اسمك الحقيقي من حسابك
        try:
            owner_entity = await client.get_entity(OWNER_ID)
            owner_name = owner_entity.first_name or "المطور"
        except:
            owner_name = "المطور"

        pic = random.choice(PIC_URLS)

        caption = (
            "**مطورين سورس فينيكس**\n"
            "✛━━━━━━━━━━━━━✛\n"
            f"**• المطور الأساسي :** @{OWNER_USERNAME}\n"
            f"**• قناة السورس :** @lAYAI\n"
            "✛━━━━━━━━━━━━━✛\n"
            "**• النظام :** يعمل الآن بنجاح 🚀"
        )

        # الأزرار الأونلاين كما تريدها
        buttons = [
            [Button.url(f"👨‍💻 المطور: {owner_name}", f"https://t.me/{OWNER_USERNAME}")],
            [Button.url("📢 قناة السورس", "https://t.me/lAYAI")]
        ]

        try:
            await client.send_file(
                event.chat_id,
                file=pic,
                caption=caption,
                buttons=buttons,
                reply_to=reply_to
            )
        except Exception:
            # إذا فشل إرسال الصورة، نرسل رسالة نصية
            await client.send_message(
                event.chat_id,
                caption,
                buttons=buttons,
                reply_to=reply_to
            )

        await event.delete()
