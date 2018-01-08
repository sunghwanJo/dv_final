# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from django.db import IntegrityError

from instarank.models import InstaUser


class InstascrapyPipeline(object):
    def process_item(self, item, spider):
        print('IN Pipeline')

        target = item.get('target')
        articles = item.get('articles')
        tag = target.tag
        followings = item.get('following')

        print('\tTarget : ', target)
        try:
            target.save()
        except IntegrityError as e:
            pass
        target = InstaUser.objects.filter(tag=tag).first()
        print('\t\t>>Process Target : ', target)

        if 'parent_tag' in item:

            parent_tag = item.get('parent_tag')
            parent = InstaUser.get_by_tag(parent_tag)
            if parent is not None:
                parent.following.add(target)
                print('\t\t>>Add Parent : ', parent)

        for article in articles:
            try:
                article = article.save(commit=False)
                article.user_id = target.id
                article.save()
            except IntegrityError as e:
                pass

        return item