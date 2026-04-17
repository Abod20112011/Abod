# -*- coding: utf-8 -*-
# Plugins/colored_buttons.py
# أمر .ازرار - يرسل أزراراً ملونة عبر البوت المساعد

import json
import requests
from telethon import events

def setup(client):
    # الحصول على دوال القاعدة من الكائن المحقون 'database'
    database = getattr(client, 'database', None)
    if database:
        get_config = database.get_config
    else:
        # احتياط في حال عدم وجود الحقن
        def get_config(key): return None

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ازرار$"))
    async def colored_buttons_cmd(event):
        chat_id = event.chat_id
        token = get_config("TOKEN")
        if not token:
            await event.edit("❌ التوكن غير موجود في القاعدة.")
            return

        text = (
            "✨ <b>مرحباً بك في نظام الأزرار الملونة!</b>\n"
            "اختر أحد الأزرار أدناه:"
        )
        buttons = [
            [{"text": "🔵 زر أزرق (primary)", "callback_data": "btn_primary", "style": "primary"}],
            [{"text": "🟢 زر أخضر (success)", "callback_data": "btn_success", "style": "success"}],
            [{"text": "🔴 زر أحمر (danger)", "callback_data": "btn_danger", "style": "danger"}]
        ]

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps({"inline_keyboard": buttons}),
            "parse_mode": "HTML"
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                await event.delete()
            else:
                await event.edit(f"⚠️ فشل الإرسال: {resp.text}")
        except Exception as e:
            await event.edit(f"❌ خطأ: {e}")
