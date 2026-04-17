import os
from telethon import events, functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest, UploadProfilePhotoRequest
import database

# ذاكرة مؤقتة لحفظ بياناتك قبل الانتحال
MY_DATA = {}

def setup(l313l):
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.انتحال$"))
    async def clone(event):
        reply = await event.get_reply_message()
        if not reply:
            return await event.edit("⚠️ **يجب الرد على مستخدم لانتحاله!**")
        
        await event.edit("🎭 **جاري حفظ بياناتك الأصلية والانتحال...**")
        
        try:
            # 1. حفظ بياناتك الحالية (الاسم والبايو)
            me = await l313l.get_me()
            me_full = await l313l(GetFullUserRequest(me.id))
            MY_DATA['first_name'] = me.first_name
            MY_DATA['last_name'] = me.last_name or ""
            MY_DATA['about'] = me_full.full_user.about or ""
            
            # 2. حفظ صورتك الحالية
            photos = await l313l(GetUserPhotosRequest(user_id=me.id, offset=0, max_id=0, limit=1))
            if photos.photos:
                MY_DATA['photo'] = await l313l.download_media(photos.photos[0])
            else:
                MY_DATA['photo'] = None

            # 3. جلب بيانات الضحية
            user = await l313l.get_entity(reply.sender_id)
            user_full = await l313l(GetFullUserRequest(reply.sender_id))
            
            # 4. تحميل صورة الضحية
            user_photo = await l313l.download_profile_photo(user.id)
            
            # 5. تطبيق الانتحال على حسابك
            await l313l(functions.account.UpdateProfileRequest(
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                about=user_full.full_user.about or ""
            ))
            
            if user_photo:
                await l313l(UploadProfilePhotoRequest(file=await l313l.upload_file(user_photo)))
                os.remove(user_photo)

            await event.edit(f"✅ **تم انتحال شخصية {user.first_name} بنجاح!**")
            
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ:** `{str(e)}`")

    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.اعادة$"))
    async def restore(event):
        if not MY_DATA:
            return await event.edit("⚠️ **لا توجد بيانات محفوظة للعودة إليها!**")
        
        await event.edit("🔄 **جاري استعادة حسابك الأصلي يا عبود...**")
        
        try:
            # 1. استعادة الاسم والبايو
            await l313l(functions.account.UpdateProfileRequest(
                first_name=MY_DATA.get('first_name', 'Abod'),
                last_name=MY_DATA.get('last_name', ''),
                about=MY_DATA.get('about', '')
            ))
            
            # 2. استعادة الصورة الشخصية
            if MY_DATA.get('photo'):
                await l313l(UploadProfilePhotoRequest(file=await l313l.upload_file(MY_DATA['photo'])))
                if os.path.exists(MY_DATA['photo']):
                    os.remove(MY_DATA['photo'])
            
            MY_DATA.clear()
            await event.edit("✅ **تمت استعادة حسابك بنجاح.**")
            
        except Exception as e:
            await event.edit(f"❌ **فشل في الاستعادة:** `{str(e)}`")
