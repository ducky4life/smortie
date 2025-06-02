# smortie

shitty discord.py music bot with tons of security concerns. for me and 1 friend. public because github actions

it prints your system directory out lol. super hardcoded and too many bugs.

just a fun side project.

i wont give documentation if you'd like to use it, just do the token stuff in music.py, and put your songs (.mp3, .m4a) inside playlists/(playlist name), and play by supplying a channel id.

supports playing 24/7, from a playlist, singular song, shuffling, master playlist with all songs in all playlists, and more that I don't remember.

run it in github codespaces or actions. its not safe.

contact me at ducky4life@duck.com

### features

- 24/7 playing (/play24)
- playing a playlist (/play, folder inside /playlists)
- playing a single file (/playfile, file inside /playlists/*)
- playing a local file (uploaded with /playlocalfile command)
- master playlist (all files inside /playlists/*)
- importing/displaying queue (!smort import, /queue)
- continuing from where you left off (/play the "continue" playlist)
- searching by track name/artist name (/search)
