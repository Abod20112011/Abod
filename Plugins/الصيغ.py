import os
import asyncio
from telethon import events

def setup(client):
    global l313l
    l313l = client

    @l313l.on(events.NewMessage(pattern=r"^\.تحويل بصمة$", outgoing=True))
    async def mp3_to_voice(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.edit("**᯽︙ رد على ملف MP3 أولاً!**")

        await event.edit("**᯽︙ جاري تحويل الملف إلى بصمة صوتية... 🎙**")
        
        if not os.path.exists("./temp"): os.makedirs("./temp")
        file_path = await event.client.download_media(reply, "./temp/")
        # يجب أن ينتهي الملف بـ .ogg ليعتبره التيليجرام بصمة صحيحة
        voice_file = file_path.rsplit('.', 1)[0] + ".ogg"

        try:
            # أوامر ffmpeg مخصصة للبصمات (تردد 48000 وقناة واحدة mono)
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-i', file_path,
                '-c:a', 'libopus', '-b:a', '32k', '-ar', '48000', '-ac', '1',
                voice_file, '-y'
            )
            await process.wait()

            if os.path.exists(voice_file):
                await event.client.send_file(
                    event.chat_id,
                    voice_file,
                    voice_note=True, # هذا الخيار هو اللي يخليها بصمة
                    reply_to=reply.id
                )
                await event.delete()
            else:
                await event.edit("❌ **فشل في معالجة الملف.**")

        except Exception as e:
            await event.edit(f"❌ **حدث خطأ:** `{str(e)}`")
        
        if os.path.exists(file_path): os.remove(file_path)
        if os.path.exists(voice_file): os.remove(voice_file)
