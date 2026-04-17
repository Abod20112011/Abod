from telethon import events
import database as db

# --- معالج حذف رسائل المكتومين ---
@events.register(events.NewMessage(incoming=True))
async def mute_handler(event):
    if db.is_muted(event.sender_id):
        try:
            await event.delete()
        except Exception:
            pass

def setup(client):
    # تسجيل معالج الرسائل المكتومة في المحرك
    client.add_event_handler(mute_handler)

    # أمر كتم شخص (بالرد)
    @client.ar_cmd(pattern="كتم$")
    async def mute_user(event):
        if not event.is_reply:
            return await event.edit("**⚠️ يجب الرد على الشخص لكتمه.**")
        
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        user = await event.client.get_entity(user_id)
        
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد"
        
        db.add_muted(user_id, full_name, username)
        await event.edit(f"**👤 المستخدم: {full_name}\n✅ تم كتمه بنجاح.**")

    # أمر إلغاء الكتم (بالرد)
    @client.ar_cmd(pattern="الغاء الكتم$")
    async def unmute_user(event):
        if not event.is_reply:
            return await event.edit("**⚠️ يجب الرد على الشخص لالغاء كتمه.**")
        
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        
        db.remove_muted(user_id)
        await event.edit("**✅ تم إلغاء الكتم عن الشخص بنجاح.**")

    # أمر عرض قائمة المكتومين
    @client.ar_cmd(pattern="المكتومين$")
    async def list_muted(event):
        muted_list = db.get_all_muted()
        if not muted_list:
            return await event.edit("**📭 قائمة المكتومين فارغة.**")
        
        msg = "**📋 قائمة المكتومين لديك:**\n\n"
        for i, (uid, name, user) in enumerate(muted_list, 1):
            msg += f"{i} - {name} ({user})\n"
        
        await event.edit(msg)

    # أمر مسح كل المكتومين
    @client.ar_cmd(pattern="مسح المكتومين$")
    async def clear_muted(event):
        db.clear_all_muted()
        await event.edit("**🗑️ تم مسح جميع المكتومين من قاعدة البيانات.**")
