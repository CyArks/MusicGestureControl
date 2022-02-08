import cv2
import mediapipe as mp
import time
import psutil as psutil
# from playsound import playsound
# from pydub import AudioSegment
# from pydub.playback import play
import os
import pytube
from pytube import Playlist
# import vlc
# from pygame import mixer
import subprocess
import webbrowser
import player_v2


class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.8, trackCon=0.75):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 8, (0, 0, 5), cv2.BORDER_CONSTANT)
        return lmList


def analyze_gestures():
    camera_number = 0
    pTime = 0
    cap = cv2.VideoCapture(cv2.CAP_DSHOW + camera_number)
    detector = HandDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            thumb_tip_coo = lmList[4]
            index_mcp_coo = lmList[5]
            middle_tip_coo = lmList[12]
            middle_mcp_coo = lmList[9]
            ring_mcp_coo = lmList[13]
            ring_tip_coo = lmList[16]

            x_distance_thumb_tip_index_mcp = thumb_tip_coo[1] - index_mcp_coo[1]
            y_distance_thumb_tip_index_mcp = thumb_tip_coo[2] - index_mcp_coo[2]

            x_distance_middle_mcp_middle_tip = middle_mcp_coo[1] - middle_tip_coo[1]
            y_distance_middle_mcp_middle_tip = middle_mcp_coo[2] - middle_tip_coo[2]
            x_distance_ring_mcp_ring_tip = ring_mcp_coo[1] - ring_tip_coo[1]
            y_distance_ring_mcp_ring_tip = ring_mcp_coo[2] - ring_tip_coo[2]

            # print("x: ", x_distance_thumb_tip_index_mcp)
            # print("y:", y_distance_thumb_tip_index_mcp)
            if abs(x_distance_middle_mcp_middle_tip) < 30 and abs(y_distance_middle_mcp_middle_tip) < 30:
                player_v2.obj.prev_track()
            if abs(x_distance_ring_mcp_ring_tip) < 30 and abs(y_distance_ring_mcp_ring_tip) < 15:
                player_v2.obj.next_track()

            if abs(x_distance_thumb_tip_index_mcp) < 35 and abs(y_distance_thumb_tip_index_mcp) < 35:
                type = "thumb_touch_index"
                return type

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (125, 12, 0), 3)
        img = cv2.resize(img, (620, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


id4 = 0
out_dir = os.getcwd()

Playlist_URL = input("YT Playlist URL")
p = Playlist(Playlist_URL)
urls = p.video_urls.__str__().split(",")
playlist_length = p.video_urls.__len__()
playlist_title = p.title
length = pytube.YouTube(urls[id4]).length


def create_log_files():
    try:
        with open(out_dir + "\\log.txt", "x") as log:
            log.write("stopped")
    except FileExistsError:
        with open(out_dir + "\\log.txt", "w") as log:
            log.write("stopped")

    try:
        with open(out_dir + "\\id.txt", "x") as id3:
            id3.write("0")
    except FileExistsError:
        with open(out_dir + "\\id.txt", "w") as id3:
            id3.write("0")


def stop_player():
    print("Stopping Music")
    for process in (process for process in psutil.process_iter() if process.name() == "Music.UI.exe"):
        process.kill()
    with open(out_dir + "\\log.txt", "w") as log:
        log.write("stopped")


def start_player(ids):
    print("Start Playing song: ", urls[ids])
    try:
        yt = pytube.YouTube(urls[ids],
                            use_oauth=True,
                            allow_oauth_cache=True
                            )
        out_file = yt.streams.filter(only_audio=True).first().download(out_dir)
        # os.rename(out_file, out_file.replace("mp4", "mp3"))

        if not os.path.exists(out_file.replace("mp4", "mp3")):
            subprocess.run([
                'ffmpeg',
                '-i', os.path.join(out_file),
                os.path.join(out_file.replace("mp4", "mp3"))
            ])
            os.remove(out_file)

        with open(out_dir + "\\log.txt", "w") as log:
            log.write("playing")
        # play(AudioSegment.from_mp3(out_file.replace("mp4", "mp3")))
        # so = vlc.MediaPlayer(out_file.replace("mp4", "mp3"))
        # so.play()

        # os.system("Microsoft.ZuneMusic_10.20022.11011.0_x64__8wekyb3d8bbwe " + out_file.replace("mp4", "mp3"))

        # playsound(out_file.replace("mp4", "mp3"))

        webbrowser.open(out_file.replace("mp4", "mp3"))

        # mixer.init()
        # mixer.music.load(out_file.replace("mp4", "mp3"))
        # mixer.music.play()

    except Exception as e:
        print("Error: ", e)


def previous_song():
    with open(out_dir + "\\id.txt", "r") as id0:
        id_num = int(id0.read())
    if id_num < playlist_length:
        with open(out_dir + "\\id.txt", "w") as id0:
            id0.write(str(int(id_num) - 1))
            print("-ID: ", pytube.YouTube(urls[id_num - 1]).title)
    if id_num <= 0:
        with open(out_dir + "\\id.txt", "w") as id0:
            id0.write(str(playlist_length - 1))
            print("Playlist Anfang! Starte von Ende!")
            print(pytube.YouTube(urls[playlist_length - 1]).title)


def next_song():
    with open(out_dir + "\\id.txt", "r") as id1:
        id_num = int(id1.read())
    if id_num < playlist_length - 1:
        with open(out_dir + "\\id.txt", "w") as id1:
            id1.write(str(int(id_num) + 1))
            print("+ID: ", pytube.YouTube(urls[id_num + 1]).title)
    if id_num >= playlist_length - 1:
        with open(out_dir + "\\id.txt", "w") as id1:
            print("Playlist Ende! Starte erneut!")
            print("Anfang: ", pytube.YouTube(urls[0]).title)
            id1.write("0")
