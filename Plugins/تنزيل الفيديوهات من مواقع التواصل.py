import asyncio
from telethon import events, functions
import database

# معرف البوت المستخدم للتحميل
DOWNLOAD_BOT = "@K0XBOT"

def setup(l313l):
    # 1. أمر التحميل الرئيسي
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.داون (.*)"))
    async def downloader(event):
        link = event.pattern_match.group(1).strip()
        
        if not link:
            return await event.edit("**⚠️ يرجى وضع رابط مع الأمر!**")
        
        # تحديث الإحصائيات
        try:
            database.update_stats("التحميل")
        except:
            pass
        
        await event.edit("⎉╎جـارِ التحميل انتظر قليلا ▬▭")
        
        # إرسال الرابط للبوت (ستارت ثم الرابط)
        await event.client.send_message(DOWNLOAD_BOT, "/start")
        await asyncio.sleep(2)
        await event.client.send_message(DOWNLOAD_BOT, link)

    # 2. موديول المراقبة (يحول الفيديو فور وصوله)
    @l313l.on(events.NewMessage(incoming=True, from_users=DOWNLOAD_BOT))
    async def worker(event):
        # التأكد أن الرسالة تحتوي على ميديا (فيديو أو صور)
        if event.media:
            # إرسال الميديا للمطور مع الوصف المطلوب
            caption = "• uploader @BD_0I"
            # سيتم الإرسال إلى "الرسائل المحفوظة" أو آخر محادثة نشطة
            # والأفضل إرسالها لك مباشرة عبر معرفك المخزن
            await event.client.send_file("me", event.media, caption=caption)
            
            # تنظيف المحادثة من طرفك (اختياري ليبقى الحساب نظيفاً)
            await event.client(functions.messages.DeleteHistoryRequest(
                peer=DOWNLOAD_BOT,
                max_id=0,
                just_clear=False,
                revoke=False
            ))
