# USAGE
# python recognize_faces_video_file.py --encodings encodings.pickle --input videos/input_video.mp4
# python recognize_faces_video_file.py --encodings encodings.pickle --input videos/input_video.mp4 --output output/input_video_output.avi --display 0

# import the necessary packages
import json
import os
from imutils.video import FPS, WebcamVideoStream, FileVideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR =os .path.join(FILE_DIR,'profile_detail.json')
DB ={}
try:
    DB = json.loads(open(BASE_DIR).read())
except:
    DB = {}
matched = {}
def recognise_face(data,input,args):
# initialize the pointer to the video file and the video writer
    print("[INFO] processing video...")
    stream = cv2.VideoCapture(args["input"])
    stream = FileVideoStream(args["input"]).start()
    # fps =FPS(args["input"])#.start()
    # stream =fps
    writer = None

    # loop over frames from the video file stream
    while stream.more():
        # grab the next frame
        frame = stream.read()

        # if the frame was not grabbed, then we have reached the
        # end of the stream
        # if not grabbed:
        #     break

        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(frame, width=750)
        r = frame.shape[1] / float(rgb.shape[1])

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input frame, then compute
        # the facial embeddings for each face

        boxes = face_recognition.face_locations(frame,
            model=args["detection_method"])
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []
        results =[]

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"],
                encoding)
            name = "Unknown_0"

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    key = str(name) + "_" +str(data["id"][i])
                    counts[key] = counts.get(key, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

            # update the list of names, id
            name = name.split("_")
            id = int(name[-1])
            name = name[:-1]
            name = " ".join(name)
            names.append(name)
            results.append(dict(id=id, name=name))

        # loop over the recognized faces
        for ((top, right, bottom, left), name,res) in zip(boxes, names,results):
            # rescale the face coordinates
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            # draw the predicted face name on the image
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
            yield res
        # if the video writer is None *AND* we are supposed to write
        # the output video to disk initialize the writer
        if writer is None and args["output"] is not None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 24,
                (frame.shape[1], frame.shape[0]), True)

        # if the writer is not None, write the frame with recognized
        # faces t odisk
        if writer is not None:
            writer.write(frame)

        # check to see if we are supposed to display the output frame to
        # the screen
        if args["display"] > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    # close the video file pointers
    stream.release()

    # check to see if the video writer point needs to be released
    if writer is not None:
        writer.release()
if __name__=="__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--encodings", default='encodings.pickle',
                    help="path to serialized db of facial encodings")
    ap.add_argument("-i", "--input", required=True,
                    help="path to input video")
    ap.add_argument("-o", "--output", type=str,
                    help="path to output video")
    ap.add_argument("-y", "--display", type=int, default=1,
                    help="whether or not to display output frame to screen")
    ap.add_argument("-d", "--detection-method", type=str, default="hog",
                    help="face detection model to use: either `hog` or `cnn`")
    args = vars(ap.parse_args())

    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    data = pickle.loads(open(args["encodings"], "rb").read())
    # try:
    result =recognise_face(data=data,input=input,args=args)
    for val in result:
        found = DB.get(str(val["id"]),False)
        if found:
            matched[str(id)]=found
        else :
            found= val
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(found)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # except Exception as e:
    #     print(e)
    #     file_name =os.path.join(FILE_DIR,'recognised_result.json')
    #     with open(file_name,'w') as f:
    #         f.flush()
    #         json.dump(matched,f)
    # finally:
    #     file_name = os.path.join(FILE_DIR, 'recognised_result.json')
    #     with open(file_name, 'w') as f:
    #         f.flush()
    #         json.dump(matched, f)