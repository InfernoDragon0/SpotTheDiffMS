import time
import win32gui
import win32ui
import win32con
import numpy
import cv2
import imutils

hwnds = []
#default size
w = 1366
h = 768
mouseX,mouseY = 0,0

targetFPS = 30 #change this to change the FPS

#set the start and end location of each image in game
image1Xstart,image1Ystart = 233,126
image1Xend,image1Yend = 682,575

image2Xstart,image2Ystart = 691,126
image2Xend,image2Yend = 1140,575

#debug to get the X Y axis
def draw_circle(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(img,(x,y),100,(255,0,0),-1)
        mouseX,mouseY = x,y

#window finder
def winEnumHandler( hwnd, ctx ):
    if win32gui.IsWindowVisible( hwnd ):
        if (win32gui.GetWindowText(hwnd) == "MapleStory"):
            print ( hex( hwnd ), win32gui.GetWindowText( hwnd ) )
            hwnds.append(hwnd)


win32gui.EnumWindows( winEnumHandler, None )

hwnd = hwnds[0]
if (len(hwnds) > 1): #player has chat external
    hwnd = hwnds[1]

#get the correct size
rect = win32gui.GetWindowRect(hwnd)
x = rect[0]
y = rect[1]
w = rect[2] - x
h = rect[3] - y

# hwnd = win32gui.FindWindow(None, "MapleStory")
wDC = win32gui.GetWindowDC(hwnd)
dcObj=win32ui.CreateDCFromHandle(wDC)
cDC=dcObj.CreateCompatibleDC()
dataBitMap = win32ui.CreateBitmap()
dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
cDC.SelectObject(dataBitMap)
# cv2.namedWindow('image')
# cv2.setMouseCallback('image',draw_circle)

while True:
    #get the image from the window
    timestart = time.time()
    cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)

    #make CV image
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = numpy.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h,w,4)
    datashow = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    data = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

    #crop the 2 images
    image1 = datashow[image1Ystart:image1Yend, image1Xstart:image1Xend]
    image2 = datashow[image2Ystart:image2Yend, image2Xstart:image2Xend]

    datashowCropped = datashow[image1Ystart:image1Yend, image1Xstart:image1Xend]
    #do an abs difference
    diff = cv2.absdiff(image1, image2)
    #cv2.imshow("diff(img1, img2)", diff)
    diff = cv2.cvtColor(diff, cv2.COLOR_RGBA2GRAY) #uncolor the difference

    #dilate the difference
    kernel = numpy.ones((5,5), numpy.uint8) 
    dilate = cv2.dilate(diff, kernel, iterations=2) 
    cv2.imshow("Dilate", dilate)

    contours = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    for contour in contours:
        if cv2.contourArea(contour) > 30:
            # Calculate bounding box around contour
            xx, yy, ww, hh = cv2.boundingRect(contour)
            cv2.rectangle(datashowCropped, (xx, yy), (xx+ww, yy+hh), (0,255,255), 3)

    #show results
    # cv2.imshow("left", image1)
    # cv2.imshow("right", image2)
    # cv2.imshow("image", datashow)
    cv2.imshow("final", datashowCropped)

    timend = time.time()
    
    if (1/targetFPS - (timend-timestart) > 0):
        time.sleep(1/targetFPS - (timend-timestart))

    #end when Q is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
            # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        break
    elif cv2.waitKey(1) & 0xFF == ord('a'):
        print (mouseX,mouseY)
