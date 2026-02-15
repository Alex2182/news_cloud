import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np
from newsapi import NewsApiClient
# from translate import Translator
import json
# with open('news/stopwords-iso.json','r') as f:
#     stop = json.load(f)
with open('stopwords-iso.json','r') as f:
    stop = json.load(f)

# translator= Translator(to_lang="ru")
# Init
newsapi = NewsApiClient(api_key='GET_YOUR OWN_API_KEY_https://newsapi.org/')
ru_stop = stop['ru']+['в','на','за','с','из','не','о','к','что','по','сообщили','и','И','СМИ','пишут','более','еще','без','В','сообщили'
        'сделали','заявление','заявили','рассказали','заявил','над','Над','под','Под','заявила','рассказала',
       'для','Для','об','тоже','рассказал','при','При','после','во','Во','его','до','у','от','как','Как','Когда','когда','со']
en_stop=stop['en']+['BBC.com','NBC','News','Reuters','Al','Jazeera','CBS','CNN','Removed']
# ru_mask = np.array(Image.open("news/head.jpg"))
# en_mask=np.array(Image.open("news/head_flop.jpg"))
# mask_ru=np.array(Image.open("news/ru.jpg"))
# mask_en=np.array(Image.open("news/usa.jpg"))
ru_mask = np.array(Image.open("head.jpg"))
en_mask=np.array(Image.open("head_flop.jpg"))
mask_ru=np.array(Image.open("ru.jpg"))
mask_en=np.array(Image.open("usa.jpg"))

rss = 'https://ria.ru/export/rss2/archive/index.xml'

def get_date_id(url: str):
    l = url.split('/')
    return l[3],l[4].split('-')[1].replace('.html','')
def get_emoji(link: str):
    date,id=get_date_id(link)
    r = requests.get(f'https://ria.ru/services/dynamics/{date}/{id}.html')
    soup = BeautifulSoup(r.text)
    views = soup.find("span",class_='article__views').text.split("\n")[0]
    emoji = {}
    emoji_list = soup.find_all("a",class_="emoji-item")
    # print(soup.title.text)
    for i in emoji_list:
        emoji.update({i.attrs['data-type']: int(i.text)})
    emoji.update({'views': int(views)})
    return emoji
def get_us_news():
    usa = pd.DataFrame()
    # top_headlines = 's'
    page=1
    while True:
        try:
            top_headlines = newsapi.get_top_headlines( # sources='bbc-news,the-verge',
                                          # category='business',
                                          # language='en',
                                          country='us',
                                          page=page)
            usa = pd.concat([usa,pd.DataFrame(top_headlines['articles'])],ignore_index=True)
            page += 1
        except Exception as err:
            # usa['title2']=usa.title.apply(lambda x: translator.translate(x.split('-')[0].strip()))
            usa['title2']=usa.title.apply(lambda x: x.split('-')[0].strip())
            # return usa.title2.to_list()
            return ' '.join(usa.title2.to_list())
def get_ru_news():
    df = pd.read_xml(rss,xpath='.//item')
    df2=df #.tail(20)
    # df2['emoji']=df2.link.apply(get_emoji)
    # df2['s1']=df2.emoji.apply(lambda x: x.get('s1'))
    # df2['s6']=df2.emoji.apply(lambda x: x.get('s6'))
    # df2['s2']=df2.emoji.apply(lambda x: x.get('s2'))
    # df2['s3']=df2.emoji.apply(lambda x: x.get('s3'))
    # df2['s4']=df2.emoji.apply(lambda x: x.get('s4'))
    # df2['s5']=df2.emoji.apply(lambda x: x.get('s5'))
    # df2['views']=df2.emoji.apply(lambda x: x.get('views'))
    # df2['feedbacks'] = df2['s1'] + df2['s2'] + df2['s3'] + df2['s4'] + df2['s5'] + df2['s6']
    # df2['f_per_v'] = df2['feedbacks']/df2['views']*100
    # wordcloud generate
    # wordcloud = ' '.join(df2.sort_values('f_per_v',ascending=False).head(20)['title'].to_list())
    return  ' '.join(df2['title'].to_list())
def get_wordcloud(text,stopwords,max_words,mask,font_size):
    return WordCloud(stopwords=stopwords,
               max_font_size=font_size,
               background_color="white",
               mask=mask,
               # contour_width=1,
               # contour_color='steelblue',
               max_words=max_words).generate(text)

def gen_news():
    wc=get_wordcloud(get_ru_news(),ru_stop,2000,ru_mask,100)
    color = ImageColorGenerator(mask_ru)
    wc.recolor(color_func=color)
    # wc.to_file('news/full_head.jpg')
    wc.to_file('full_head.jpg')

    wc = get_wordcloud(get_us_news(),en_stop+['Removed','Удалено'],2000,en_mask,100)
    color = ImageColorGenerator(mask_en)
    wc.recolor(color_func=color)
    # wc.to_file('news/full_head_usa.jpg')
    wc.to_file('full_head_usa.jpg')

    # images = [Image.open(x) for x in ['news/full_head_usa.jpg', 'news/full_head.jpg']]
    images = [Image.open(x) for x in ['full_head_usa.jpg', 'full_head.jpg']]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]

    # new_im.save('news/news.jpg')
    new_im.save('news.jpg')
    return 'Done'

if __name__ == "__main__":
    gen_news()
