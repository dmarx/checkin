import psaw
import random
from loguru import logger

api = psaw.PushshiftAPI()

#https://www.reddit.com/subreddits/mine/
cute_subs = ['aww', 
             'eyebleach', 
             'rarepuppers', 
             'pitbulls', 
             'dogs', 
             'AnimalsBeingDerps',
             'AmStaffPitts',
             'pitbullsinjammies',
             'dogsusingpillows',
             'AnimalsBeingDerps',
             'AnimalsBeingSleepy',
             'cromch',
             'derp',
             'dogswearinghats',
             'happydogs',
             'mlem',
             'puppysmiles',
             'tinyunits',
             'tripawds',
             'WhatsWrongWithYourDog'
            ]

supported_extensions = [
    '.png',
    '.gif',
    #'.gifv', probably needs to get embedded in an iframe?
    '.jpg',
    '.jpeg'
]

whitelisted_domains = [
    #'gfycat', ... # https://developers.gfycat.com/iframe/#simple-iframe-player
    'imgur'
]

extensions_blacklist = [
    '.gifv'
]

async def random_cute_image_url(sub=None):
    max_items = 100
    base_days = 30
    #k = random.randint(0,7)
    k = random.randint(0,335)
    #i = random.randint(0,4)
    i = 0
    days_back = base_days+k
    if sub is None:
        sub = random.choice(cute_subs)
    assert sub is not None
    logger.debug(sub)
    logger.debug(days_back)
    gen = api.search_submissions(subreddit=sub, 
                                 before=f"{days_back}d", 
                                 after=f"{days_back+1}d", # top posts for a given day 
                                 sort_type='score')

    for j, p in enumerate(gen):
        logger.debug((j, p.url))
        # Check conditions
        cond1 = (j >= i)
        cond2a = any(p.url.endswith(suffix) for suffix in supported_extensions)
        cond2b = any(d in p.domain for d in whitelisted_domains)
        cond2 = cond2a or cond2b
        cond3 = not any(p.url.endswith(suffix) for suffix in extensions_blacklist)
        logger.debug((cond1, cond2, cond3))
        logger.debug((cond2a, cond2b))
        if all([cond1, cond2, cond3]):
            #logger.debug(p)
            logger.debug(f"Satisfactory canddiate URL found after {j} iterations")
            url = p.url
            #if ('imgur' in p.domain) and (not cond2a):
            #    url += '.png'
            logger.info(url)
            logger.info(p.title)
            return url
            
        if j > max_items:
            logger.warning(f"Max items exceeded ({max_items}) without encountering a viable candidate URL.")
            return None
