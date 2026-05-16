import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
from logger import get_logger

logger = get_logger("TikTok")

def tiktok_collector(username, msg_queue, is_running_func):
    logger.info(f"TikTok Collector started: {username}")
    
    # Clean username if URL was provided
    if "tiktok.com/@" in username:
        username = username.split("@")[-1].split("/")[0].split("?")[0]
    elif username.startswith("@"):
        username = username[1:]

    async def run_tiktok():
        while is_running_func():
            try:
                client = TikTokLiveClient(unique_id=username)

                @client.on("comment")
                async def on_comment(event: CommentEvent):
                    try:
                        if not is_running_func():
                            await client.stop()
                            return
                        msg_queue.put({"author": event.user.nickname, "message": event.comment})
                    except Exception as e:
                        if "'str' object has no attribute 'get_type'" in str(e):
                            pass # Ignore this specific internal library error during parsing
                        else:
                            logger.error(f"TikTok Comment Error: {e}")

                @client.on("disconnect")
                async def on_disconnect(event):
                    logger.warning("TikTok disconnected. Reconnecting...")

                await client.start()
            except Exception as e:
                if "'str' object has no attribute 'get_type'" in str(e):
                    logger.error(f"TikTok Error: {e} (This is a known library bug, retrying...)")
                else:
                    logger.error(f"TikTok Error: {e}")
                
                if not is_running_func(): break
                await asyncio.sleep(10)

    asyncio.run(run_tiktok())
