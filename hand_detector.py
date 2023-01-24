import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
from utility_classes import Detector, Colors
import socket

# Initializing Video Camera
cap = cv2.VideoCapture(0)

# Initializing Hands processing and drawing landmarks utilities
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Setting up the devices to control the computer audio
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Setting constants Range
led_range = [0, 255]
led_index_range = [15, 100]
led_mf_range = [15, 115]
led_rf_range = [15, 95]

fan_range = [0, 100]
fan_finger_range = [20, 200]

buzzer_range = [0, 1500]
buzzer_finger_range = [20, 200]

# Initializing Variables
previous_index_position = [0, 0]
rgb = [0, 0, 0]
fan_power = 50

HOST = "192.168.4.3"  # The server's hostname or IP address
PORT = 15000  # The port used by the server

# Initializing detector input variables
detector_mode = Detector.NONE
freeze_sampling = False
freeze_requests = True

print("Sampling is frozen: ", freeze_sampling)
print("Sending requests is frozen: ", freeze_requests)


# Always executeffss
while True:
    # Take a picture from the webcam
    success, img = cap.read()

    # Process the capture taken for hands
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Create Landmarks for each hand detected in the capture taken
    landmark_list = []
    if results.multi_hand_landmarks:
        for hand_landmark in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmark.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([id, cx, cy])
            mpDraw.draw_landmarks(img, hand_landmark, mpHands.HAND_CONNECTIONS)

    # Only register 1 hand!
    if landmark_list != []:
        '''
            landmark_list is a variable that contains the 21 points of the hands and their coordinates.
            Each finger has 3 points (making a total of 15) and the palm has 6 points.
            The index of the landmarks are symmetric (that means, all the indexes remain the same regardless
            if the hand shown is right or left one)
        '''

        if detector_mode == Detector.RGB:
            # Index Coordinates - Controls Red
            tip_index_x, tip_index_y = landmark_list[8][1], landmark_list[8][2]
            base_index_x, base_index_y = landmark_list[5][1], landmark_list[5][2]

            # Middle Finger Coordinates - Controls Green
            tip_mf_x, tip_mf_y = landmark_list[12][1], landmark_list[12][2]
            base_mf_x, base_mf_y = landmark_list[9][1], landmark_list[9][2]

            # Ring Finger Coordinates - Controls Blue
            tip_rf_x, tip_rf_y = landmark_list[16][1], landmark_list[16][2]
            base_rf_x, base_rf_y = landmark_list[13][1], landmark_list[13][2]

            # Drawing
            cv2.line(img, (base_index_x, base_index_y), (tip_index_x, tip_index_y), (0, 0, 255), 3)
            cv2.line(img, (base_mf_x, base_mf_y), (tip_mf_x, tip_mf_y), (0, 255, 0), 3)
            cv2.line(img, (base_rf_x, base_rf_y), (tip_rf_x, tip_rf_y), (255, 0, 0), 3)

            if not freeze_sampling:
                # Calculating RGB values
                red_length = hypot(tip_index_x - base_index_x, tip_index_y - base_index_y)
                green_length = hypot(tip_mf_x - base_mf_x, tip_mf_y - base_mf_y)
                blue_length = hypot(tip_rf_x - base_rf_x, tip_rf_y - base_rf_y)

                rgb[0] = int(np.interp(red_length, led_index_range, led_range))
                rgb[1] = int(np.interp(green_length, led_mf_range, led_range))
                rgb[2] = int(np.interp(blue_length, led_rf_range, led_range))

                if not freeze_requests:
                    esp_request = 0x01000000 | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((HOST, PORT))
                            s.sendall(esp_request.to_bytes(4, 'big'))
                            s.close()
                    except Exception:
                        pass

            previous_index_position = [tip_index_x, tip_index_y]

        elif detector_mode == Detector.BUZZER:
            # Tip Thumb Coordinates
            tip_thumb_x, tip_thumb_y = landmark_list[4][1], landmark_list[4][2]

            # Tip Index Coordinates
            tip_lf_x, tip_lf_y = landmark_list[20][1], landmark_list[20][2]

            # Drawing
            cv2.line(img, (tip_thumb_x, tip_thumb_y), (tip_lf_x, tip_lf_y), (214, 169, 19), 3)

            if not freeze_sampling:
                # Calculating how much the fan should be working [0%-100%]
                power_length = hypot(tip_thumb_x - tip_lf_x, tip_thumb_y - tip_lf_y)

                buzzer_power = int(np.interp(power_length, buzzer_finger_range, buzzer_range))

                # Sending request
                if not freeze_requests:
                    esp_request = 0x02000000 | buzzer_power
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((HOST, PORT))
                            s.sendall(esp_request.to_bytes(4, 'big'))
                            s.close()
                    except Exception:
                        pass

            previous_index_position = [landmark_list[8][1], landmark_list[8][2]]
        elif detector_mode == Detector.FAN:
            # Tip Index Coordinates
            tip_index_x, tip_index_y = landmark_list[8][1], landmark_list[8][2]

            # Drawing
            cv2.line(img, (tip_index_x, tip_index_y),
                     (previous_index_position[0], previous_index_position[1]), (214, 19, 152), 3)

            if not freeze_sampling:
                # Calculating how much the fan should be working [0%-100%]
                swipe_length = hypot(previous_index_position[0] - tip_index_x,
                                     previous_index_position[1] - tip_index_y)

                #swipe = int(np.interp(swipe_length, buzzer_swipe_range, buzzer_range))
                swipe = True if int(np.interp(swipe_length, buzzer_swipe_range, buzzer_range)) > 50 else False
                print(swipe)

            previous_index_position = [tip_index_x, tip_index_y]
        else:
            pass

        #length = hypot(x2 - x1, y2 - y1)

        #vol = np.interp(length, [15, 220], ledRange)
        #print(vol, length)
        #volume.SetMasterVolumeLevel(vol, None)

        # Hand range 15 - 220
        # Volume range -63.5 - 0.0

    # Show a window of the capture taken with all the modifications done to it
    cv2.imshow('Image', img)

    # ---------------------------- INPUTS

    # Changing Detector Mode to RGB
    key_pressed = cv2.waitKey(5)
    if key_pressed & 0xff == ord('1'):
        detector_mode = Detector.RGB
        print("Changing Detector Mode to RGB")
        # Changing Detector Mode to FAN
    elif key_pressed & 0xff == ord('2'):
        detector_mode = Detector.BUZZER
        print("Changing Detector Mode to Buzzer")
    # Changing Detector Mode to NONE
    elif key_pressed & 0xff == ord('3'):
        detector_mode = Detector.FAN
        print("Changing Detector Mode to Swipe Fan")
    # Changing Detector Mode to NONE
    elif key_pressed & 0xff == ord('0'):
        detector_mode = Detector.NONE
        print("Deactivating Detector...")

    # Press 'f' to toggle sampling
    elif key_pressed & 0xff == ord('f'):
        freeze_sampling = not freeze_sampling
        print("Sampling is frozen: ", freeze_sampling)
    # Press 's' to toggle request spam
    elif key_pressed & 0xff == ord('s'):
        freeze_requests = not freeze_requests
        print("Sending requests is frozen: ", freeze_requests)
    # Press 'q' to quit
    elif key_pressed & 0xff == ord('q'):
        print("Quitting IoT...")
        break
