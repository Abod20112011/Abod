# -*- coding: utf-8 -*-
# Plugins/المطور.py
# أمر .المطور مع أزرار أونلاين ملونة (مثل أمر هاك)

from telethon import events, Button
from ..Config import Config
from . import l313l, tgbot

# بيانات المطور (عدلها)
OWNER_ID = 6373993992
OWNER_USERNAME = "BD_0I"
DEV_PIC = "https://files.catbox.moe/k4fxu0.jpg"

# النص الذي سيظهر في الرسالة
DEV_TEXT = (
    "<b>مطورين سورس فينيكس</b>\n"
    "✛━━━━━━━━━━━━━✛\n"
    f"<b>• المطور الأساسي :</b> @{OWNER_USERNAME}\n"
    f"<b>• قناة السورس :</b> @lAYAI\n"
    "✛━━━━━━━━━━━━━✛\n"
    "<b>• النظام :</b> يعمل الآن بنجاح 🚀"
)

Bot_Username = Config.TG_BOT_USERNAME

# ============== معالج InlineQuery ==============
if Config.TG_BOT_USERNAME is not None and tgbot is not None:

    @tgbot.on(events.InlineQuery)
    async def inline_handler(event):
        builder = event.builder
        result = None
        query = event.text

        # التحقق من أن المستخدم هو المطور
        if query.startswith("المطور") and event.query.user_id == l313l.uid:
            # بناء الأزرار الملونة
            buttons = [
                [Button.url(f"👨‍💻 المطور: {OWNER_USERNAME}", f"https://t.me/{OWNER_USERNAME}")],
                [Button.url("📢 قناة السورس", "https://t.me/lAYAI")]
            ]

            if DEV_PIC and DEV_PIC.endswith((".jpg", ".png", "gif", "mp4")):
                result = builder.photo(
                    DEV_PIC,
                    text=DEV_TEXT,
                    buttons=buttons,
                    link_preview=False,
                    parse_mode="html"
                )
            elif DEV_PIC:
                result = builder.document(
                    DEV_PIC,
                    title="معلومات المطور",
                    text=DEV_TEXT,
                    buttons=buttons,
                    link_preview=False,
                    parse_mode="html"
                )
            else:
                result = builder.article(
                    title="معلومات المطور",
                    text=DEV_TEXT,
                    buttons=buttons,
                    link_preview=False,
                    parse_mode="html"
                )

        await event.answer([result] if result else None)

# ============== أمر .المطور ==============
@l313l.ar_cmd(pattern="المطور$")
async def developer_cmd(event):
    if event.fwd_from:
        return

    bot_username = Config.TG_BOT_USERNAME
    if not bot_username:
        return await event.edit("❌ لم يتم تعيين توكن البوت المساعد.")

    # استدعاء Inline Query من البوت المساعد
    try:
        response = await event.client.inline_query(bot_username, "المطور")
        if response:
            await response[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
            await event.delete()
        else:
            await event.edit("❌ لم يتم العثور على نتائج.")
    except Exception as e:
        await event.edit(f"❌ حدث خطأ: {e}")
