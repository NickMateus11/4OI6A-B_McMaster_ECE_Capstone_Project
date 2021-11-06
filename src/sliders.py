import cv2
 
 
def on_change(val):
 
    imageCopy = img.copy()
 
    cv2.putText(imageCopy, str(val), (0, imageCopy.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4)
    (thresh, bin_img) = cv2.threshold(imageCopy, val, 255, cv2.THRESH_BINARY)
    cv2.imshow(windowName, bin_img)
 
# binary threshold
# blur
# sensitivity
 
img = cv2.imread('./images/maze5.jpg', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (img.shape[1]//5, img.shape[0]//5))
 
windowName = 'image'
 
cv2.imshow(windowName, img)
cv2.createTrackbar('slider', windowName, 150, 255, on_change)
 
cv2.waitKey(0)
cv2.destroyAllWindows()