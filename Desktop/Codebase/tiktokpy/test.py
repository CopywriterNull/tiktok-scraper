import csv
import os
from tikapi import TikAPI, ValidationException, ResponseException

API_KEY = 'dt3MtdduCuz7vd6FZp9GwOQIPiIH1sML7nX37g1rGWruvijm'
ACCOUNT_KEY = 'qT5cC5QiQSDLWIXpf3mzkPYCdllf8L3bxqsdpT6KETM4l7RUvf'

api = TikAPI(API_KEY)
account = TikAPI(ACCOUNT_KEY)

# Function to check username and get user info
def check_username(username):
    try:
        response = api.public.check(username=username)
        user_info = response.json().get('userInfo', {})
        user = user_info.get('user', {})
        stats = user_info.get('stats', {})
        
        # Collect required fields
        user_data = {
            'Username': user.get('uniqueId', ''),
            'Name': user.get('nickname', ''),
            'Followers': stats.get('followerCount', 0),
            'Following': stats.get('followingCount', 0),
            'Likes': stats.get('heartCount', 0),
            'Videos': stats.get('videoCount', 0),
        }
        
        sec_uid = user.get('secUid')
        if sec_uid:
            print(f"secUid for {username}: {sec_uid}")
            return sec_uid, user_data
        else:
            print(f"No secUid found for {username}")
            return None, None
    except ValidationException as e:
        print(e, e.field)
    except ResponseException as e:
        print(e, e.response.status_code)
    return None, None

# Function to get posts using secUid and calculate averages
def get_posts(sec_uid):
    try:
        response = api.public.posts(secUid=sec_uid)
        data = response.json()
        
        if 'itemList' in data:
            collect_counts = []
            comment_counts = []
            digg_counts = []
            play_counts = []
            share_counts = []
            
            # Process posts 4 to 12 (index 3 to 11)
            for i, item in enumerate(data['itemList']):
                if i < 3:
                    continue  # Skip the first 3 videos
                if i > 11:
                    break  # Stop after the 12th video
                
                stats = item.get('stats', {})
                collect_counts.append(stats.get('collectCount', 0))
                comment_counts.append(stats.get('commentCount', 0))
                digg_counts.append(stats.get('diggCount', 0))
                play_counts.append(stats.get('playCount', 0))
                share_counts.append(stats.get('shareCount', 0))

            # Calculate averages
            avg_collect = sum(collect_counts) // len(collect_counts) if collect_counts else 0
            avg_comment = sum(comment_counts) // len(comment_counts) if comment_counts else 0
            avg_digg = sum(digg_counts) // len(digg_counts) if digg_counts else 0
            avg_play = sum(play_counts) // len(play_counts) if play_counts else 0
            avg_share = sum(share_counts) // len(share_counts) if share_counts else 0
            
            # Calculate average views for posts 4 to 12
            avg_views_4_to_12 = sum(play_counts) // len(play_counts) if len(play_counts) >= 9 else 0
            
            print(f"\nAverages for secUid: {sec_uid}")
            print(f"  Average Collect Count: {avg_collect}")
            print(f"  Average Comment Count: {avg_comment}")
            print(f"  Average Digg Count: {avg_digg}")
            print(f"  Average Play Count: {avg_play}")
            print(f"  Average Share Count: {avg_share}")
            print(f"  Average Views (posts 4-12): {avg_views_4_to_12}")
            
            return {
                'Avg. Saves': avg_collect,
                'Avg. Comments': avg_comment,
                'Avg. Likes': avg_digg,
                'Avg. Views': avg_play,
                'Avg. Shares': avg_share,
                'Avg. Views (4-12)': avg_views_4_to_12,
                'Saves': collect_counts,
                'Comments': comment_counts,
                'Likes': digg_counts,
                'Views': play_counts,
                'Shares': share_counts
            }
        else:
            print(f"No items found for secUid: {sec_uid}")
            return None
    except ValidationException as e:
        print(e, e.field)
    except ResponseException as e:
        print(e, e.response.status_code)
        return None

# Read usernames from CSV and process each one
csv_file = 'usernames.csv'  # Replace with the path to your CSV file
output_file = 'user_stats.csv'

# Check if the output file already exists
file_exists = os.path.isfile(output_file)

with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    with open(output_file, mode='a', newline='', encoding='utf-8') as outfile:
        fieldnames = ['Username', 'Name', 'Followers', 'Following', 'Likes', 'Videos',
                      'Avg. Saves', 'Avg. Comments', 'Avg. Likes', 'Avg. Views', 'Avg. Shares',
                      'Avg. Views (4-12)',  # New field for average views of posts 4-12
                      'Saves', 'Comments', 'Likes', 'Views', 'Shares']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        # Write headers only if the file does not exist or is empty
        if not file_exists or os.stat(output_file).st_size == 0:
            writer.writeheader()
        
        for row in reader:
            username = row[0]  # Assuming the username is in the first column
            sec_uid, user_data = check_username(username)
            if sec_uid:
                post_data = get_posts(sec_uid)
                if post_data:
                    combined_data = {**user_data, **post_data}
                    writer.writerow(combined_data)
