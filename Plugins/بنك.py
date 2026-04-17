import random
import asyncio
from datetime import datetime
from telethon import events
from JoKeRUB import l313l # استيراد المحرك الأساسي

# --- إعدادات افتراضية لـ aBooD ---
DEFAULT_PING_IMG = "https://graph.org/file/26ece5eed6b56c5ba671f-fa81fdea5124cb7cb2.jpg"
DEFAULT_PING_TEXT = "**[ 𝗜 𝗝𝘂𝘀𝘁 𝗔𝘀𝗸𝗲𝗱 𝗙𝗼𝗿 𝗦𝗼𝗺𝗲 𝗣𝗲𝗮𝗰𝗲 . ](t.me/BD_0I)**"
TEMP = """{PING_TEXT}
┏━━━━━━━┓
┃ ✦ {ping} ms
┃ ✦ {mention}
┗━━━━━━━┛"""

@l313l.ar_cmd(pattern="بنك(?:\s|$)([\s\S]*)")
async def jokerping(event):
    # حساب سرعة الاستجابة
    start = datetime.now()
    # رسالة مؤقتة لتأكيد البدء
    msg = await event.edit("** ᯽︙ يتـم التـأكـد من البنك انتـظر قليلا رجاءا**")
    end = datetime.now()
    
    # حساب الملي ثانية
    ms = (end - start).microseconds / 1000
    
    # جلب الإعدادات (تأكد من وجود نظام gvarstatus في سورسك أو سيستخدم الافتراضي)
    EMOJI = "✇ ◅"
    PING_TEXT = DEFAULT_PING_TEXT
    PING_IMG = DEFAULT_PING_IMG
    
    # الحصول على المنشن من الحساب المشغل
    me = await event.client.get_me()
    mention = f"[{me.first_name}](tg://user?id={me.id})"
    
    caption = TEMP.format(
        PING_TEXT=PING_TEXT,
        ping=ms,
        mention=mention
    )

    if PING_IMG:
        try:
            # إرسال الصورة مع الكابشن الجديد
            await event.client.send_file(
                event.chat_id, 
                PING_IMG, 
                caption=caption, 
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
        except Exception as e:
            # في حال فشل الرابط، نرسل نص فقط
            await event.edit(f"**الميـديا خـطأ، تم إرسال النص فقط:**\n\n{caption}")
    else:
        await event.edit(caption)
