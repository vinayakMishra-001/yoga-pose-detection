# # import math
# # import cv2
# # import numpy as np
# # from time import time
# # import mediapipe as mp
# # import matplotlib.pyplot as plt

# # # Part 1 ------------------- Pose Detection on Image/Video -------------------

# # # Initialize the pose detection model
# # # FIX 1: Typo fixed -> min_detction_confidence => min_detection_confidence
# # mp_pose = mp.solutions.pose
# # pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2)
# # mp_drawing = mp.solutions.drawing_utils

# # # Read an image
# # sample_img = cv2.imread('media/sample.jpg')
# # plt.figure(figsize=[10, 10])
# # plt.title("Sample Image"); plt.axis('off'); plt.imshow(sample_img[:, :, ::-1]); plt.show()

# # # FIX 2: cv2.cvtcolor() => cv2.cvtColor() (case-sensitive OpenCV function)
# # results = pose.process(cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB))

# # # FIX 3: results.pose_landmark => results.pose_landmarks (missing 's')
# # if results.pose_landmarks:
# #     for i in range(2):
# #         # FIX 4: mp.pose_PoseLandmark => mp_pose.PoseLandmark
# #         print(f'{mp_pose.PoseLandmark(i).name}:\n{results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value]}')

# # image_height, image_width, _ = sample_img.shape
# # if results.pose_landmarks:
# #     for i in range(2):
# #         print(f'{mp_pose.PoseLandmark(i).name}:')
# #         print(f'x: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].x * image_width}')
# #         print(f'y: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].y * image_height}')
# #         print(f'z: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].z * image_width}')
# #         print(f'visibility: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].visibility}\n')

# # img_copy = sample_img.copy()
# # if results.pose_landmarks:
# #     mp_drawing.draw_landmarks(image=img_copy, landmark_list=results.pose_landmarks, connections=mp_pose.POSE_CONNECTIONS)
# #     fig = plt.figure(figsize=[10, 10])
# #     plt.title("Output"); plt.axis('off'); plt.imshow(img_copy[:, :, ::-1]); plt.show()

# # # FIX 5: Plot_landmarks => plot_landmarks (uppercase P was wrong)
# # mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)


# # # ----------------------- Pose Detection Function ----------------------------

# # def detectPose(image, pose, display=True):
# #     output_image = image.copy()

# #     # FIX 6: cv2.cvtcolor() => cv2.cvtColor()
# #     imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #     results = pose.process(imageRGB)

# #     height, width, _ = image.shape
# #     landmarks = []

# #     if results.pose_landmarks:
# #         mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
# #                                   connections=mp_pose.POSE_CONNECTIONS)

# #         # FIX 7: Loop variable was 'landmarks' (shadowed the list) => renamed to 'landmark'
# #         for landmark in results.pose_landmarks.landmark:
# #             # FIX 8: landmarks.append(x, y, z) => landmarks.append((x, y, z))
# #             #         append() accepts only ONE argument; wrap coords in a tuple
# #             landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))

# #     if display:
# #         plt.figure(figsize=[22, 22])
# #         plt.subplot(121); plt.imshow(image[:, :, ::-1]); plt.title("Original Image"); plt.axis('off')
# #         plt.subplot(122); plt.imshow(output_image[:, :, ::-1]); plt.title("Output Image"); plt.axis('off')
# #         mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
# #     else:
# #         return output_image, landmarks


# # # ----------------------- Test on Sample Images ------------------------------

# # image = cv2.imread('media/sample1.jpg')
# # detectPose(image, pose, display=True)

# # image = cv2.imread('media/sample2.jpg')
# # detectPose(image, pose, display=True)

# # image = cv2.imread('media/sample3.jpg')
# # detectPose(image, pose, display=True)


# # # ----------------------- Real-Time Webcam / Video ---------------------------

# # # FIX 9: Used pose_video (correct instance) instead of reusing static 'pose'
# # pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

# # video = cv2.VideoCapture(1)
# # cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
# # video.set(3, 1280)
# # video.set(4, 960)
# # time1 = 0

# # while video.isOpened():
# #     ok, frame = video.read()
# #     if not ok:
# #         break

# #     frame = cv2.flip(frame, 1)
# #     frame_height, frame_width, _ = frame.shape
# #     frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

# #     # FIX 10: Pass pose_video (not pose) for the video feed
# #     frame, _ = detectPose(frame, pose_video, display=False)

# #     time2 = time()
# #     if (time2 - time1) > 0:
# #         frames_per_second = 1.0 / (time2 - time1)
# #         cv2.putText(frame, 'FPS: {}'.format(int(frames_per_second)),
# #                     (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 200, 0), 3)
# #         time1 = time2

# #     # FIX 11: cv2.waitkey() => cv2.waitKey() (capital K required)
# #     cv2.imshow('Pose Detection', frame)
# #     k = cv2.waitKey(1) & 0xFF
# #     if k == 27:
# #         break

# # # FIX 12: video.release() and destroyAllWindows() were INSIDE the while loop
# # #          (ran on first frame, killing video immediately) => moved OUTSIDE
# # video.release()
# # cv2.destroyAllWindows()


# # # Part 2 ------------------- Pose Classification ----------------------------
# # # Poses: a. Warrior II   b. T Pose   c. Tree Pose


# # def calculateAngle(landmark1, landmark2, landmark3):
# #     x1, y1, _ = landmark1
# #     x2, y2, _ = landmark2
# #     x3, y3, _ = landmark3

# #     # FIX 13: math.degree() => math.degrees() (missing 's')
# #     angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))

# #     if angle < 0:
# #         angle += 360

# #     return angle


# # angle = calculateAngle((558, 326, 0), (642, 333, 3), (718, 321, 0))
# # print(f'The calculated angle is {angle}')


# # # FIX 14: Parameter typo 'ouptut_image' => 'output_image'
# # #          (was causing NameError inside the function body)
# # def classifyPose(landmarks, output_image, display=False):

# #     # FIX 15: label initialised as 'unknown pose' but compared to 'Unknown Pose'
# #     #          Unified to 'Unknown Pose' so the green-color check works correctly
# #     label = 'Unknown Pose'
# #     color = (0, 0, 255)

# #     # Get the angle between the left shoulder, elbow and wrist points.
# #     left_elbow_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
# #     )

# #     # Get the angle between the right shoulder, elbow and wrist points.
# #     right_elbow_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
# #     )

# #     # Get the angle between the left elbow, shoulder and hip points.
# #     left_shoulder_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
# #     )

# #     # Get the angle between the right hip, shoulder and elbow points.
# #     right_shoulder_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
# #     )

# #     # Get the angle between the left hip, knee and ankle points.
# #     left_knee_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
# #     )

# #     # Get the angle between the right hip, knee and ankle points.
# #     right_knee_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
# #     )

# #     # -------------------- Warrior II / T Pose check -------------------------
# #     # Both require straight arms and shoulders at ~90 degrees

# #     if (left_elbow_angle > 165 and left_elbow_angle < 195 and
# #             right_elbow_angle > 165 and right_elbow_angle < 195):

# #         if (left_shoulder_angle > 80 and left_shoulder_angle < 110 and
# #                 right_shoulder_angle > 80 and right_shoulder_angle < 110):

# #             # Warrior II: one leg straight, the other bent at 90-120 degrees
# #             if ((left_knee_angle > 165 and left_knee_angle < 195) or
# #                     (right_knee_angle > 165 and right_knee_angle < 195)):

# #                 if ((left_knee_angle > 90 and left_knee_angle < 120) or
# #                         (right_knee_angle > 90 and right_knee_angle < 120)):
# #                     label = 'Warrior II Pose'

# #             # T Pose: both legs straight
# #             if (left_knee_angle > 160 and left_knee_angle < 195 and
# #                     right_knee_angle > 160 and right_knee_angle < 195):
# #                 label = 'T Pose'

# #     # ----------------------------- Tree Pose --------------------------------
# #     # FIX 16: Tree Pose block was mis-indented (outside shoulder check)
# #     #          and had inconsistent condition structure — corrected below
# #     if ((left_knee_angle > 165 and left_knee_angle < 195) or
# #             (right_knee_angle > 165 and right_knee_angle < 195)):

# #         if ((left_knee_angle > 315 and left_knee_angle < 335) or
# #                 (right_knee_angle > 25 and right_knee_angle < 45)):
# #             label = 'Tree Pose'

# #     # ------------------------------------------------------------------------

# #     if label != 'Unknown Pose':
# #         color = (0, 255, 0)

# #     cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

# #     if display:
# #         plt.figure(figsize=[10, 10])
# #         plt.imshow(output_image[:, :, ::-1]); plt.title("Output Image"); plt.axis('off')
# #         plt.show()
# #     else:
# #         return output_image, label
    

# # # Read a sample image and perform pose classification on it.
# # image = cv2.imread('media/warriorIIpose.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/warriorIIpose1.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read a sample image and perform pose classification on it.
# # image = cv2.imread('media/treepose.jpg')
# # output_image, landmarks = detectPose(
# #     image,
# #     mp_pose.Pose(static_image_mode=True,
# #                  min_detection_confidence=0.5,
# #                  model_complexity=0),
# #     display=False
# # )
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/treepose1.jpg')
# # output_image, landmarks = detectPose(
# #     image,
# #     mp_pose.Pose(static_image_mode=True,
# #                  min_detection_confidence=0.5,
# #                  model_complexity=0),
# #     display=False
# # )
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/treepose2.jpg')
# # output_image, landmarks = detectPose(
# #     image,
# #     mp_pose.Pose(static_image_mode=True,
# #                  min_detection_confidence=0.5,
# #                  model_complexity=0),
# #     display=False
# # )
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)

# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/Tpose.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/Tpose1.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/cobrapose1.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
# # camera_video=cv2.Videocapture(0)
# # camera_video.set(3,1280)
# # camera_video.set(4,960)

# # cv2.namedWindow('Pose Classification ', cv2.WINDOW_GUI_NORMAL)
# # while camera_video.isOpened():
# #     ok, frame = camera_video.read()
# #     if not ok:
# #         continue
# #     frame = cv2.flip(frame, 1)
# #     frame_height, frame_width, _ =frame.shape

# #     # Resize the frame while keeping the aspect ratio.
# # frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

# # # Perform Pose landmark detection.
# # frame, landmarks = detectPose(frame, pose_video, display=False)

# # # Check if the landmarks are detected.
# # if landmarks:

# #     # Perform the Pose Classification.
# #     frame, _ = classifyPose(landmarks, frame, display=False)

# # # Display the frame.
# # cv2.imshow('Pose Classification', frame)

# # # Wait until a key is pressed.
# # # Retrieve the ASCII code of the key pressed
# # k = cv2.waitKey(1) & 0xFF

# # # Check if 'ESC' is pressed.
# # if(k == 27):

# #     # Break the loop.
# #     break

# # # Release the VideoCapture object and close the windows.
# # camera_video.release()
# # cv2.destroyAllWindows()

# # import math
# # import cv2
# # import numpy as np
# # from time import time
# # import mediapipe as mp
# # import matplotlib.pyplot as plt

# # # Part 1 ------------------- Pose Detection on Image/Video -------------------

# # # Initialize the pose detection model
# # # FIX 1: Typo fixed -> min_detction_confidence => min_detection_confidence
# # mp_pose = mp.solutions.pose
# # pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2)
# # mp_drawing = mp.solutions.drawing_utils

# # # Read an image
# # sample_img = cv2.imread('media/sample_img.jpg')
# # plt.figure(figsize=[10, 10])
# # plt.title("Sample Image"); plt.axis('off'); plt.imshow(sample_img[:, :, ::-1]); plt.show()

# # # FIX 2: cv2.cvtcolor() => cv2.cvtColor() (case-sensitive OpenCV function)
# # results = pose.process(cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB))

# # # FIX 3: results.pose_landmark => results.pose_landmarks (missing 's')
# # if results.pose_landmarks:
# #     for i in range(2):
# #         # FIX 4: mp.pose_PoseLandmark => mp_pose.PoseLandmark
# #         print(f'{mp_pose.PoseLandmark(i).name}:\n{results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value]}')

# # image_height, image_width, _ = sample_img.shape
# # if results.pose_landmarks:
# #     for i in range(2):
# #         print(f'{mp_pose.PoseLandmark(i).name}:')
# #         print(f'x: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].x * image_width}')
# #         print(f'y: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].y * image_height}')
# #         print(f'z: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].z * image_width}')
# #         print(f'visibility: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].visibility}\n')

# # img_copy = sample_img.copy()
# # if results.pose_landmarks:
# #     mp_drawing.draw_landmarks(image=img_copy, landmark_list=results.pose_landmarks, connections=mp_pose.POSE_CONNECTIONS)
# #     fig = plt.figure(figsize=[10, 10])
# #     plt.title("Output"); plt.axis('off'); plt.imshow(img_copy[:, :, ::-1]); plt.show()

# # # FIX 5: Plot_landmarks => plot_landmarks (uppercase P was wrong)
# # mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)


# # # ----------------------- Pose Detection Function ----------------------------

# # def detectPose(image, pose, display=True):
# #     output_image = image.copy()

# #     # FIX 6: cv2.cvtcolor() => cv2.cvtColor()
# #     imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #     results = pose.process(imageRGB)

# #     height, width, _ = image.shape
# #     landmarks = []

# #     if results.pose_landmarks:
# #         mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
# #                                   connections=mp_pose.POSE_CONNECTIONS)

# #         # FIX 7: Loop variable was 'landmarks' (shadowed the list) => renamed to 'landmark'
# #         for landmark in results.pose_landmarks.landmark:
# #             # FIX 8: landmarks.append(x, y, z) => landmarks.append((x, y, z))
# #             #         append() accepts only ONE argument; wrap coords in a tuple
# #             landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))

# #     if display:
# #         plt.figure(figsize=[22, 22])
# #         plt.subplot(121); plt.imshow(image[:, :, ::-1]); plt.title("Original Image"); plt.axis('off')
# #         plt.subplot(122); plt.imshow(output_image[:, :, ::-1]); plt.title("Output Image"); plt.axis('off')
# #         mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
# #     else:
# #         return output_image, landmarks


# # # ----------------------- Test on Sample Images ------------------------------

# # image = cv2.imread('media/sample1.jpg')
# # detectPose(image, pose, display=True)

# # image = cv2.imread('media/sample2.jpg')
# # detectPose(image, pose, display=True)

# # image = cv2.imread('media/sample3.jpg')
# # detectPose(image, pose, display=True)


# # # ----------------------- Real-Time Webcam / Video ---------------------------

# # # FIX 9: Used pose_video (correct instance) instead of reusing static 'pose'
# # pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

# # video = cv2.VideoCapture(1)
# # cv2.namedWindow('Pose Detection', cv2.WINDOW_NORMAL)
# # video.set(3, 1280)
# # video.set(4, 960)
# # time1 = 0

# # while video.isOpened():
# #     ok, frame = video.read()
# #     if not ok:
# #         break

# #     frame = cv2.flip(frame, 1)
# #     frame_height, frame_width, _ = frame.shape
# #     frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

# #     # FIX 10: Pass pose_video (not pose) for the video feed
# #     frame, _ = detectPose(frame, pose_video, display=False)

# #     time2 = time()
# #     if (time2 - time1) > 0:
# #         frames_per_second = 1.0 / (time2 - time1)
# #         cv2.putText(frame, 'FPS: {}'.format(int(frames_per_second)),
# #                     (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 200, 0), 3)
# #         time1 = time2

# #     # FIX 11: cv2.waitkey() => cv2.waitKey() (capital K required)
# #     cv2.imshow('Pose Detection', frame)
# #     k = cv2.waitKey(1) & 0xFF
# #     if k == 27:
# #         break

# # # FIX 12: video.release() and destroyAllWindows() were INSIDE the while loop
# # #          (ran on first frame, killing video immediately) => moved OUTSIDE
# # video.release()
# # cv2.destroyAllWindows()


# # # Part 2 ------------------- Pose Classification ----------------------------
# # # Poses: a. Warrior II   b. T Pose   c. Tree Pose


# # def calculateAngle(landmark1, landmark2, landmark3):
# #     x1, y1, _ = landmark1
# #     x2, y2, _ = landmark2
# #     x3, y3, _ = landmark3

# #     # FIX 13: math.degree() => math.degrees() (missing 's')
# #     angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))

# #     if angle < 0:
# #         angle += 360

# #     return angle


# # angle = calculateAngle((558, 326, 0), (642, 333, 3), (718, 321, 0))
# # print(f'The calculated angle is {angle}')


# # # FIX 14: Parameter typo 'ouptut_image' => 'output_image'
# # #          (was causing NameError inside the function body)
# # def classifyPose(landmarks, output_image, display=False):

# #     # FIX 15: label initialised as 'unknown pose' but compared to 'Unknown Pose'
# #     #          Unified to 'Unknown Pose' so the green-color check works correctly
# #     label = 'Unknown Pose'
# #     color = (0, 0, 255)

# #     # Get the angle between the left shoulder, elbow and wrist points.
# #     left_elbow_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
# #     )

# #     # Get the angle between the right shoulder, elbow and wrist points.
# #     right_elbow_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
# #     )

# #     # Get the angle between the left elbow, shoulder and hip points.
# #     left_shoulder_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
# #     )

# #     # Get the angle between the right hip, shoulder and elbow points.
# #     right_shoulder_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
# #     )

# #     # Get the angle between the left hip, knee and ankle points.
# #     left_knee_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
# #         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
# #     )

# #     # Get the angle between the right hip, knee and ankle points.
# #     right_knee_angle = calculateAngle(
# #         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
# #         landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
# #     )

# #     # -------------------- Warrior II / T Pose check -------------------------
# #     # Both require straight arms and shoulders at ~90 degrees

# #     if (left_elbow_angle > 165 and left_elbow_angle < 195 and
# #             right_elbow_angle > 165 and right_elbow_angle < 195):

# #         if (left_shoulder_angle > 80 and left_shoulder_angle < 110 and
# #                 right_shoulder_angle > 80 and right_shoulder_angle < 110):

# #             # Warrior II: one leg straight, the other bent at 90-120 degrees
# #             if ((left_knee_angle > 165 and left_knee_angle < 195) or
# #                     (right_knee_angle > 165 and right_knee_angle < 195)):

# #                 if ((left_knee_angle > 90 and left_knee_angle < 120) or
# #                         (right_knee_angle > 90 and right_knee_angle < 120)):
# #                     label = 'Warrior II Pose'

# #             # T Pose: both legs straight
# #             if (left_knee_angle > 160 and left_knee_angle < 195 and
# #                     right_knee_angle > 160 and right_knee_angle < 195):
# #                 label = 'T Pose'

# #     # ----------------------------- Tree Pose --------------------------------
# #     # FIX 16: Tree Pose block was mis-indented (outside shoulder check)
# #     #          and had inconsistent condition structure — corrected below
# #     if ((left_knee_angle > 165 and left_knee_angle < 195) or
# #             (right_knee_angle > 165 and right_knee_angle < 195)):

# #         if ((left_knee_angle > 315 and left_knee_angle < 335) or
# #                 (right_knee_angle > 25 and right_knee_angle < 45)):
# #             label = 'Tree Pose'

# #     # ------------------------------------------------------------------------

# #     if label != 'Unknown Pose':
# #         color = (0, 255, 0)

# #     cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

# #     if display:
# #         plt.figure(figsize=[10, 10])
# #         plt.imshow(output_image[:, :, ::-1]); plt.title("Output Image"); plt.axis('off')
# #         plt.show()
# #     else:
# #         return output_image, label
    

# # # Read a sample image and perform pose classification on it.
# # image = cv2.imread('media/warrior2pose.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/warrior2pose1.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read a sample image and perform pose classification on it.
# # image = cv2.imread('media/treepose.jpg')
# # output_image, landmarks = detectPose(
# #     image,
# #     mp_pose.Pose(static_image_mode=True,
# #                  min_detection_confidence=0.5,
# #                  model_complexity=0),
# #     display=False
# # )
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/treepose1.jpg')
# # output_image, landmarks = detectPose(
# #     image,
# #     mp_pose.Pose(static_image_mode=True,
# #                  min_detection_confidence=0.5,
# #                  model_complexity=0),
# #     display=False
# # )
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/treepose2.jpg')
# # output_image, landmarks = detectPose(
# #     image,
# #     mp_pose.Pose(static_image_mode=True,
# #                  min_detection_confidence=0.5,
# #                  model_complexity=0),
# #     display=False
# # )
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)

# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/Tpose.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/Tpose1.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # # Read another sample image and perform pose classification on it.
# # image = cv2.imread('media/Cobrapose.jpg')
# # output_image, landmarks = detectPose(image, pose, display=False)
# # if landmarks:
# #     classifyPose(landmarks, output_image, display=True)


# # pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
# # # FIX 17: cv2.Videocapture(0) => cv2.VideoCapture(0) (capital C — crashes immediately)
# # camera_video = cv2.VideoCapture(0)
# # camera_video.set(3, 1280)
# # camera_video.set(4, 960)

# # cv2.namedWindow('Pose Classification ', cv2.WINDOW_GUI_NORMAL)
# # while camera_video.isOpened():
# #     ok, frame = camera_video.read()
# #     # FIX 18: 'continue' => 'break' (continue causes infinite loop when camera disconnects)
# #     if not ok:
# #         break
# #     frame = cv2.flip(frame, 1)
# #     frame_height, frame_width, _ = frame.shape

# #     # Resize the frame while keeping the aspect ratio.
# #     # FIX 19: Lines below were de-indented outside the while loop — fixed indentation
# #     frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

# #     # Perform Pose landmark detection.
# #     frame, landmarks = detectPose(frame, pose_video, display=False)

# #     # Check if the landmarks are detected.
# #     if landmarks:

# #         # Perform the Pose Classification.
# #         frame, _ = classifyPose(landmarks, frame, display=False)

# #     # Display the frame.
# #     cv2.imshow('Pose Classification', frame)

# #     # Wait until a key is pressed.
# #     # Retrieve the ASCII code of the key pressed
# #     k = cv2.waitKey(1) & 0xFF

# #     # Check if 'ESC' is pressed.
# #     if(k == 27):

# #         # Break the loop.
# #         break

# # # Release the VideoCapture object and close the windows.
# # camera_video.release()
# # cv2.destroyAllWindows()

# import math
# import cv2
# import numpy as np
# from time import time
# import mediapipe as mp
# import matplotlib.pyplot as plt
# import os

# # ---------------- SAFE IMAGE LOADER ----------------
# def load_image(filename):
#     base_path = os.path.dirname(__file__)
#     path = os.path.join(base_path, 'media', filename)
#     img = cv2.imread(path)

#     if img is None:
#         print(f"❌ ERROR loading: {path}")
#     else:
#         print(f"✅ Loaded: {filename}")

#     return img

# # ---------------- INITIALIZE ----------------
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3, model_complexity=2)
# mp_drawing = mp.solutions.drawing_utils

# # ---------------- SAMPLE IMAGE ----------------
# sample_img = load_image('sample_img.jpg')

# if sample_img is not None:
#     plt.figure(figsize=[10, 10])
#     plt.title("Sample Image"); plt.axis('off'); plt.imshow(sample_img[:, :, ::-1]); plt.show()

#     results = pose.process(cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB))

#     if results.pose_landmarks:
#         for i in range(2):
#             print(f'{mp_pose.PoseLandmark(i).name}:\n{results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value]}')

#     image_height, image_width, _ = sample_img.shape

#     if results.pose_landmarks:
#         for i in range(2):
#             print(f'{mp_pose.PoseLandmark(i).name}:')
#             print(f'x: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].x * image_width}')
#             print(f'y: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].y * image_height}')
#             print(f'z: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].z * image_width}')
#             print(f'visibility: {results.pose_landmarks.landmark[mp_pose.PoseLandmark(i).value].visibility}\n')

#     img_copy = sample_img.copy()

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(img_copy, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#         plt.figure(figsize=[10, 10])
#         plt.title("Output"); plt.axis('off'); plt.imshow(img_copy[:, :, ::-1]); plt.show()

# # ---------------- FUNCTION ----------------
# def detectPose(image, pose, display=True):
#     if image is None:
#         print("❌ Skipping empty image")
#         return None, []

#     output_image = image.copy()
#     imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = pose.process(imageRGB)

#     height, width, _ = image.shape
#     landmarks = []

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(output_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#         for landmark in results.pose_landmarks.landmark:
#             landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))

#     if display and image is not None:
#         plt.figure(figsize=[10, 10])
#         plt.imshow(output_image[:, :, ::-1]); plt.title("Output Image"); plt.axis('off')
#         plt.show()

#     return output_image, landmarks

# # ---------------- TEST IMAGES ----------------
# for img_name in ['sample1.jpg', 'sample2.jpg', 'sample3.jpg']:
#     image = load_image(img_name)
#     detectPose(image, pose, display=True)

# # ---------------- ANGLE ----------------
# def calculateAngle(landmark1, landmark2, landmark3):
#     x1, y1, _ = landmark1
#     x2, y2, _ = landmark2
#     x3, y3, _ = landmark3

#     angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))

#     if angle < 0:
#         angle += 360

#     return angle

# # ---------------- CLASSIFICATION ----------------
# def classifyPose(landmarks, output_image, display=False):
#     if not landmarks:
#         return output_image, "No Pose"

#     label = 'Unknown Pose'
#     color = (0, 0, 255)

#     try:
#         left_elbow_angle = calculateAngle(
#             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
#             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
#             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
#         )

#         right_elbow_angle = calculateAngle(
#             landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
#             landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
#             landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
#         )

#         left_knee_angle = calculateAngle(
#             landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
#             landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
#             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
#         )

#         right_knee_angle = calculateAngle(
#             landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
#             landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
#             landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
#         )

#         if (left_elbow_angle > 160 and right_elbow_angle > 160):
#             if (left_knee_angle > 160 and right_knee_angle > 160):
#                 label = 'T Pose'
#             elif (90 < left_knee_angle < 120) or (90 < right_knee_angle < 120):
#                 label = 'Warrior II Pose'

#         if (left_knee_angle > 160 and 25 < right_knee_angle < 45) or \
#            (right_knee_angle > 160 and 315 < left_knee_angle < 335):
#             label = 'Tree Pose'

#     except Exception as e:
#         print("⚠️ Classification skipped:", e)

#     if label != 'Unknown Pose':
#         color = (0, 255, 0)

#     cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

#     if display:
#         plt.imshow(output_image[:, :, ::-1]); plt.title(label); plt.axis('off')
#         plt.show()

#     return output_image, label

# # ---------------- RUN ALL IMAGES ----------------
# image_list = [
#     'warrior2pose.jpg', 'warrior2pose1.jpg',
#     'treepose.jpg', 'treepose1.jpg', 'treepose2.jpg',
#     'Tpose.jpg', 'Tpose1.jpg', 'Cobrapose.jpg'
# ]

# for img_name in image_list:
#     image = load_image(img_name)
#     output_image, landmarks = detectPose(image, pose, display=False)

#     if output_image is not None and landmarks:
#         classifyPose(landmarks, output_image, display=True)

# # ---------------- WEBCAM ----------------
# pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

# camera_video = cv2.VideoCapture(0)
# cv2.namedWindow('Pose Classification', cv2.WINDOW_NORMAL)

# while camera_video.isOpened():
#     ok, frame = camera_video.read()
#     if not ok:
#         break

#     frame = cv2.flip(frame, 1)

#     frame, landmarks = detectPose(frame, pose_video, display=False)

#     if landmarks:
#         frame, _ = classifyPose(landmarks, frame, display=False)

#     cv2.imshow('Pose Classification', frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# camera_video.release()
# cv2.destroyAllWindows()


import cv2
import math
import time
import threading
import base64
import numpy as np
import mediapipe as mp
from flask import Flask, Response, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='.')
CORS(app)

# ─── MediaPipe Setup ────────────────────────────────────────────────────────
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose_image = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, model_complexity=1)
pose_video = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

# ─── Shared State ───────────────────────────────────────────────────────────
latest_data = {
    "pose": "Unknown Pose",
    "confidence": 0,
    "angles": {"le": 0, "re": 0, "ls": 0, "rs": 0, "lk": 0, "rk": 0},
    "fps": 0
}
data_lock = threading.Lock()
camera_running = False
camera_thread = None

# ─── Angle Calculation ──────────────────────────────────────────────────────
def calculateAngle(landmark1, landmark2, landmark3):
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

# ─── Pose Detection ─────────────────────────────────────────────────────────
def detectPose(image, pose_model):
    output_image = image.copy()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose_model.process(imageRGB)
    height, width, _ = image.shape
    landmarks = []
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(output_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 150), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2))
        for lm in results.pose_landmarks.landmark:
            landmarks.append((int(lm.x * width), int(lm.y * height), lm.z * width))
    return output_image, landmarks

# ─── Pose Classification ────────────────────────────────────────────────────
def classifyPose(landmarks):
    if not landmarks or len(landmarks) < 33:
        return "Unknown Pose", 0, {}

    try:
        PL = mp_pose.PoseLandmark
        angles = {}

        le = calculateAngle(landmarks[PL.LEFT_SHOULDER.value], landmarks[PL.LEFT_ELBOW.value], landmarks[PL.LEFT_WRIST.value])
        re = calculateAngle(landmarks[PL.RIGHT_SHOULDER.value], landmarks[PL.RIGHT_ELBOW.value], landmarks[PL.RIGHT_WRIST.value])
        ls = calculateAngle(landmarks[PL.LEFT_ELBOW.value], landmarks[PL.LEFT_SHOULDER.value], landmarks[PL.LEFT_HIP.value])
        rs = calculateAngle(landmarks[PL.RIGHT_HIP.value], landmarks[PL.RIGHT_SHOULDER.value], landmarks[PL.RIGHT_ELBOW.value])
        lk = calculateAngle(landmarks[PL.LEFT_HIP.value], landmarks[PL.LEFT_KNEE.value], landmarks[PL.LEFT_ANKLE.value])
        rk = calculateAngle(landmarks[PL.RIGHT_HIP.value], landmarks[PL.RIGHT_KNEE.value], landmarks[PL.RIGHT_ANKLE.value])

        angles = {
            "le": round(le), "re": round(re),
            "ls": round(ls), "rs": round(rs),
            "lk": round(lk), "rk": round(rk)
        }

        label = "Unknown Pose"
        confidence = 10

        # T Pose
        if le > 160 and re > 160 and ls > 75 and ls < 110 and rs > 75 and rs < 110:
            if lk > 160 and rk > 160:
                label = "T Pose"
                confidence = min(99, int((le + re) / 3.6))

        # Warrior II
        elif le > 160 and re > 160 and ls > 75 and ls < 110 and rs > 75 and rs < 110:
            if (lk > 165 or rk > 165) and (90 < lk < 125 or 90 < rk < 125):
                label = "Warrior II Pose"
                confidence = min(97, int(ls + rs) // 2)

        # Tree Pose
        elif (lk > 160 and 25 < rk < 50) or (rk > 160 and 315 < lk < 340):
            label = "Tree Pose"
            confidence = min(95, int((lk + rk) / 3.8))

        return label, confidence, angles

    except Exception as e:
        return "Unknown Pose", 0, {}

# ─── Webcam Stream Generator ────────────────────────────────────────────────
def generate_frames():
    global camera_running
    cap = cv2.VideoCapture(0)#http://10.174.32.128:8080/video
    # ADD these 3 lines right after:
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # cap.set(cv2.CAP_PROP_FPS, 30)
    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    t_prev = time.time()

    while camera_running:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        output_frame, landmarks = detectPose(frame, pose_video)
        label, conf, angles = classifyPose(landmarks)

        t_now = time.time()
        fps = int(1.0 / max(t_now - t_prev, 0.001))
        t_prev = t_now

        # Overlay label
        color = (0, 255, 100) if label != "Unknown Pose" else (0, 0, 255)
        cv2.putText(output_frame, f"{label} {conf}%", (10, 35),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 2)
        cv2.putText(output_frame, f"FPS: {fps}", (10, 65),
                    cv2.FONT_HERSHEY_PLAIN, 1.2, (180, 255, 180), 2)

        # Update shared state
        with data_lock:
            latest_data["pose"] = label
            latest_data["confidence"] = conf
            latest_data["angles"] = angles
            latest_data["fps"] = fps

        _, buffer = cv2.imencode('.jpg', output_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'demo.html')

@app.route('/style.css')
def styles():
    return send_from_directory('.', 'style.css')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_running, camera_thread
    if not camera_running:
        camera_running = True
    return jsonify({"status": "started"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera_running
    camera_running = False
    return jsonify({"status": "stopped"})

@app.route('/pose_data')
def pose_data():
    with data_lock:
        return jsonify(latest_data)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    img_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Invalid image"}), 400

    # Resize for processing
    h, w = image.shape[:2]
    if w > 960:
        scale = 960 / w
        image = cv2.resize(image, (960, int(h * scale)))

    output_image, landmarks = detectPose(image, pose_image)
    label, conf, angles = classifyPose(landmarks)

    # Encode output image to base64
    _, buffer = cv2.imencode('.jpg', output_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "pose": label,
        "confidence": conf,
        "angles": angles,
        "image": img_b64
    })

if __name__ == '__main__':
    print("🧘 YogaVision Flask Server starting...")
    print("📡 Open: http://127.0.0.1:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)