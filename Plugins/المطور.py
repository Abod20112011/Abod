# -*- coding: utf-8 -*-
# Plugins/المطور.py
# أمر .المطور يرسل رسالة المطور مع أزرار ملونة

from telethon import events

# ضع يوزر البوت المساعد هنا (بدون @)
BOT_USERNAME = "xxscnbot"

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        try:
            results = await client.inline_query(BOT_USERNAME, "المطور")
            if results:
                await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
                await event.delete()
            else:
                await event.edit("❌ لم يتم العثور على نتائج.")
        except Exception as e:
            await event.edit(f"❌ حدث خطأ: {e}")
