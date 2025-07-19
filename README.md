# smortie

shitty discord.py music bot with security concerns. for me and 1 friend. public because github actions

just a fun side project

## hyperloglog

uses the extremely cool, [accurate, and low-memory-usage](https://github.com/shun4midx/FQ-HyperLogLog-Autocorrect/tree/main/fq_hll_py#results) autocorrect algorithm library which you can read more about [here](https://github.com/shun4midx/FQ-HyperLogLog-Autocorrect)!!! star the repository and `pip install fq-hll` or `pip install DyslexicLogLog` :D

https://github.com/shun4midx/FQ-HyperLogLog-Autocorrect

## docs

documentation? mmmmmmmmmm one day maybe, just do the token stuff in music.py, and put your songs (.mp3, .m4a) inside playlists/(playlist name), and play by supplying a channel id.

supports playing 24/7, from a playlist, singular song, shuffling, master playlist with all songs in all playlists, and more that I don't remember.

clone using `git clone -b main --single-branch https://github.com/ducky4life/smortie.git`

contact me at ducky4life@duck.com

### features

- 24/7 playing (/play24)
- playing a playlist (/play, folder inside /playlists)
- playing a single file (/playfile, file inside /playlists/*)
- playing a local file (uploaded with /playlocalfile command)
- playing an imported queue (/play the "continue" playlist)
- searching for local songs from a spotify playlist and importing to queue (/playspotify)
- autocorrect search queries with [FQ-HLL](https://github.com/shun4midx/FQ-HyperLogLog-Autocorrect) (fully automatic, library can be accessed using /autocorrect)
- master playlist (all files inside /playlists/*)
- importing/displaying/appending to queue (!smort import, /queue)
- continuing from where you left off (/play the "continue" playlist)
- searching by track name/artist name (/search, /playartist to quickly import all songs of an artist)
