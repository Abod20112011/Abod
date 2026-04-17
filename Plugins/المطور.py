# -*- coding: utf-8 -*-
# Plugins/developer.py
# أمر .المطور مع زر يوجه لحساب المطور

import random
from telethon import events, Button

OWNER_USERNAME = "BD_0I"        # بدون @
OWNER_ID = 6373993992           # آيديك
PIC_URLS = ["https://files.catbox.moe/k4fxu0.jpg"]

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        reply_to = event.reply_to_msg_id

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

        # زر رابط باستخدام Button.url (متوافق مع Telethon 1.31.0)
        dev_button = Button.url(
            text=f"👨‍💻 المطور: {owner_name}",
            url=f"https://t.me/{OWNER_USERNAME}"
        )

        try:
            await client.send_file(
                event.chat_id,
                file=pic,
                caption=caption,
                buttons=dev_button,
                reply_to=reply_to
            )
        except Exception:
            await client.send_message(
                event.chat_id,
                caption,
                buttons=dev_button,
                reply_to=reply_to
            )

        await event.delete()
