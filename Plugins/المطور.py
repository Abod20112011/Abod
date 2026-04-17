# -*- coding: utf-8 -*-
# Plugins/developer.py
# أمر .المطور يرسل رسالة عبر البوت المساعد مع أزرار ملونة

import json
import random
import requests
from telethon import events

# --- الإعدادات (عدلها حسب معلوماتك) ---
OWNER_USERNAME = "BD_0I"        # بدون @
OWNER_ID = 6373993992           # آيديك
PIC_URLS = ["https://files.catbox.moe/k4fxu0.jpg"]
# -----------------------------------------

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        chat_id = event.chat_id
        reply_to = event.reply_to_msg_id

        # 1. جلب توكن البوت من قاعدة البيانات
        token = client.get_config("TOKEN")
        if not token:
            await event.edit("❌ توكن البوت غير موجود في القاعدة!")
            return

        # 2. جلب اسمك من حسابك الشخصي
        try:
            owner_entity = await client.get_entity(OWNER_ID)
            owner_name = owner_entity.first_name or "المطور"
        except:
            owner_name = "المطور"

        # 3. تحضير محتوى الرسالة
        pic = random.choice(PIC_URLS)
        caption = (
            "**مطورين سورس فينيكس**\n"
            "✛━━━━━━━━━━━━━✛\n"
            f"**• المطور الأساسي :** @{OWNER_USERNAME}\n"
            f"**• قناة السورس :** @lAYAI\n"
            "✛━━━━━━━━━━━━━✛\n"
            "**• النظام :** يعمل الآن بنجاح 🚀"
        )

        # 4. بناء الأزرار الملونة
        keyboard = {
            "inline_keyboard": [
                [{
                    "text": f"👨‍💻 المطور: {owner_name}",
                    "url": f"https://t.me/{OWNER_USERNAME}",
                    "style": "primary"   # أزرق
                }],
                [{
                    "text": "📢 قناة السورس",
                    "url": "https://t.me/lAYAI",
                    "style": "success"   # أخضر
                }]
            ]
        }

        # 5. إرسال الصورة مع الأزرار عبر البوت المساعد
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": pic,
            "caption": caption,
            "reply_to_message_id": reply_to,
            "reply_markup": json.dumps(keyboard),
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, data=payload).json()
            if response.get("ok"):
                await event.delete()
            else:
                await event.edit(f"⚠️ فشل الإرسال: {response.get('description')}")
        except Exception as e:
            await event.edit(f"❌ حدث خطأ: {e}")
