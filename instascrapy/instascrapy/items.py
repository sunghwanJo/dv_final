# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem

from instarank.models import InstaUser, Article


class InstaUserItem(DjangoItem):
    django_model = InstaUser

class ArticleItem(DjangoItem):
    django_model = Article
