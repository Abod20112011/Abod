import re
from asyncio import sleep
from telethon import events
from telethon.errors import rpcbaseerrors
from telethon.tl.types import (
    InputMessagesFilterDocument,
    InputMessagesFilterEmpty,
    InputMessagesFilterGeo,
    InputMessagesFilterGif,
    InputMessagesFilterMusic,
    InputMessagesFilterPhotos,
    InputMessagesFilterRoundVideo,
    InputMessagesFilterUrl,
    InputMessagesFilterVideo,
    InputMessagesFilterVoice,
)

# استيراد المديرين والمساعدات مع معالجة الأخطاء
try:
    from ..core.managers import edit_delete, edit_or_reply
    from ..helpers.utils import reply_id
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = "me"
    async def edit_or_reply(event, text): return await event.edit(text)

# تعريف فلاتر التنظيف
purgetype = {
    "ب": InputMessagesFilterVoice,
    "م": InputMessagesFilterDocument,
    "ح": InputMessagesFilterGif,
    "ص": InputMessagesFilterPhotos,
    "l": InputMessagesFilterGeo,
    "غ": InputMessagesFilterMusic,
    "r": InputMessagesFilterRoundVideo,
    "ق": InputMessagesFilterEmpty,
    "ر": InputMessagesFilterUrl,
    "ف": InputMessagesFilterVideo,
}

def setup(client):
    global l313l
    l313l = client

    # --- أمر المسح (حذف رسالة محددة بالرد) ---
    @l313l.on(events.NewMessage(pattern=r"^\.مسح(\s*| \d+)$", outgoing=True))
    async def delete_it(event):
        input_str = event.pattern_match.group(1).strip()
        msg_src = await event.get_reply_message()
        
        if msg_src:
            if input_str and input_str.isnumeric():
                await event.delete()
                await sleep(int(input_str))
                try:
                    await msg_src.delete()
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, "#الـمسـح \n ᯽︙ تـم حـذف الـرسالة بـنجاح")
                except rpcbaseerrors.BadRequestError:
                    if BOTLOG:
                        await event.client.send_message(BOTLOG_CHATID, "᯽︙ لا يمـكنني الـحذف احـتاج صلاحيـات الادمـن")
            else:
                try:
                    await msg_src.delete()
                    await event.delete()
                except rpcbaseerrors.BadRequestError:
                    await edit_or_reply(event, "᯽︙ عـذرا الـرسالة لا استـطيع حـذفها")
        elif not input_str:
            await event.delete()

    # --- أمر مسح رسائلي (حذف كل رسائلك في الدردشة) ---
    @l313l.on(events.NewMessage(pattern=r"^\.مسح رسائلي$", outgoing=True))
    async def purge_me(event):
        count = 0
        async for message in event.client.iter_messages(event.chat_id, from_user='me'):
            count += 1
            await message.delete()

        smsg = await event.respond(f"**أنتهى التنظيف** تم حذف {count} من الرسائل التي أرسلتها أنت.")
        if BOTLOG:
            await event.client.send_message(BOTLOG_CHATID, f"#مسح_رسائلي\nتم حذف {count} رسالة في {event.chat_id}")
        await sleep(5)
        await smsg.delete()

    # --- أمر التنظيف السريع (بناءً على العدد أو النوع) ---
    @l313l.on(events.NewMessage(pattern=r"^\.تنظيف(?:\s|$)([\s\S]*)", outgoing=True))
    async def fastpurger(event):
        chat = await event.get_input_chat()
        msgs = []
        count = 0
        input_str = event.pattern_match.group(1)
        
        ptype = re.findall(r"-\w+", input_str)
        try:
            p_type = ptype[0].replace("-", "")
            input_str = input_str.replace(ptype[0], "").strip()
        except IndexError:
            p_type = None

        await event.delete()
        reply = await event.get_reply_message()
        
        if reply:
            async for msg in event.client.iter_messages(event.chat_id, min_id=reply.id - 1):
                msgs.append(msg)
                count += 1
                if len(msgs) == 100:
                    await event.client.delete_messages(chat, msgs)
                    msgs = []
        elif input_str.isnumeric():
            async for msg in event.client.iter_messages(chat, limit=int(input_str)):
                msgs.append(msg)
                count += 1
                if len(msgs) == 100:
                    await event.client.delete_messages(chat, msgs)
                    msgs = []
        
        if msgs:
            await event.client.delete_messages(chat, msgs)

        result = f"᯽︙ اكـتمل الـتنظيف السـريع\n᯽︙ تـم حـذف {count} مـن الـرسائل"
        hi = await event.client.send_message(event.chat_id, result)
        if BOTLOG:
            await event.client.send_message(BOTLOG_CHATID, f"#التنـظيف \n{result}")
        await sleep(5)
        await hi.delete()
