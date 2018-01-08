from operator import itemgetter

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import InstaUser
from konlpy.tag import Twitter

from gensim.models import word2vec
import json
import os
from instasta.settings import BASE_DIR

word_model = word2vec.Word2Vec.load(os.path.join(BASE_DIR, 'instarank.model'))


def home(request):
    user_list = InstaUser.objects.all()
    context = {'user_list': user_list}
    return render(request, 'index.html', context)


def results(request, tag):
    import jpype
    if jpype.isJVMStarted():
        jpype.attachThreadToJVM()

    twitter = Twitter()
    user = get_object_or_404(InstaUser, tag=tag)
    word_dic = {}
    results = ""

    articles = user.articles.all()
    article_size = len(articles)
    for article in articles:
        malist = twitter.pos(article.content)
        for word in malist:
            if word[1] == 'Noun':
                if not (word[0] in word_dic):
                    word_dic[word[0]] = 0
                word_dic[word[0]] += 1

    keys = sorted(word_dic.items(), key=lambda x: x[1], reverse=True)
    for word, count in keys:
        results += "{0}({1})".format(word, count) + "\n"

    similar_images = user.find_similar_image()

    user_data = {
        'article_size': article_size,
        'user_profile_image': user.profile_image_link,
        'similar_images_size': len(similar_images),
        'similar_images': similar_images,
    }

    context = {'words': results, 'user_data': user_data}
    return render(request, 'results.html', context)


def predict(url, top_n=3):
    from PIL import Image
    from keras.applications.resnet50 import ResNet50
    from keras.preprocessing import image
    from keras.applications.resnet50 import preprocess_input, decode_predictions
    import numpy as np
    import requests
    from io import BytesIO

    response = requests.get(url)
    try:
        img = Image.open(BytesIO(response.content))

        target_size = ((224, 224))

        model = ResNet50(weights='imagenet')
        if img.size != target_size:
            img = img.resize(target_size)

        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x)

        return decode_predictions(preds, top=top_n)[0][0][1]
    except OSError:
        return ''


# from instarank.views import predict
# from instarank.models import Article
# predict(Article.objects.first().image_link)
#
# for index, article in enumerate(articles):
#     print(index)
#     article.image_label = predict(article.image_link)
#     article.save()

def get_words(articles):
    import jpype
    if jpype.isJVMStarted():
        jpype.attachThreadToJVM()

    twitter = Twitter()
    word_dic = {}

    for article in articles:
        malist = twitter.pos(article.content)
        for word in malist:
            if word[1] == 'Noun':
                if not (word[0] in word_dic):
                    word_dic[word[0]] = 0
                word_dic[word[0]] += 1

    return sorted(word_dic.items(), key=lambda x: x[1], reverse=True)[:5]


def get_text_similarity_index(user_word_list, other_word_list):
    tsi_sum = 0
    n = len(user_word_list)
    for i, (word, _) in enumerate(user_word_list):
        for j, (other_word, _) in enumerate(other_word_list):
            try:
                tsi_sum += (n - i + 1) * (n - j + 1) * word_model.similarity(word, other_word)
            except KeyError:
                tsi_sum = 0
    return tsi_sum


def analysis_user(request, tag):
    user = get_object_or_404(InstaUser, tag=tag)
    articles = user.articles.all()

    # 유저의 상위 5개
    user_words = get_words(articles)

    followings_data = []
    tsi_list = []
    for following_user in user.following.all():
        f_user_tag = following_user.tag
        f_user_word = get_words(following_user.articles.all())
        tsi = get_text_similarity_index(user_words, f_user_word)
        tsi_list.append(tsi)
        followings_data.append({
            'tag': f_user_tag,
            'profile_image': following_user.profile_image_link,
            'words': f_user_word,
            'word_label': [i[0] for i in f_user_word],
            'word_data': [i[1] for i in f_user_word],
            'tsi': tsi
        })

    user_data = {
        'words': user_words,
        'word_label': [i[0] for i in user_words],
        'word_data': [i[1] for i in user_words],
        'tag': user.tag,
        'profile_image': user.profile_image_link
    }
    similar_user = sorted(followings_data, key=itemgetter('tsi'), reverse=True)[0]

    data = {
        'user': user_data,
        'similar_user': similar_user,
        'tsi_ratio': float(similar_user['tsi'])/400
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
