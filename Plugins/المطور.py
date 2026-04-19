# -*- coding: utf-8 -*-
# Plugins/المطور.py
# أمر .المطور مع أزرار أونلاين ملونة عبر Inline Mode

from telethon import events, Button
from ..Config import Config
from . import l313l, tgbot

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

if Config.TG_BOT_USERNAME is not None and tgbot is not None:

    @tgbot.on(events.InlineQuery)
    async def dev_inline_handler(event):
        builder = event.builder
        query = event.text.strip()
        result = None

        # السماح فقط للمطور باستخدام هذا الاستعلام
        if query.startswith("المطور") and event.query.user_id == l313l.uid:
            buttons = [
                [Button.url("👨‍💻 المطور: BD_0I", "https://t.me/BD_0I")],
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

        await event.answer([result] if result else [])


@l313l.ar_cmd(pattern="المطور$")
async def developer_cmd(event):
    """إرسال رسالة المطور بأزرار أونلاين من حسابك الشخصي"""
    await event.delete()  # حذف الأمر فوراً

    bot_username = Config.TG_BOT_USERNAME
    if not bot_username:
        return await event.respond("❌ لم يتم تعيين توكن البوت المساعد.")

    try:
        response = await event.client.inline_query(bot_username, "المطور")
        if response:
            await response[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
        else:
            await event.respond("❌ لم يتم العثور على نتائج. تأكد من تفعيل Inline للبوت.")
    except Exception as e:
        await event.respond(f"❌ حدث خطأ: {e}")
