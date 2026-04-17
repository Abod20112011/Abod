# -*- coding: utf-8 -*-
# Plugins/colored_buttons.py
# أمر .ازرار لاستدعاء الأزرار الملونة عبر البوت المساعد

from telethon import events
import sys
import os

# إضافة مجلد assistant إلى المسار لاستيراد الدوال
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'assistant'))
from bot_utils import send_colored_buttons_example

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ازرار$"))
    async def colored_buttons_cmd(event):
        chat_id = event.chat_id
        # استدعاء دالة الإرسال من المساعد
        await send_colored_buttons_example(client, chat_id)
        await event.delete()
