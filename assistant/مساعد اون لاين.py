# -*- coding: utf-8 -*-
# assistant/مساعد_اونلاين.py
# معالج InlineQuery لأمر المطور

from telethon import events, types

OWNER_ID = 6373993992
OWNER_USERNAME = "BD_0I"
PIC_URL = "https://files.catbox.moe/k4fxu0.jpg"

def setup(client):
    @client.on(events.InlineQuery)
    async def inline_handler(event):
        query = event.text.strip()
        user_id = event.query.user_id

        if user_id != OWNER_ID:
            await event.answer([], switch_pm="🚫 هذا الأمر للمطور فقط", switch_pm_param="start")
            return

        if query == "المطور":
            try:
                owner_entity = await client.get_entity(OWNER_ID)
                owner_name = owner_entity.first_name or "المطور"
            except:
                owner_name = "المطور"

            caption = (
                "<b>مطورين سورس فينيكس</b>\n"
                "✛━━━━━━━━━━━━━✛\n"
                f"<b>• المطور الأساسي :</b> @{OWNER_USERNAME}\n"
                f"<b>• قناة السورس :</b> @lAYAI\n"
                "✛━━━━━━━━━━━━━✛\n"
                "<b>• النظام :</b> يعمل الآن بنجاح 🚀"
            )

            buttons = [
                types.KeyboardButtonRow(buttons=[
                    types.KeyboardButtonUrl(
                        text=f"👨‍💻 المطور: {owner_name}",
                        url=f"https://t.me/{OWNER_USERNAME}",
                        color=1   # 1 = أزرق
                    )
                ]),
                types.KeyboardButtonRow(buttons=[
                    types.KeyboardButtonUrl(
                        text="📢 قناة السورس",
                        url="https://t.me/lAYAI",
                        color=3   # 3 = أخضر
                    )
                ])
            ]

            result = types.InputBotInlineResult(
                id="dev_info",
                type="photo",
                title="معلومات المطور",
                description="اضغط للإرسال",
                url=f"https://t.me/{OWNER_USERNAME}",
                thumb=types.InputWebDocument(
                    url=PIC_URL, size=0, mime_type="image/jpeg", attributes=[]
                ),
                content=types.InputWebDocument(
                    url=PIC_URL, size=0, mime_type="image/jpeg", attributes=[]
                ),
                send_message=types.InputBotInlineMessageMediaAuto(
                    message=caption,
                    entities=None,
                    reply_markup=types.ReplyInlineMarkup(rows=buttons),
                    parse_mode="html"
                )
            )

            await event.answer([result], cache_time=0)
