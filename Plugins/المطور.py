# -*- coding: utf-8 -*-
# Plugins/developer.py
# أمر .المطور يرسل رسالة عبر البوت المساعد لتحتوي على أزرار ملونة

import random
import requests
from telethon import events

# --- إعدادات ---
OWNER_USERNAME = "BD_0I"        # بدون @
OWNER_ID = 6373993992           # آيديك
PIC_URLS = ["https://files.catbox.moe/k4fxu0.jpg"]
# --------------

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

        # 4. بناء الزر الملون (أزرق)
        # هذه هي الطريقة الصحيحة لبناء الأزرار الملونة عبر Bot API
        keyboard = {
            "inline_keyboard": [
                [{
                    "text": f"👨‍💻 المطور: {owner_name}",
                    "url": f"https://t.me/{OWNER_USERNAME}",
                    "style": "primary"  # ✅ هذا هو اللون الأزرق (primary)
                }]
            ]
        }

        # 5. إرسال الرسالة عبر البوت المساعد
        # نستخدم requests مباشرة لإرسال صورة مع زر عبر Bot API
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": pic,
            "caption": caption,
            "reply_to_message_id": reply_to,
            "reply_markup": json.dumps(keyboard) # تحويل الـ keyboard إلى JSON
        }

        try:
            # إرسال الصورة عبر البوت
            response = requests.post(url, data=payload).json()
            if response.get("ok"):
                await event.delete() # حذف أمر .المطور بعد نجاح الإرسال
            else:
                await event.edit(f"⚠️ فشل الإرسال: {response.get('description')}")
        except Exception as e:
            await event.edit(f"❌ حدث خطأ: {e}")

# لا تنسى استيراد json في أعلى الملف إذا لم يكن موجودًا
import json
