import time
import configparser
from engine import ChatTTSEngine
from logger import get_logger

logger = get_logger("IntegrationTest")

def run_full_test():
    # Simulate the GUI starting the engine with all platforms enabled
    test_settings = {
        'voice': 'th-TH-PremwadeeNeural',
        'delay_per_char': '0.03',
        'max_delay': '2.0',
        'auto_translate': 'True',
        'yt_enabled': 'True',
        'yt_id': 'HZyLkj3to6o', # From user's config
        'fb_enabled': 'True',
        'fb_url': 'https://www.facebook.com/TempTos1/videos/1314041977350733',
        'tw_enabled': 'True',
        'tw_channel': 'tditbam',
        'tk_enabled': 'True',
        'tk_username': '@mr.sweet_eggs'
    }
    
    engine = ChatTTSEngine()
    logger.info(">>> STARTING FULL SYSTEM INTEGRATION TEST <<<")
    logger.info("Enabling all platforms: YouTube, Facebook, Twitch, TikTok")
    
    engine.start(test_settings)
    
    # Run for 20 seconds to allow all collectors to attempt connection and retry
    logger.info("System running... monitoring collectors for 20 seconds...")
    time.sleep(20)
    
    logger.info(">>> INTEGRATION TEST COMPLETE. STOPPING ENGINE <<<")
    engine.stop()
    time.sleep(2)

if __name__ == "__main__":
    run_full_test()
