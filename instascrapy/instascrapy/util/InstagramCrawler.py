from collections import defaultdict
import re

from selenium.webdriver import ActionChains

from instarank.models import InstaUser
from ..items import ArticleItem

try:
    from urlparse import urljoin
    from urllib import urlretrieve
except ImportError:
    from urllib.parse import urljoin
    from urllib.request import urlretrieve

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .util import sleep, format_number

# HOST
HOST = 'http://www.instagram.com/'

# SELENIUM XPATH SELECTOR
XPATH_SWITCH_LANGUAGE = "//footer[@class='_s5vm9']/div[@class='_g7lf5 _9z659']/nav[" \
                        "@class='_luodr']/ul[@class='_g8wl6']/li[@class='_538w0'][10]/" \
                        "span[@class='_pqycz _hqmnd']/select[@class='_fsoey']/option" \
                        "[text()='English']"
XPATH_LOGIN = "//article/div/div/p/a[text()='Log in']"
XPATH_LOGIN_USERNAME = "//input[@name='username']"
XPATH_LOGIN_PASSWORD = "//input[@name='password']"
XPATH_LOGIN_SUBMIT_BUTTON = "//form/span/button[text()='Log in']"
XPATH_LOAD_MORE = "//*[@id='react-root']/section/main/article/div[2]/a"

# CSS SELECTOR
CSS_SELECTOR_ARTICLES = "div[class='_70iju'] > div"
CSS_SELECTOR_TARGET_NAME = "h1[class='_kc4z2']"
CSS_SELECTOR_TARGET_IMAGE_SRC = "img[class='_9bt3u']"

# FOLLOWERS/FOLLOWING RELATED
CSS_FOLLOWERS = "a[href='/{}/followers/']"
CSS_FOLLOWING = "a[href='/{}/following/']"
FOLLOWER_PATH = "//div[contains(text(), 'Followers')]"
FOLLOWING_PATH = "//div[contains(text(), 'Following')]"

# JAVASCRIPT COMMANDS
SCROLL_UP = "window.scrollTo(0, 0);"
SCROLL_DOWN = "window.scrollTo(0, document.body.scrollHeight);"
SCROLL_DOWN_PARAM = "arguments[0].scrollTop = arguments[0].scrollHeight"
BACK = "window.history.go(-1)"

#CONSTANTS
FOLLOWERS = "followers"
FOLLOWING = "following"

class InstagramCrawler(object):
    def __init__(self, browser):
        self._browser = browser
        self._browser.implicitly_wait(10)
        self.data = defaultdict(list)
        self.current_url = None
        self.prev_url = None

    def login(self, username, password):
        self._browser.get(HOST)
        self._browser.find_element_by_xpath(XPATH_SWITCH_LANGUAGE).click()

        login_elem = self._browser.find_element_by_xpath(XPATH_LOGIN)
        if login_elem is not None:
            ActionChains(self._browser).move_to_element(login_elem).click().perform()

        input_username = self._browser.find_elements_by_xpath(XPATH_LOGIN_USERNAME)

        ActionChains(self._browser).move_to_element(input_username[0]).click().send_keys(username).perform()
        self._browser.implicitly_wait(1)
        input_password = self._browser.find_elements_by_xpath(XPATH_LOGIN_PASSWORD)
        ActionChains(self._browser).move_to_element(input_password[0]).click().send_keys(password).perform()

        login_button = self._browser.find_element_by_xpath(XPATH_LOGIN_SUBMIT_BUTTON)
        ActionChains(self._browser).move_to_element(login_button).click().perform()

        sleep(5)

        nav = self._browser.find_elements_by_xpath('//nav')
        if len(nav) == 2:
            return True
        else:
            return False

    def target(self, target_tag, parent_tag=None):
        print('TARGET : ', target_tag)
        self._browser.get(HOST + target_tag)
        self._browser.implicitly_wait(5)
        try:
            name = self._browser.find_element_by_css_selector(CSS_SELECTOR_TARGET_NAME).text
        except NoSuchElementException:
            name = ''

        profile_image_link = self._browser.find_element_by_css_selector(CSS_SELECTOR_TARGET_IMAGE_SRC).get_attribute('src')

        if parent_tag:
            self.data['parent_tag'] = parent_tag
        self.data['target'] = InstaUser(name=name, profile_image_link=profile_image_link, tag=target_tag)
        self.scrape_articles(100)
        self.scrape_followers_or_following(FOLLOWING, target_tag, 20)
        return self.data


    def _scroll_to_num_of_articles(self, number):
        num_info = re.search(r'\], "count": \d+', self._browser.page_source).group()
        num_of_articles = int(re.findall(r'\d+', num_info)[0])

        print("\tArticles: {}, number: {}".format(num_of_articles, number))
        # number = number if number < num_of_posts else num_of_posts

        self.more()

        num_to_scroll = int((number - 12) / 12) + 1
        for _ in range(num_to_scroll):
            self._browser.execute_script(SCROLL_DOWN)
            sleep(0.5)
            self._browser.execute_script(SCROLL_UP)
            sleep(0.2)

        return num_of_articles

    def more(self):
        try:
            more_elem = self._browser.find_element_by_xpath(XPATH_LOAD_MORE)
            ActionChains(self._browser).move_to_element(more_elem).click().perform()
            sleep(1)
        except NoSuchElementException:
            return

    def quit(self):
        self._browser.quit()

    def scrape_followers_or_following(self, crawl_type, target_tag, number):
        self._browser.execute_script(SCROLL_UP)
        print("Scraping {}...".format(crawl_type))
        if crawl_type == "followers":
            FOLLOW_ELE = CSS_FOLLOWERS
            FOLLOW_PATH = FOLLOWER_PATH
        elif crawl_type == "following":
            FOLLOW_ELE = CSS_FOLLOWING
            FOLLOW_PATH = FOLLOWING_PATH

        follow_ele = WebDriverWait(self._browser, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, FOLLOW_ELE.format(target_tag)))
        )

        total = int(''.join(filter(lambda x: x.isdigit(), str(follow_ele.text))))
        if total < number:
            number = total

        follow_ele.click()

        dialog = self._browser.find_element_by_xpath(FOLLOW_PATH+'/following-sibling::div')
        follow_list = dialog.find_element_by_tag_name('ul')
        follow_list.click()
        num_of_shown_follow = 0
        while num_of_shown_follow < number:
            num_of_shown_follow = len(dialog.find_elements_by_class_name('_2nunc'))
            self._browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
            sleep(1)
            print("\t{}/{} ({}%)".format(num_of_shown_follow, number, int(num_of_shown_follow/float(number) *100)))
        follow_items = []
        for ele in dialog.find_elements_by_class_name('_2nunc')[:number]:
            follow_items.append(ele.text.split('\n')[0])
        self.data[crawl_type] = follow_items

    def scrape_articles(self, number):
        print('Scraping articles...')

        num_of_articles = self._scroll_to_num_of_articles(number)

        content_divs = self._browser.find_elements_by_css_selector(CSS_SELECTOR_ARTICLES)

        articles = []
        for item in content_divs[:num_of_articles]:
            link = item.find_element_by_xpath('.//a').get_attribute('href')
            img = item.find_element_by_xpath('.//a/div/div/img').get_attribute('src')
            content = item.find_element_by_xpath('.//a/div/div/img').get_attribute('alt')
            ActionChains(self._browser).move_to_element(item).perform()
            sleep(0.1)
            CSS_SELECTOR_COMMENTS_LIKES = "div[class='_mli86']"
            comments_likes = self._browser.find_element_by_css_selector(CSS_SELECTOR_COMMENTS_LIKES)
            try:
                comments = format_number(comments_likes.find_elements_by_css_selector('span')[0].text)
            except IndexError:
                comments = 0
            try:
                likes = format_number(comments_likes.find_elements_by_css_selector('span')[2].text)
            except IndexError:
                likes = 0



            articles.append(ArticleItem(link=link, image_link=img, content=content, comment_count=comments, likes=likes))

        # for index, article in enumerate(articles):
        #     self._browser.get(link)
        #     self._browser.implicitly_wait(3)
        #     likes = self.format_number(self._browser.find_element_by_css_selector(CSS_SELECTOR_ARTICLE_LIKES).text)
        #     self._browser.execute_script(BACK)
        #     articles[index]['like'] = likes
        #     articles.append(ArticleItem(link=link, image_link=img, content=content, likes=likes))


        self.data["articles"] = articles
        return articles
