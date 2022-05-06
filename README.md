# Spotinlizer(tm) - docs
## Find that song that got stuck in your head, and fast


### How does it work?

I used a few assumptions in order to find what song stuck in your head:
1. You liked that song in spotify
2. You know a few words, hopefully from the anthem (it don't have to be accurate, just close enough)

What Spotinlizer(tm) does is connect to your spotify account, loading up all your liked songs and gets their lyrics from Genius,
and we take the words that you remember, and we check how many times they occurred in the song (if the word "damn" occured 3 times, it will count 3 times! 
that's why it's better if it's in the anthem) and we take the likeliness score that is a multiplier of how many times the words exists to the sample

For example - you remember the words "There's nowhere left to turn Walls keep breaking" (from the song Telescope by Cage the Elephant) - these words would appear in the song a total of 58 times, and we entered 8 words
meaning that the strength would be 7.25 - play with the `--likeliness_threshold` to better filter songs (the lower the threshold the more non-relevant songs would appear)


### How to install this magnificent software?

First, clone it and sign in to Spotify and Genius APIs and create projects in both - afterwards create a new `.env` file with the following template:

Now, chose if you want to run Spotinlizer(tm) using python or in Docker

#### Local python
Create a virtual env (if you want, y'know)

```
mkvirtualenv spotinlizer
```
And then install Spotinlizer(tm)'s requirements:
```
pip install -r requirements.txt
```

And then create a `.env` file with the following template
```
SPOTIFY_CLIENT_ID=<key>
SPOTIFY_CLIENT_SECRET=<key>
SPOTIFY_REDIRECT_URI=<redirect uri (you can put http://localhost/ and add it to spotify settings!>
GENIUS_ACCESS_TOKEN=<access_token>
```


#### Using Docker

Fill the project keys and change the text you look for and the likeliness threshold in `docker-compose.yml` and then run
```
docker-compose up
```

And now just wait, it might take a few minutes (depends on how many songs you liked, ig)


I hope that it found that song that got stuck in your head

NOTE: this is not really a TM, just a joke on a bad name, and yes, I know that the name sucks no need to open issues about it
