from konlpy.tag import Twitter
from gensim.models import word2vec
from instarank.models import Article


def article_word_to_vec():
    import jpype
    if jpype.isJVMStarted():
        jpype.attachThreadToJVM()

    twitter = Twitter()
    lines = []
    results = []
    for article in Article.objects.all():
        lines += article.content.split("\n")

    for line in lines:
        malist = twitter.pos(line, norm=True, stem=True)
        r = []
        for word in malist:
            if not word[1] in ['Josa', 'Eomi', 'Punctuation']:
                r.append(word[0])

        rl = (" ".join(r)).strip()
        results.append(rl)
        print(rl)

    wakati_file = 'instarank.wakati'
    with open(wakati_file, 'w', encoding='utf-8') as fp:
        fp.write("\n".join(results))

    data = word2vec.LineSentence(wakati_file)
    model = word2vec.Word2Vec(data, size=200, window=10, hs=1, min_count=2, sg=1)
    model.save("instarank.model")


from PIL import Image
import numpy as np
import requests

def average_hash(image_link, size=16):
    img = Image.open(requests.get(image_link, stream=True).raw)
    img = img.convert('L').resize((size, size), Image.ANTIALIAS)
    pixels = np.array(img.getdata()).reshape((size, size))
    avg = pixels.mean()
    px = 1 * (pixels > avg)

    return (px, img)

def hamming_dist(a, b):
    aa = a.reshape(1, -1)  # 1차원 배열로 변환하기
    ab = b.reshape(1, -1)
    dist = (aa != ab).sum()
    return dist

def find_image(user_profile_link, article_image_links, rate):
    src, src_img = average_hash(user_profile_link)
    for link in article_image_links:
        try:
            dst, dst_img = average_hash(link)
            diff_r = hamming_dist(src, dst) / 256
            print(diff_r)
            if diff_r < rate:
                yield (diff_r, link)
        except OSError as e:
            print('OSError')

# from instarank.models import InstaUser
# InstaUser.objects.first().find_similar_image()
