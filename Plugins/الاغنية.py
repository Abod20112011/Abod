import asyncio
import os
from telethon import events
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import MessageEntityCustomEmoji

# ==================================================================
# 🎯 الإعدادات (تأكد من هذه القيم)
# ==================================================================
BOT_USERNAME = "@GoldnB7Rbot"           # بوت التحميل
MY_RIGHTS = "@BD_0I"                   # توقيعك
# أيدي النجمة المميزة الرسمي (لا تغيره لكي تظهر النجمة بشكل صحيح)
PREMIUM_EMOJI_ID = 5159115433214739591 
CMD_SONG = "يوت"                        # الأمر المرسل للبوت

async def unblock_bot(client):
    try: await client(UnblockRequest(id=BOT_USERNAME))
    except: pass

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.بحث (.*)"))
    async def owner_search(event):
        query = event.pattern_match.group(1)
        # رسالة الانتظار
        status_msg = await event.edit("╮ جـارِ البحث عـن الإغـنيةة ... 🎧♥️ ╰")
        
        try:
            await unblock_bot(event.client)
            # إرسال طلب البحث للبوت المساعد
            sent = await event.client.send_message(BOT_USERNAME, f"{CMD_SONG} {query}")
            
            media_msg = None
            # انتظار رد البوت لمدة 20 ثانية
            for _ in range(10):
                await asyncio.sleep(2)
                messages = await event.client.get_messages(BOT_USERNAME, limit=5)
                for msg in messages:
                    if msg.id > sent.id and msg.media:
                        media_msg = msg
                        break
                if media_msg: break

            if media_msg:
                # 🛠️ إنشاء الكابشن مع النجمة المميزة
                caption_text = f"• uploader {MY_RIGHTS} ⭐"
                # تحديد مكان النجمة لوضع التأثير المميز عليها
                emoji_pos = caption_text.find("⭐")
                entities = [
                    MessageEntityCustomEmoji(
                        offset=emoji_pos,
                        length=2, # طول الإيموجي
                        document_id=PREMIUM_EMOJI_ID
                    )
                ]

                # إرسال الملف بالحقوق المطلوبة
                await event.client.send_file(
                    event.chat_id, 
                    media_msg.media, 
                    caption=caption_text, 
                    formatting_entities=entities, # تفعيل النجمة المميزة
                    reply_to=event.id
                )
                await status_msg.delete()
            else:
                await status_msg.edit("**❌ لم يتم العثور على نتائج في القناة.**")
        
        except Exception as e:
            await status_msg.edit(f"**❌ حدث خطأ:** `{str(e)[:50]}`")
        finally:
            # تنظيف المحادثة مع بوت التحميل
            try: 
                await event.client(DeleteHistoryRequest(peer=BOT_USERNAME, max_id=0, just_clear=True, revoke=True))
            except: pass

    print("✅ تم تحديث موديول البحث (الحقوق: uploader @BD_0I ⭐)")
