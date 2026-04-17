from telethon import events, Button

try:
    import l313l
    client = l313l.l313l
except:
    from .. import l313l as client

@client.on(events.NewMessage(pattern="/start", incoming=True))
async def bot_start(event):
    if event.is_private:
        await event.reply("**مرحباً بك في بوت مساعد عبود ✅**", 
            buttons=[[Button.url("المطور", url="https://t.me/BD_0I")]])
