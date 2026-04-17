import asyncio, speedtest
from telethon import events
import database

def setup(l313l):
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"\.فحص النت"))
    async def test_speed(event):
        database.update_stats("فحص_السرعة")
        await event.edit("⚡ **جاري فحص السرعة...**")
        loop = asyncio.get_event_loop()
        s = await loop.run_in_executor(None, speedtest.Speedtest)
        await loop.run_in_executor(None, s.get_best_server)
        download = await loop.run_in_executor(None, s.download)
        upload = await loop.run_in_executor(None, s.upload)
        res = f"⬇️ التحميل: `{round(download/1e6, 2)} Mbps`\n⬆️ الرفع: `{round(upload/1e6, 2)} Mbps`"
        await event.edit(f"✅ **نتائج الفحص:**\n{res}")
