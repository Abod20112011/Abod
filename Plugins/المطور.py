# -*- coding: utf-8 -*-
# موديول المطور المحدث - سورس عبود V11.0
# يتم وضعه في Plugins

import asyncio
import time
from telethon import events, Button
import database

# إعدادات المطور
OWNER_ID = 6373993992 
PROGS = [OWNER_ID] 

# --- [ 1. دالة حماية الأزرار ] ---
# هذه الدالة تمنع أي شخص غيرك من الضغط على أزرار التحكم
def check_owner(func):
    async def wrapper(event):
        if event.query.user_id in PROGS:
            return await func(event)
        else:
            # رسالة التنبيه للمتطفلين
            return await event.answer("⚠️ هذا الخيار خاص بالمطور عبود فقط! @BD_0I", alert=True)
    return wrapper

def setup(l313l):
    # --- [ 2. أمر المطور الرئيسي ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
    async def developer_info(event):
        # معلومات المطور للتنسيق
        me = await l313l.get_me()
        user_name = f"@{me.username}" if me.username else me.first_name
        
        caption = (
            f"✛━━━━━━━━━━━━━✛\n"
            f"   • **MY INFORMATION** •\n"
            f"✛━━━━━━━━━━━━━✛\n"
            f"**• NAME :** Abod\n"
            f"**• USERNAME :** @BD_0I\n"
            f"**• ID :** `{OWNER_ID}`\n"
            f"**• SOURCE :** PHOENIX V11.0\n"
            f"✛━━━━━━━━━━━━━✛\n"
            f"**• DEVELOPER :**\n"
            f"**• SOURCE MADE BY ABOD**\n"
            f"**• THANKS FOR USING**\n"
            f"✛━━━━━━━━━━━━━✛"
        )

        # إنشاء الأزرار الملونة (الأزرق primary)
        # ملاحظة: أزرار الروابط (URL) تعمل للجميع، أزرار الـ callback سنحميها
        buttons = [
            [Button.url("‹ : المطور : ›", "https://t.me/BD_0I")],
            [Button.inline("⚙️ إعدادات السورس (خاص)", data="dev_settings", style="primary")]
        ]

        try:
            # الإرسال عبر البوت المساعد لضمان ظهور الزر "عبر البوت" كما في الصورة
            await tgbot.send_message(
                event.chat_id,
                caption,
                buttons=buttons,
                link_preview=False
            )
            await event.delete()
        except Exception as e:
            # إذا فشل البوت المساعد يرسلها الحساب كرسالة عادية
            await event.edit(caption + f"\n\n⚠️ خطأ في الأزرار: {e}")

    # --- [ 3. معالج الأزرار مع الحماية ] ---
    @tgbot.on(events.CallbackQuery(data="dev_settings"))
    @check_owner
    async def dev_callback(event):
        # هذه الرسالة لن يراها إلا أنت بفضل @check_owner
        await event.answer("✅ أهلاً بك مطوري في لوحة التحكم الخاصة بك.", alert=True)
        
        # يمكنك هنا تغيير نص الرسالة لخيارات أخرى
        await event.edit("⚙️ **لوحة تحكم سورس عبود:**", buttons=[
            [Button.inline("🔴 حظر السورس", data="block_src", style="danger")],
            [Button.inline("🟢 إلغاء الحظر", data="unblock_src", style="success")],
            [Button.inline("« رجوع", data="back_dev", style="primary")]
        ])

    # --- [ 4. أوامر الحظر من داخل الأزرار ] ---
    @tgbot.on(events.CallbackQuery(data="block_src"))
    @check_owner
    async def block_src_btn(event):
        database.set_config("is_blocked", "yes")
        await event.answer("✅ تم تفعيل الحظر العام للسورس.", alert=True)

    @tgbot.on(events.CallbackQuery(data="unblock_src"))
    @check_owner
    async def unblock_src_btn(event):
        database.set_config("is_blocked", "no")
        await event.answer("✅ تم إلغاء الحظر العام.", alert=True)

