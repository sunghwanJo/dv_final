from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class InstaUser(models.Model):
    """
    - id: String
	- profile_image_link: String
	- tag: String
	- follower: List<User>
	- following: List<User>
	- article: List<Article>
    """
    name = models.CharField(max_length=256, default='')
    tag = models.CharField(max_length=256, unique=True)
    following = models.ManyToManyField('self')
    profile_image_link = models.CharField(max_length=256, default='')

    @classmethod
    def get_by_tag(cls, tag):
        try:
            return InstaUser.objects.get(tag=tag)
        except ObjectDoesNotExist as e:
            return None

    def find_similar_image(self):
        from .utils import find_image
        sim = list(find_image(self.profile_image_link, list(self.get_article_links()),0.4))
        sim = sorted(sim, key=lambda x: x[0])
        # print('print sim')
        # print(sim)
        # for r, f in sim:
        #     print(r, ">", f)

        return sim

    def get_article_links(self):
        for article in self.articles.all():
            yield article.image_link

    def get_top_3_word(self):
        pass

    def __str__(self):
        return "{}({})".format(self.tag, self.id)

class Article(models.Model):
    """
    # - image_link: String
	# - like_count: Int
	# - content: String
	# - comment: (User, String)

	# + link
    """
    user = models.ForeignKey(InstaUser, related_name='articles', on_delete=models.CASCADE)
    link = models.CharField(max_length=256, unique=True)
    image_link = models.CharField(max_length=256, default='')
    content = models.CharField(max_length=256, default='')
    likes = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    image_label = models.CharField(max_length=256, default='')

    def __str__(self):
        return "[{}] {}".format(self.image_label, self.content)

    @classmethod
    def make_model(cls):
        from .utils import article_word_to_vec
        article_word_to_vec()