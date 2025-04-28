from vision import visionNav as vn
import cv2 as cv

# files

red_green = cv.VideoCapture('/home/salvador_cb/3_term/engineering_club/data/Videos/Bouygs in the sea.mp4')
green = cv.VideoCapture('/home/salvador_cb/3_term/engineering_club/data/Videos/video with only green bouyg.mp4')
red = cv.VideoCapture('/home/salvador_cb/3_term/engineering_club/data/Videos/video with only red bouyg.mp4')
empty = cv.VideoCapture('/home/salvador_cb/3_term/engineering_club/data/Videos/empty sea.mp4')

simulation = cv.VideoCapture('/home/salvador_cb/3_term/engineering_club/data/Videos/path 2.mp4')

output = "/home/salvador_cb/3_term/engineering_club/data/output/output2.mp4"

#MAIN

if __name__ == "__main__":
    
    nav = vn(video=simulation)
    nav.run_on_video(output_path=output)