import praw
import pandas as pd
from datetime import datetime
import json
from dotenv import load_dotenv
import os
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),  
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
)

def scrape_reddit_posts(product_name, subreddit="all", limit=100):
    """
    Scrape Reddit for posts about a specific product
    """
    search_query = f"{product_name} product OR review"
    posts = []
    
    for submission in reddit.subreddit(subreddit).search(search_query, limit=limit):
        post_data = {
            "title": submission.title,
            "author": str(submission.author),
            "score": submission.score,
            "id": submission.id,
            "url": submission.url,
            "num_comments": submission.num_comments,
            "created_utc": datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "selftext": submission.selftext,
            "subreddit": str(submission.subreddit),
            "comments": []  
        }
        posts.append(post_data)
    
    return posts  

def scrape_post_comments(post_id, limit=100):
    """
    Scrape comments from a specific Reddit post
    """
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=0)  
    
    comments = []
    for comment in submission.comments.list()[:limit]:
        comment_data = {
            "comment_id": comment.id,
            "author": str(comment.author),
            "score": comment.score,
            "created_utc": datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "body": comment.body,
            "parent_id": comment.parent_id
        }
        comments.append(comment_data)
    
    return comments

def save_to_json(data, filename):
    """
    Save data to a JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_csv(data, filename):
    """
    Save data to a CSV file
    """
    flattened_data = []
    for post in data:
        for comment in post['comments']:
            flattened_data.append({
                "Post Title": post['title'],
                "Post Author": post['author'],
                "Post Score": post['score'],
                "Post ID": post['id'],
                "Post URL": post['url'],
                "Post Num Comments": post['num_comments'],
                "Post Created UTC": post['created_utc'],
                "Post Subreddit": post['subreddit'],
                "Post Selftext": post['selftext'],
                "Comment ID": comment['comment_id'],
                "Comment Author": comment['author'],
                "Comment Score": comment['score'],
                "Comment Created UTC": comment['created_utc'],
                "Comment Body": comment['body'],
                "Comment Parent ID": comment['parent_id']
            })
    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False, encoding='utf-8')

def scrape_subreddit(
    subreddit_name: str,
    sort: str = 'hot',          # one of 'hot', 'new', 'top', 'controversial'
    post_limit: int = 100,
    comment_limit: int = 50,
    output_filename: str = None
):
    """
    Scrape posts + comments from a specific subreddit and save to JSON.

    Args:
        subreddit_name: e.g. "Python"
        sort: which listing to use; defaults to 'hot'
        post_limit: how many posts to fetch
        comment_limit: how many comments per post
        output_filename: where to save JSON; 
                         defaults to '{subreddit}_{sort}_{post_limit}posts.json'
    """
    print(f"→ Scraping r/{subreddit_name} [{sort}] – {post_limit} posts, {comment_limit} comments each")

    posts = []
    # dynamically grab the listing method: reddit.subreddit(...).hot(), .new(), .top(), etc.
    fetcher = getattr(reddit.subreddit(subreddit_name), sort)
    
    for submission in fetcher(limit=post_limit):
        post_data = {
            "title": submission.title,
            "author": str(submission.author),
            "score": submission.score,
            "id": submission.id,
            "url": submission.url,
            "num_comments": submission.num_comments,
            "created_utc": datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "selftext": submission.selftext,
            "subreddit": str(submission.subreddit),
            "comments": []  
        }

        # grab comments (uses your existing function)
        post_data['comments'] = scrape_post_comments(submission.id, limit=comment_limit)
        print(f"  • {submission.id}: fetched {len(post_data['comments'])} comments")
        posts.append(post_data)

    # default filename if none provided
    if not output_filename:
        output_filename = f"{subreddit_name}_{sort}_{post_limit}posts.json"

    save_to_json(posts, output_filename)
    print(f"✅ Saved {len(posts)} posts (with comments) to {output_filename}")



def main(product_name, subreddit="all"):
    print(f"Scraping posts about {product_name}...")
    posts = scrape_reddit_posts(product_name, subreddit=subreddit, limit=50)
    
    if posts:
        print(f"Found {len(posts)} posts. Now scraping comments...")
        for post in posts[:5]: 
            post_id = post['id']
            comments = scrape_post_comments(post_id, limit=100)
            post['comments'] = comments
            print(f"Scraped {len(comments)} comments for post: {post['title']}")
        
        json_filename = f"reddit_data_{product_name.replace(' ', '_')}.json"
        # csv_filename = f"reddit_data_{product_name.replace(' ', '_')}.csv"
        
        save_to_json(posts, json_filename)
        # save_to_csv(posts, csv_filename)
        
        print(f"Saved {len(posts)} posts with comments to {json_filename}")
    else:
        print("No posts found for the given product.")

if __name__ == "__main__":
    query = ""
    subreddit = "all"
    scrape_subreddit(
        subreddit_name="homesecurity",
        sort="top",
        post_limit=10,
        comment_limit=20
    )
    # main(product_name=query, subreddit=subreddit)