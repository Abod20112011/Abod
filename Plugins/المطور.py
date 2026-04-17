# -*- coding: utf-8 -*-
# Plugins/developer.py
# أمر .المطور مع زر أزرق يوجه لحساب المطور

import random
import time
from telethon import events, types
from telethon.tl.functions.users import GetFullUserRequest
from ..helpers.utils import reply_id
from . import mention

plugin_category = "utils"

# بيانات المطور (عدلها حسب حسابك)
OWNER_USERNAME = "BD_0I"        # بدون @
OWNER_ID = 6373993992           # آيديك
PIC_URLS = ["https://files.catbox.moe/k4fxu0.jpg"]  # قائمة صور

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_cmd(event):
        reply_to = await reply_id(event)

        # جلب اسم المطور من حسابه
        try:
            full = await client(GetFullUserRequest(OWNER_ID))
            owner_name = full.users[0].first_name or "المطور"
        except:
            owner_name = "المطور"

        # اختيار صورة عشوائية
        pic = random.choice(PIC_URLS)

        # نص الرسالة
        caption = (
            "**مطورين سورس فينيكس**\n"
            "✛━━━━━━━━━━━━━✛\n"
            f"**• المطور الأساسي :** @{OWNER_USERNAME}\n"
            f"**• قناة السورس :** @lAYAI\n"
            "✛━━━━━━━━━━━━━✛\n"
            "**• النظام :** يعمل الآن بنجاح 🚀"
        )

        # بناء زر أزرق (primary) مع رابط حساب المطور
        dev_button = types.KeyboardButtonUrl(
            text=f"👨‍💻 المطور: {owner_name}",
            url=f"https://t.me/{OWNER_USERNAME}",
            color=1   # 1 = primary (أزرق)
        )
        inline_markup = types.ReplyInlineMarkup(
            rows=[types.KeyboardButtonRow(buttons=[dev_button])]
        )

        # إرسال الصورة مع الزر
        try:
            await client.send_file(
                event.chat_id,
                file=pic,
                caption=caption,
                buttons=inline_markup,
                reply_to=reply_to
            )
        except Exception as e:
            # في حال فشل الصورة، نرسل رسالة نصية مع الزر
            await client.send_message(
                event.chat_id,
                caption,
                buttons=inline_markup,
                reply_to=reply_to
            )

        # حذف أمر .المطور (اختياري)
        await event.delete()
