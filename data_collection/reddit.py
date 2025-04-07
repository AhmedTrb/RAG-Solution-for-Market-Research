import praw
import pandas as pd
from datetime import datetime
import json
import argparse  
from dotenv import load_dotenv
import os
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv('clientid'),  
    client_secret=os.getenv('clientsecret'),
    user_agent=os.getenv('useragent'),
)

def scrape_reddit_posts(product_name, subreddit="all", limit=100):
    """
    Scrape Reddit for posts about a specific product
    """
    search_query = f"{product_name} product OR review OR opinion"
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
        csv_filename = f"reddit_data_{product_name.replace(' ', '_')}.csv"
        
        save_to_json(posts, json_filename)
        save_to_csv(posts, csv_filename)
        
        print(f"Saved {len(posts)} posts with comments to {json_filename} and {csv_filename}")
    else:
        print("No posts found for the given product.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Reddit for product discussions')
    parser.add_argument('--query', type=str, required=True, help='Product name to search for')
    parser.add_argument('--subreddit', type=str, default='all', help='Subreddit to search in (default: all)')
    
    args = parser.parse_args()
    main(product_name=args.query, subreddit=args.subreddit)