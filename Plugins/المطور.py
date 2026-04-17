# -*- coding: utf-8 -*-
# Plugins/المطور.py
from telethon import events

BOT_USERNAME = "xxscnbot"  # ⚠️ غيّره إلى يوزر بوتك المساعد (بدون @)

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        try:
            results = await client.inline_query(BOT_USERNAME, "المطور")
            if results:
                await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
                await event.delete()
            else:
                await event.edit("❌ لم يتم العثور على نتائج. تأكد من أن البوت يعمل.")
        except Exception as e:
            await event.edit(f"❌ حدث خطأ: {e}")
