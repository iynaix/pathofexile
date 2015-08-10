# Scrapy settings for poe project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'poe'

SPIDER_MODULES = ['poe.spiders']
NEWSPIDER_MODULE = 'poe.spiders'

# HTTPCACHE_ENABLED = True
# cache for a day
# HTTPCACHE_EXPIRATION_SECS = 24 * 60 * 60
# RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 403]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'poe (+http://www.yourdomain.com)'
