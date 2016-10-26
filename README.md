# yt-analysis

A work in progress to programmatically obtain YouTube data (views, comments, etc.) for further computational text analysis and qualitative analysis.


## Run

```
$ python3 youtube-data-api.py
```

Not designed to run with Python 2.x as some unicode support may break.


## YouTube Data API v3 Endpoints

The following endpoints are queried in this project.

```
youtube.commentThreads - get YouTube video comments and replies

youtube.channels - get channelIds

youtube.videos - get video title, description, duration

```




