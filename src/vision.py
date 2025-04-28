import cv2 as cv
import numpy as np

class visionNav:
    def __init__(self, video=None):

        #inputs
        self.video = video
        self.image = None

        self.hsv_color = None
        self.mask_r = None
        self.mask_g = None

        self.middle_x = None
        self.height = None
        self.width = None
        self.distance = None

    def text_size(self, width ,direction):
        font = cv.FONT_HERSHEY_SIMPLEX
        scale = 1.8
        thickness = 4
        text_size = cv.getTextSize(direction, font, scale, thickness)[0]
        cv.putText(self.image, direction, ((width - text_size[0])//2, 50), font, scale, (0, 0, 0), thickness, cv.LINE_AA)

    def generate_masks(self):
        if self.image is not None:

            image_bilateral = cv.bilateralFilter(self.image, 25, 400, 400)
            self.hsv_color = cv.cvtColor(image_bilateral, cv.COLOR_BGR2HSV)

            red = {
                "lower1": np.array([0, 40, 40]),
                "upper1": np.array([10, 255, 255]),
                "lower2": np.array([170, 0, 20]),
                "upper2": np.array([180, 255, 255])
            }
            green = {
                "lower": np.array([30, 40, 0]),
                "upper": np.array([90, 255, 255])
            }

            # green mask
            self.mask_g = cv.inRange(self.hsv_color, green["lower"], green["upper"])
            
            # red mask
            mask_r1 = cv.inRange(self.hsv_color, red["lower1"], red["upper1"])
            mask_r2 = cv.inRange(self.hsv_color, red["lower2"], red["upper2"])
            self.mask_r = mask_r1 | mask_r2

            # Morphological operations
            self.mask_g = self.morphops(self.mask_g)
            self.mask_r = self.morphops(self.mask_r)
        else:
            print("No image loaded.")

    def morphops(self, mask):
        kernel = np.ones((5,5), np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN,kernel)
        mask = cv.erode(mask, kernel, iterations=4)
        return mask

    def detect(self, mask, min_area, color, description):
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        biggest_contour = max(contours, key=cv.contourArea) if contours else None
        x,y,w,h= cv.boundingRect(biggest_contour)
        position = x + w // 2
        box = cv.rectangle(self.image, (x,y), (x+w, y+h), color, 5)
        cv.putText(self.image, f"{description} BUOY", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return (True, position, x, y, w, h)
    
    def line_style(self, centerp, p1, p2, color, thickness, description):
        cv.line(self.image, p1, p2, color, thickness)
        cv.circle(self.image, centerp, 5, color, thickness)
        self.text_size(self.width,description)
    
    def distance_between(self, x_green, x_red, y_green, y_red, green_w, green_h, red_w, red_h):
        green_point = ((x_green + (green_w // 2)), (y_green + (green_h // 2)))
        green_missing = (0,(y_red + (red_h // 2)))
        red_point = ((x_red + (red_w // 2)), (y_red + (red_h // 2)))
        red_missing = (self.width, (y_green + (green_h // 2)))
        distance = x_green - x_red
        self.middle_x = abs((x_green - x_red) // 2)
        center_line = (((x_green + (green_w // 2)) + (x_red + (red_w // 2))) // 2, ((y_green + (green_h // 2)) + (y_red + (red_h // 2))) // 2)

        if distance < 0:

            if x_green == 0 and y_green == 0:
                self.line_style(green_missing,green_missing,red_point,(0, 255, 0),3,"Turn Starboard!") 
            
            else:
                # Create points correctly with brackets
                point1 = np.array([((x_green + (green_w // 2)) + (x_red + (red_w // 2))) // 2, self.height // 2])
                point2 = np.array([self.width // 2, self.height // 2])
                self.distance = cv.norm(point1, point2)
                if (((x_green + (green_w // 2)) + (x_red + (red_w // 2))) // 2) > self.width // 2:
                    self.line_style(center_line,green_point, red_point, (0, 255, 255), 3, f"Keep Route! Move right: {int(self.distance)}")
                elif (((x_green + (green_w // 2)) + (x_red + (red_w // 2))) // 2) < self.width // 2:
                    self.line_style(center_line,green_point, red_point, (0, 255, 255), 3, f"Keep Route! Move left: {int(self.distance)}")
                #line between buoys and center of the frame
                cv.line(self.image, center_line,(((x_green + (green_w // 2)) + (x_red + (red_w // 2))) // 2, self.height // 2), (0, 255, 255),2)
                cv.line(self.image,(((x_green + (green_w // 2)) + (x_red + (red_w // 2))) // 2, self.height // 2),(self.width // 2, self.height // 2), (0, 255, 255),2)
        else:
            if x_red == 0 and y_red == 0:
                self.line_style(red_missing,green_point,red_missing,(0, 0, 255),3,"Turn Port!")
            else:
                self.line_style(center_line,green_point, red_point, (0, 0, 255), 3, f"Turn Around!")
            
    def detect_buoys(self, min_area = 1000):

        green_detected, green_position, green_x, green_y, green_w, green_h = self.detect(self.mask_g, min_area, (0, 255, 0),"GREEN") if self.detect(self.mask_g, min_area, (0, 255, 0), "GREEN") else (False, None)
        red_detected, red_position, red_x, red_y, red_w, red_h = self.detect(self.mask_r, min_area, (0, 0, 255),"RED") if self.detect(self.mask_r, min_area, (0, 0, 255), "RED") else (False, None)
        
        height, width, _ = self.image.shape
        self.height = height
        self.width = width

        self.distance_between(green_x, red_x, green_y, red_y,green_w, green_h, red_w, red_h)
        
        middle_frame = width // 2
        distance = middle_frame - self.middle_x
    
    def run_on_video(self, output_path):
        width = int(self.video.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.video.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = self.video.get(cv.CAP_PROP_FPS)

        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(output_path, fourcc, fps, (width, height))

        try:
            while self.video.isOpened():
                ret, frame = self.video.read()
                if not ret:
                    break
                self.image = frame
                self.generate_masks()
                self.detect_buoys()
                out.write(self.image)
                cv.imshow("Processed Frame", self.image)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            self.video.release()
            out.release()
            cv.destroyAllWindows()

        return output_path