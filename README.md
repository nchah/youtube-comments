# yt-analysis

A work in progress to programmatically obtain YouTube data (views, comments, etc.) for further computational text analysis and qualitative analysis.


## Dependencies

In addition to the standard Python libraries, this project also uses the following.

- Requests

## Run

```
$ python3 youtube-data-api.py [path_to_input_file]
```

Not designed to run with Python 2.x as some unicode support may break.

## Data

### Input

Input CSV data is composed of the following columns.

### Output

Output CSV data is composed of the following columns. 


## YouTube Data API v3 Endpoints

The following endpoints are queried in this project.

```
youtube.commentThreads - get YouTube video comments and replies

youtube.channels - get channelIds

youtube.videos - get video title, description, duration

```




