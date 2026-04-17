# -*- coding: utf-8 -*-
# assistant/اونلاين_المطور.py
# معالج InlineQuery لأمر المطور مع أزرار ملونة وحماية check_owner

import asyncio
from telethon import events, types
from telethon.errors import FloodWaitError, MessageNotModifiedError

# بيانات المطور (عدلها)
OWNER_ID = 6373993992
OWNER_USERNAME = "BD_0I"
PIC_URL = "https://files.catbox.moe/k4fxu0.jpg"

# ============== دالة الحماية check_owner ==============
# يمكنك استيرادها من decorators.py إذا أردت، لكننا نعرفها هنا لضمان التوافق
def check_owner(func):
    async def wrapper(event):
        user_id = event.query.user_id if hasattr(event, 'query') else event.sender_id
        if user_id == OWNER_ID:
            try:
                await func(event)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 5)
            except MessageNotModifiedError:
                pass
        else:
            # في حالة InlineQuery نستخدم switch_pm
            if hasattr(event, 'answer'):
                await event.answer(
                    [],
                    switch_pm="🚫 هذا الأمر للمطور فقط",
                    switch_pm_param="start"
                )
            else:
                await event.answer("هذا الأمر للمطور فقط", alert=True)
    return wrapper
# =====================================================

def setup(client):
    @client.on(events.InlineQuery)
    @check_owner
    async def inline_handler(event):
        query = event.text.strip()
        if query != "المطور":
            return

        # جلب اسم المطور الحقيقي
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

        # بناء الأزرار الملونة
        buttons = [
            types.KeyboardButtonRow(buttons=[
                types.KeyboardButtonUrl(
                    text=f"👨‍💻 المطور: {owner_name}",
                    url=f"https://t.me/{OWNER_USERNAME}",
                    color=1   # 1 = primary (أزرق)
                )
            ]),
            types.KeyboardButtonRow(buttons=[
                types.KeyboardButtonUrl(
                    text="📢 قناة السورس",
                    url="https://t.me/lAYAI",
                    color=3   # 3 = success (أخضر)
                )
            ])
        ]

        # بناء نتيجة Inline بصورة
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
