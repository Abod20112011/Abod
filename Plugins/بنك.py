# -*- coding: utf-8 -*-
# موديول البنك - خاص بسورس عبود المطور
import random
import asyncio
from datetime import datetime
from telethon import events

# إعدادات الميديا الافتراضية
DEFAULT_PING_IMG = "https://graph.org/file/26ece5eed6b56c5ba671f-fa81fdea5124cb7cb2.jpg"
DEFAULT_PING_TEXT = "**[ 𝗜 𝗝𝘂𝘀𝘁 𝗔𝘀𝗸𝗲𝗱 𝗙𝗼𝗿 𝗦𝗼𝗺𝗲 𝗣𝗲𝗮𝗰𝗲 . ](t.me/BD_0I)**"

TEMP = """{PING_TEXT}
┏━━━━━━━┓
┃ ✦ {ping} ms
┃ ✦ {mention}
┗━━━━━━━┛"""

def setup(client):
    # استخدام ar_cmd المحقون في ملف التشغيل الأساسي
    @client.ar_cmd(pattern="بنك(?:\s|$)([\s\S]*)")
    async def abood_ping_handler(event):
        # حساب سرعة الاستجابة
        start = datetime.now()
        msg = await event.edit("**᯽︙ جـاري فحـص البنك.. انتظر قليلاً عبود 🩵**")
        end = datetime.now()
        
        # حساب الملي ثانية بدقة
        ms = (end - start).microseconds / 1000
        
        # جلب البيانات من محرك التوافق (database هو الموديل الأساسي المحقون)
        # سيقوم الكود بالبحث عن نص مخصص في القاعدة، وإذا لم يجد سيستخدم الافتراضي
        try:
            from database import get_config
            PING_TEXT = get_config("PING_TEXT") or DEFAULT_PING_TEXT
            PING_IMG = get_config("PING_IMG") or DEFAULT_PING_IMG
        except ImportError:
            PING_TEXT = DEFAULT_PING_TEXT
            PING_IMG = DEFAULT_PING_IMG

        # الحصول على معلومات الحساب
        me = await client.get_me()
        mention = f"[{me.first_name}](tg://user?id={me.id})"
        
        # تنسيق الرسالة النهائية
        caption = TEMP.format(
            PING_TEXT=PING_TEXT,
            ping=ms,
            mention=mention
        )

        try:
            if PING_IMG:
                # إرسال الصورة مع الكابشن وحذف رسالة "جاري الفحص"
                await client.send_file(
                    event.chat_id, 
                    PING_IMG, 
                    caption=caption, 
                    reply_to=event.reply_to_msg_id
                )
                await event.delete()
            else:
                await event.edit(caption)
        except Exception as e:
            # في حال وجود خطأ في الرابط أو الميديا، نرسل نصاً فقط
            await event.edit(f"⚠️ **حدث خطأ في الميديا، إليك النتيجة نصياً:**\n\n{caption}")

# تم التعديل ليتوافق مع هيكلية سورس عبود V10.0
