import re
import pytz
import datetime
import platform
import requests
from newspaper import Article
from bs4 import BeautifulSoup
from readability.readability import Document as Paper
import random
user_agent_list = [
    #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

done = {}

def textgetter(url):
    """Scrapes web news and returns the content

    Parameters
    ----------

    url : str
        web address to news report

    Returns
    -------

    answer : dict
        Python dictionary with key/value pairs for:
            text (str) - Full text of article
            url (str) - url to article
            title (str) - extracted title of article
            author (str) - name of extracted author(s)
            base (str) - base url of where article was located
            provider (str) - string of the news provider from url
            published_date (str,isoformat) - extracted date of article
            top_image (str) - extracted url of the top image for article

    """
    global done
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'p', 'li']

    # regex for url check
    s = re.compile('(http://|https://)([A-Za-z0-9_\.-]+)')
    u = re.compile("(http://|https://)(www.)?(.*)(\.[A-Za-z0-9]{1,4})$")
    if s.search(url):
        site = u.search(s.search(url).group()).group(3)
    else:
        site = None
    answer = {}
    r = None
    # check that its an url
    if s.search(url):
        if url in done.keys():
            return done[url]
            pass
        try:
            # make a request to the url
            print("About to do Request")
            user_agent = random.choice(user_agent_list)
            r = requests.get(url, verify=False, timeout=100, headers={'User-Agent': user_agent})
            print("Request Complete! ")
        except Exception as e:
            print("exception")
            print(e)
            # print(e.message)
            # if the url does not return data, set to empty values
            done[url] = "Unable to reach website (exception)."
            answer['author'] = None
            answer['base'] = s.search(url).group()
            answer['provider'] = site
            answer['published_date'] = None
            answer['text'] = "Unable to reach website. (exception)."
            answer['title'] = None
            answer['top_image'] = None
            answer['url'] = url
            answer['keywords'] = None
            answer['summary'] = None
            return answer
        # if url does not return successfully, set ot empty values
        if r.status_code != 200:
            done[url] = "Unable to reach website (!200)."
            answer['author'] = None
            answer['base'] = s.search(url).group()
            answer['provider'] = site
            answer['published_date'] = None
            answer['text'] = "Unable to reach website (!200)."
            answer['title'] = None
            answer['top_image'] = None
            answer['url'] = url
            answer['keywords'] = None
            answer['summary'] = None

        # test if length of url content is greater than 500, if so, fill data
        if len(r.content) > 500:
            # set article url
            article = Article(url)
            # test for python version because of html different parameters
            if int(platform.python_version_tuple()[0]) == 3:
                article.download(input_html=r.content)
            elif int(platform.python_version_tuple()[0]) == 2:
                article.download(input_html=r.content)
            # parse the url
            article.parse()
            article.nlp()
            # if parse doesn't pull text fill the rest of the data
            if len(article.text) >= 200:
                answer['author'] = ", ".join(article.authors)
                answer['base'] = s.search(url).group()
                answer['provider'] = site
                answer['published_date'] = article.publish_date
                answer['keywords'] = article.keywords
                answer['summary'] = article.summary
                # convert the data to isoformat; exception for naive date
                if isinstance(article.publish_date, datetime.datetime):
                    try:
                        answer['published_date'] = article.publish_date.astimezone(pytz.utc).isoformat()
                    except:
                        answer['published_date'] = article.publish_date.isoformat()

                answer['text'] = article.text
                answer['title'] = article.title
                answer['top_image'] = article.top_image
                answer['url'] = url



            # if previous didn't work, try another library
            else:
                doc = Paper(r.content)
                data = doc.summary()
                title = doc.title()
                soup = BeautifulSoup(data, 'lxml')
                newstext = " ".join([l.text for l in soup.find_all(tags)])

                # as we did above, pull text if it's greater than 200 length
                if len(newstext) > 200:
                    answer['author'] = None
                    answer['base'] = s.search(url).group()
                    answer['provider'] = site
                    answer['published_date'] = None
                    answer['text'] = newstext
                    answer['title'] = title
                    answer['top_image'] = None
                    answer['url'] = url
                    answer['keywords'] = None
                    answer['summary'] = None
                # if nothing works above, use beautiful soup
                else:
                    newstext = " ".join([
                        l.text
                        for l in soup.find_all(
                            'div', class_='field-item even')
                    ])
                    done[url] = newstext
                    answer['author'] = None
                    answer['base'] = s.search(url).group()
                    answer['provider'] = site
                    answer['published_date'] = None
                    answer['text'] = newstext
                    answer['title'] = title
                    answer['top_image'] = None
                    answer['url'] = url
                    answer['keywords'] = None
                    answer['summary'] = None
        # if nothing works, fill with empty values
        else:
            answer['author'] = None
            answer['base'] = s.search(url).group()
            answer['provider'] = site
            answer['published_date'] = None
            answer['text'] = 'No text returned'
            answer['title'] = None
            answer['top_image'] = None
            answer['url'] = url
            answer['keywords'] = None
            answer['summary'] = None
            return answer
        return answer

    # the else clause to catch if invalid url passed in
    else:
        answer['author'] = None
        answer['base'] = s.search(url).group()
        answer['provider'] = site
        answer['published_date'] = None
        answer['text'] = 'This is not a proper url'
        answer['title'] = None
        answer['top_image'] = None
        answer['url'] = url
        answer['keywords'] = None
        answer['summary'] = None
        return answer
