import time
import traceback
from chat_downloader.sites.facebook import FacebookChatDownloader
from logger import get_logger

logger = get_logger("Facebook")

def facebook_collector(url, msg_queue, is_running_func):
    logger.info(f"Facebook Collector started: {url}")
    
    # Normalize URL for chat-downloader's specific regex
    # The most reliable format for chat-downloader is the raw video ID or video.php?v=ID
    video_id = ""
    if url.isdigit():
        video_id = url
    elif "v=" in url:
        video_id = url.split("v=")[1].split("&")[0].split("/")[0]
    elif "/videos/" in url:
        # Matches https://www.facebook.com/TempTos1/videos/1314041977350733
        parts = url.split("/videos/")
        if len(parts) > 1:
            video_id = parts[1].split("/")[0].split("?")[0]
    
    if video_id:
        full_url = f"https://www.facebook.com/video.php?v={video_id}"
    else:
        full_url = url

    while is_running_func():
        try:
            # We use FacebookChatDownloader directly to bypass the library-level
            # "Site not supported" bug in the main ChatDownloader class.
            downloader = FacebookChatDownloader()
            chat = downloader.get_chat(full_url)
            for message in chat:
                if not is_running_func(): break
                author = message.get('author', {}).get('name', 'Unknown')
                text = message.get('message', '')
                msg_queue.put({"author": author, "message": text})
            if is_running_func(): time.sleep(5)
        except Exception as e:
            err_str = str(e)
            if "Unable to set datr cookie" in err_str:
                logger.error(f"Facebook Error: Connection blocked by Facebook. This is an anti-bot measure. Try again later or use a different IP/Proxy.")
            elif "Site not supported" in err_str:
                # This shouldn't happen anymore with direct class usage
                logger.error(f"Facebook Error: Library bug detected. Standard URL format rejected.")
            else:
                logger.error(f"Facebook Error: {e}")
            
            logger.debug(traceback.format_exc())
            if not is_running_func(): break
            time.sleep(15)
