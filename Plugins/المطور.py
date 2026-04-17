# -*- coding: utf-8 -*-
# Plugins/developer.py
# أمر .المطور يرسل صورة مع أزرار ملونة عبر البوت المساعد

import json
import random
import requests
from telethon import events

OWNER_USERNAME = "BD_0I"
OWNER_ID = 6373993992
PIC_URLS = ["https://files.catbox.moe/k4fxu0.jpg"]

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        chat_id = event.chat_id
        reply_to = event.reply_to_msg_id

        token = client.get_config("TOKEN")
        if not token:
            await event.edit("❌ توكن البوت غير موجود في القاعدة!")
            return

        try:
            owner_entity = await client.get_entity(OWNER_ID)
            owner_name = owner_entity.first_name or "المطور"
        except:
            owner_name = "المطور"

        pic = random.choice(PIC_URLS)

        caption = (
            "<b>مطورين سورس فينيكس</b>\n"
            "✛━━━━━━━━━━━━━✛\n"
            f"<b>• المطور الأساسي :</b> @{OWNER_USERNAME}\n"
            f"<b>• قناة السورس :</b> @lAYAI\n"
            "✛━━━━━━━━━━━━━✛\n"
            "<b>• النظام :</b> يعمل الآن بنجاح 🚀"
        )

        keyboard = {
            "inline_keyboard": [
                [{
                    "text": f"👨‍💻 المطور: {owner_name}",
                    "url": f"https://t.me/{OWNER_USERNAME}",
                    "style": "primary"
                }],
                [{
                    "text": "📢 قناة السورس",
                    "url": "https://t.me/lAYAI",
                    "style": "success"
                }]
            ]
        }

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": pic,
            "caption": caption,
            "reply_to_message_id": reply_to,
            "reply_markup": json.dumps(keyboard),
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, data=payload).json()
            if response.get("ok"):
                await event.delete()
            else:
                await event.edit(f"⚠️ فشل الإرسال: {response.get('description')}")
        except Exception as e:
            await event.edit(f"❌ حدث خطأ: {e}")
