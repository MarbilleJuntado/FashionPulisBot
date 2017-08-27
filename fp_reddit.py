import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from threading import Timer
import praw
import pdb
import re
import os

x = datetime.today()
y = x.replace(day=x.day+1, hour=6, minute=10, second=0, microsecond=0)
delta_t = y-x

secs = delta_t.seconds+1


def post():
    now = datetime.now()
    year = now.year
    month = "%02d" % now.month
    fp = "http://www.fashionpulis.com/{}/{}/".format(year, month) 
    # fp = "http://www.fashionpulis.com/2017/07"
    r = requests.get(fp)
    soup = BeautifulSoup(r.text, "html.parser")

    spec = re.compile("http://www\.fashionpulis\.com/{}/{}/".format(year, month))
    # spec = re.compile("http://www\.fashionpulis\.com/2017/07")
    article = soup.find('a', href=spec)['href']
    res = requests.get(article).text
    soup = BeautifulSoup(res, 'html.parser')
    for br in soup.findAll("br"):
        br.replaceWith("\n")

    content = ""
    for item in soup.findAll("div", class_=re.compile('post-body')):
        content += item.text

    title = soup.title.string[15:]
    content = content.strip()[35:]
    # print(title + "\n" + content)
    bi = title + "\n" + content

    # Create the Reddit instance
    reddit = praw.Reddit('bot1')

    # and login
    #reddit.login(REDDIT_USERNAME, REDDIT_PASS)

    # Have we run this code before? If not, create an empty list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []

    # If we have run the code before, load the list of posts we have replied to
    else:
        # Read the file into a list and remove any empty values
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    # Get the top 5 values from our subreddit
    subreddit = reddit.subreddit('Philippines')
    for submission in subreddit.new(limit=5):
        #print(submission.title)

        # If we haven't replied to this post before
        if submission.id not in posts_replied_to:

            # Do a case insensitive search
            if re.search("daily random discussion", submission.title, re.IGNORECASE):
                # Reply to the post
                submission.reply(bi)
                print("Bot replying to : ", submission.title)

                # Store the current id into our list
                posts_replied_to.append(submission.id)
                break

    # Write our updated list back to the file
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")

t = Timer(secs, post)
t.start()