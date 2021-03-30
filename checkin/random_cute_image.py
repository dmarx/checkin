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

def random_cute_image_url():
    max_items = 100
    base_days = 30
    k = random.randint(0,7)
    i = random.randint(0,4)
    days_back = base_days+k
    sub = random.choice(cute_subs)

    gen = api.search_submissions(subreddit=sub, 
                                 before=f"{days_back}d", 
                                 sort_type='score')

    for j, p in enumerate(gen):
        
        # Check conditions
        cond1 = i >= j
        cond2a = any(p.url.endswith(suffix) for suffix in supported_extensions)
        cond2b = any(d in p.domain for d in whitelisted_domains)
        cond2 = cond2a or cond2b
        cond3 = not any(p.url.endswith(suffix) for suffix in extensions_blacklist)
        
        if all([cond1, cond2, cond3]):
            logger.debug(p)
            url = p.url
            if ('imgur' in p.domain) and (not cond2a):
                url += '.png'
            logger.info(url)
            return url
            
        if j > max_items:
            return None
