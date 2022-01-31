import main_handtracker as htagcm #handtracker and gesture control module
import player_v2 as mp

htagcm.create_log_files()
out_dir = htagcm.out_dir


music_player = mp.music_player("myplayer")

while True:
    gesture = htagcm.analyze_gestures()
    with open(out_dir + "\\log.txt", "r") as log:
        log_data = log.read()

    with open(out_dir + "\\id.txt", "r") as id:
        ids = int(id.read())

    """Stop player"""
    if gesture == "thumb_touch_index" and log_data == "playing":
        music_player.stop_music()

    """Start player"""
    if gesture == "thumb_touch_index" and log_data == "stopped":
        music_player.start_music()

