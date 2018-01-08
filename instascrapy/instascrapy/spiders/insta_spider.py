from scrapy import Spider
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from ..util.InstagramCrawler import InstagramCrawler
from instasta.settings import BASE_DIR
from selenium.webdriver.chrome.options import Options

class InstaStaSpider(Spider):
    name = 'insta_sta'
    allowed_domains = ['https://www.instagram.com/']
    start_urls = ['https://www.instagram.com/']

    USER = 'namul10@gmail.com'
    PASSWORD = 'tjdghks2'

    TARGET_TAG = 'taeri__taeri'

    def __init__(self, *args, **kwargs):
        super(InstaStaSpider, self).__init__(*args, **kwargs)
        chromedriver_location = BASE_DIR + '/chromedriver'
        chrome_options = Options()
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_argument('headless')

        # managed_default_content_settings.images = 2: Disable images load,
        # this setting can improve pageload & save bandwidth
        # default_content_setting_values.notifications = 2:
        # Disable notifications
        # credentials_enable_service & password_manager_enabled = false:
        # Ignore save password prompt from chrome
        # 'profile.managed_default_content_settings.images': 2,
        # 'profile.default_content_setting_values.notifications' : 2,
        # 'credentials_enable_service': False,
        # 'profile': {
        #   'password_manager_enabled': False
        # }

        chrome_prefs = {
            'intl.accept_languages': 'en-US'
        }
        chrome_options.add_experimental_option('prefs', chrome_prefs)
        browser = webdriver.Chrome(chromedriver_location,
                                        chrome_options=chrome_options)

        self.insta_crawler = InstagramCrawler(browser)

    def parse(self, response):
        if self.insta_crawler.login(self.USER, self.PASSWORD):
            data = self.insta_crawler.target(self.TARGET_TAG)
            following = data['following']
            yield data
            for tag in following:
                try:
                    yield self.insta_crawler.target(tag, parent_tag=self.TARGET_TAG)
                except TimeoutException:
                    pass

    # return {'target': InstaUserItem(tag=self.target), 'articles': articles, 'followings': followings}
