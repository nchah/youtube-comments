#!/usr/bin/env python3

import argparse
from collections import OrderedDict
import csv
import datetime
import requests

"""
Running:
$ python3 youtube-api.py [input_file OR video_id]

"""

# Globals: API key
api_key = open('.api_key').read().strip()
quota_counter = 100000

"""
* * Sample request:

GET https://www.googleapis.com/youtube/v3/commentThreads?
part=snippet%2Creplies
&maxResults=100
&order=relevance
&pageToken=[long_text_string]
&videoId=srXsCRnSgBA
&key={YOUR_API_KEY}

* * Response structure:

{
 "kind": "youtube#commentThreadListResponse",
 "etag": "\"I_8xdZu766_FSaexEaDXTIfEWc0/IiDEZQ7_qegXjFH-cMADT2bWo0s\"",
 "nextPageToken": '...'
 "pageInfo": {
  "totalResults": 100,
  "resultsPerPage": 100
 },
 "items": [
  {
   "kind": "youtube#commentThread",
   "etag": "\"I_8xdZu766_FSaexEaDXTIfEWc0/W5uUBQboigHpYX84pcPhDHnm46g\"",
   "id": "z12tfd0wpun0ufjmv22zxpkg3pujhf43x",
   "snippet": {
    "videoId": "srXsCRnSgBA",
    "topLevelComment": {
     "kind": "youtube#comment",
     "etag": "\"I_8xdZu766_FSaexEaDXTIfEWc0/qSRyuWb813c3YJG_X10Tmw-13rc\"",
     "id": "z12tfd0wpun0ufjmv22zxpkg3pujhf43x",
     "snippet": {
      "authorDisplayName": "euphtygrit",
      "authorProfileImageUrl": "https://lh6.googleusercontent.com/...",
      "authorChannelUrl": "http://www.youtube.com/channel/UCYFydhhHbFNXnSGwjhGucGA",
      "authorChannelId": {
       "value": "UCYFydhhHbFNXnSGwjhGucGA"
      },
      "videoId": "srXsCRnSgBA",
      "textDisplay": "...\ufeff",
      "canRate": true,
      "viewerRating": "none",
      "likeCount": 121,
      "publishedAt": "2016-07-02T16:00:19.000Z",
      "updatedAt": "2016-07-02T16:00:19.000Z"
     }
    },
    "canReply": true,
    "totalReplyCount": 5,
    "isPublic": true
   },
   "replies": {
    "comments": [
     {
      "kind": "youtube#comment",
      "etag": "\"I_8xdZu766_FSaexEaDXTIfEWc0/btEd5iIPkf75Yj6LXsVAXP2iLdA\"",
      "id": "z12tfd0wpun0ufjmv22zxpkg3pujhf43x.1473421938255174",
      "snippet": {
       "authorDisplayName": "박지열",
       "authorProfileImageUrl": "https://lh4.googleusercontent.com/...",
       "authorChannelUrl": "http://www.youtube.com/channel/UCxK7Lmmsa-evY3ZM61dpXmg",
       "authorChannelId": {
        "value": "UCxK7Lmmsa-evY3ZM61dpXmg"
       },
       "videoId": "srXsCRnSgBA",
       "textDisplay": "...",
       "parentId": "z12tfd0wpun0ufjmv22zxpkg3pujhf43x",
       "canRate": true,
       "viewerRating": "none",
       "likeCount": 2,
       "publishedAt": "2016-09-09T11:52:18.000Z",
       "updatedAt": "2016-09-09T11:52:18.000Z"
      }
     },
     {...more replies...}
     }
    ]
   }
  }, ...
}
"""


def timestamp_to_utc(timestamp):
    """Convert unix timestamp to UTC date
    :param timestamp: int - the unix timestamp integer
    :return: utc_data - the date in YYYY-MM-DD format
    """
    timestamp = int(str(timestamp)[0:10])
    utc_date = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    return utc_date


# TODO: revise and refactor
def store_csv(video_id, json_response):
    """Store the traffic stats as a CSV, with schema (refer to main()).

    """
    dates_and_views = OrderedDict()
    detailed_views = json_response['views']
    for row in detailed_views:
        utc_date = timestamp_to_utc(int(row['timestamp']))
        dates_and_views[utc_date] = (str(row['count']), str(row['uniques']))

    # Starting up the CSV, writing the headers in a first pass
    current_timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d-%Hh-%Mm'))  # was .strftime('%Y-%m-%d'))
    csv_file_name = 'data/' + current_timestamp + '-traffic-stats.csv'

    for i in dates_and_views:
        row = [repo_name, i, dates_and_views[i][0], dates_and_views[i][1]]
        with open(csv_file_name, 'a') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(row)

    return ''


def send_request(resource, query_volume, video_id, part, max_results, order_by='relevance'):
    """
    :param resource: 'commentThreads' - only this for now
    :param query_volume: 'all' or 'once' - set to 'all' to get all comments
    :param video_id:
    :param part:
    :param max_results:
    :param order_by:
    :return:
    """
    if resource == 'commentThreads':
        # GET https://www.googleapis.com/youtube/v3/commentThreads?
        # ^ from https://developers.google.com/youtube/v3/guides/implementation/comments
        base_url = 'https://www.googleapis.com/youtube/v3/commentThreads'
        payload = {
            'part': part,
            'maxResults': max_results,
            'order': order_by,
            'videoId': video_id,
            'key': api_key
        }
        response = requests.get(base_url, params=payload)
        response_json = response.json()

        comments_list = []
        # print(len(comments_list) + 1)  # debug

        if query_volume == 'once' or response_json.get('nextPageToken') is None:
            comments_list += response_json['items']
            return comments_list

        if query_volume == 'all':
            # Getting all comments if there's a paging token, adding them all to the list after
            while response_json.get('nextPageToken'):
                next_page_token = response_json.get('nextPageToken')
                payload = {
                    'part': part,
                    'maxResults': max_results,
                    'order': order_by,
                    'videoId': video_id,
                    'pageToken': next_page_token,
                    'key': api_key
                }
                response_json = requests.get(base_url, params=payload).json()
                comments_list += response_json['items']
                # print(len(comments_list))  # debug


def main():
    """
    Input Schema: inputs.csv
    video_id, video_title

    > Output Schema: [date_time]-comments.csv
    video_id, comment_id, comment_date, updated_date, commenter_name, commenter_url, parent_comment, child_comment,

    > Mock:
    qwerty1234, asdf1234, 2016-09-09T11:52:18.000Z, 2016-09-09T11:52:18.000Z, randomUser, someURL, "

    """
    comments_list = send_request(resource='commentThreads',
                                 query_volume='all',
                                 video_id='srXsCRnSgBA',
                                 part='snippet,replies',
                                 max_results=100,
                                 order_by='relevance')

    print(len(comments_list))
    # print(response_json)

    return ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('user', help='Github username')
    # parser.add_argument('repo', help='User\'s repo')
    args = parser.parse_args()
    # main(args.user, args.repo)
    main()
