from telethon import events, functions
from telethon.tl.functions.channels import InviteToChannelRequest
import database, asyncio

def setup(l313l):
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"\.ضيف ?(.*)"))
    async def add_members(event):
        database.update_stats("اضافة_اعضاء")
        target = event.pattern_match.group(1)
        await event.edit("🔄 **جاري السحب والإضافة...**")
        try:
            async for user in l313l.iter_participants(target):
                try:
                    await l313l(InviteToChannelRequest(event.chat_id, [user.id]))
                    await asyncio.sleep(0.5)
                except: continue
            await event.edit("✅ **اكتملت عملية الإضافة.**")
        except Exception as e: await event.edit(f"❌ **خطأ:** `{e}`")

    @l313l.on(events.NewMessage(outgoing=True, pattern=r"\.اضافة_جهاتي"))
    async def add_contacts(event):
        contacts = await l313l(functions.contacts.GetContactsRequest(hash=0))
        for user in contacts.users:
            try: await l313l(InviteToChannelRequest(event.chat_id, [user.id]))
            except: continue
        await event.edit("✅ **تم إضافة جهات الاتصال.**")
