# -*- coding: utf-8 -*-
# Plugins/المطور.py - متوافق مع سورس عبود V11.0
from telethon import events

# ========== إعدادات المطور ==========
DEV_PIC = "https://files.catbox.moe/k4fxu0.jpg"
DEV_TEXT = (
    "<b>مطورين سورس عبود</b>\n"
    "✛━━━━━━━━━━━━━✛\n"
    "<b>• المطور الأساسي :</b> @BD_0I\n"
    "<b>• قناة السورس :</b> @lAYAI\n"
    "✛━━━━━━━━━━━━━✛\n"
    "<b>• النظام :</b> يعمل الآن بنجاح 🚀"
)
# =====================================

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        await event.delete()  # حذف الأمر

        # بناء الأزرار الملونة
        buttons = [
            [{"text": "👨‍💻 المطور: BD_0I", "url": "https://t.me/BD_0I", "style": "primary"}],
            [{"text": "📢 قناة السورس", "url": "https://t.me/lAYAI", "style": "success"}]
        ]

        # استخدام دالة send_bot_photo المحقونة في client
        try:
            result = client.send_bot_photo(
                chat_id=event.chat_id,
                photo_url=DEV_PIC,
                caption=DEV_TEXT,
                buttons=buttons,
                parse_mode='HTML'
            )
            if not result or not result.get("ok"):
                # في حال فشل API، نرسل رسالة نصية
                await client.send_message(event.chat_id, DEV_TEXT, parse_mode='html')
        except Exception as e:
            await client.send_message(event.chat_id, f"❌ حدث خطأ: {e}")
