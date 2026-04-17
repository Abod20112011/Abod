import os
from telethon import events, types
from PIL import Image

# دالة وهمية لتجنب خطأ No module named 'database'
class DatabaseDummy:
    def update_stats(self, name): pass
database = DatabaseDummy()

def setup(client):
    # --- تحويل صورة إلى ملصق ---
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ملصق"))
    async def img_to_sticker(event):
        database.update_stats("ملصق")
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.edit("**✿ يجب الرد على صورة أولاً!**")
        
        await event.edit("**✿ جاري المعالجة...**")
        try:
            photo = await reply.download_media()
            img = Image.open(photo)
            
            # التأكد من الحجم المناسب للملصقات في تيليجرام
            img.thumbnail((512, 512))
            
            sticker_path = "sticker.webp"
            img.save(sticker_path, "WEBP")
            
            await event.client.send_file(event.chat_id, sticker_path, reply_to=reply.id)
            await event.delete()
            
            for f in [photo, sticker_path]:
                if os.path.exists(f): os.remove(f)
        except Exception as e:
            await event.edit(f"**✿ خطأ:** `{e}`")

    # --- تحويل ملصق إلى صورة ---
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.صورة"))
    async def sticker_to_img(event):
        database.update_stats("صورة")
        reply = await event.get_reply_message()
        if not reply or not reply.sticker:
            return await event.edit("**✿ يجب الرد على ملصق أولاً!**")
        
        await event.edit("**✿ جاري التحويل إلى صورة...**")
        try:
            sticker = await reply.download_media()
            img = Image.open(sticker).convert("RGB")
            img_path = "converted.jpg"
            img.save(img_path, "JPEG")
            
            await event.client.send_file(event.chat_id, img_path, reply_to=reply.id)
            await event.delete()
            
            for f in [sticker, img_path]:
                if os.path.exists(f): os.remove(f)
        except Exception as e:
            await event.edit(f"**✿ خطأ:** `{e}`")

    # --- تحويل فيديو إلى متحركة ---
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.متحركة"))
    async def video_to_gif(event):
        database.update_stats("متحركة")
        reply = await event.get_reply_message()
        if not reply or not reply.video:
            return await event.edit("**✿ يجب الرد على فيديو أولاً!**")
        
        await event.edit("**✿ جاري التحويل لـ GIF...**")
        try:
            video = await reply.download_media()
            await event.client.send_file(
                event.chat_id, 
                video, 
                reply_to=reply.id,
                attributes=[types.DocumentAttributeVideo(
                    duration=int(reply.video.attributes[0].duration),
                    w=reply.video.attributes[0].w,
                    h=reply.video.attributes[0].h,
                    nosound=True # إزالة الصوت ليصبح GIF
                )]
            )
            await event.delete()
            if os.path.exists(video): os.remove(video)
        except Exception as e:
            await event.edit(f"**✿ خطأ:** `{e}`")
