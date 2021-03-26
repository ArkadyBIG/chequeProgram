import cv2
import json

clicks = []
path = "../../ch_photos/{}.jpg"
# path = '0.jpg'
files = ['cheques_to_test_3/0b446b34-0c82-4ee0-9295-dac4824dc6b3.jpg',
         'cheques_to_test_3/2.jpg',
         'cheques_to_test_3/2a385ed0-a84d-43d7-b2be-a35f124a96a6.jpg',
         'cheques_to_test_3/3.jpg',
         'cheques_to_test_3/4ad48164-12f3-4bf6-9720-28ab930faa8c.jpg',
         'cheques_to_test_3/a3b8e9fb-ef79-460c-96cb-b680ac6c5341.jpg']

def image_gen():
    for i in files:
        img = cv2.imread(i, 0)
        new_height = 900
        h, w = img.shape
        scale = new_height / h
        yield cv2.resize(img, None, fy=scale, fx=scale), scale, i + '.json'


gen = image_gen()
image, scale, json_path = next(gen)


def click_event(event, x, y, flags, param):
    global image, scale, json_path

    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append([x, y])
        font = cv2.FONT_HERSHEY_SIMPLEX
        strXY = str(x)+", "+str(y)
        cv2.putText(image, strXY, (x,y), font, 0.5, 255, 2)

    if len(clicks) == 4:
        data = {"corners": [{'type': name,
                             'x': int(clicks[i][0]/scale),
                             'y': int(clicks[i][1]/scale)} for
                            i, name in enumerate(('tl', 'tr', 'bl', 'br'))]}
        with open(json_path, 'w') as file:
            json.dump(data, file)

        image, scale, json_path = next(gen)
        clicks.clear()

    cv2.imshow("image", image)


cv2.imshow("image", image)
cv2.setMouseCallback("image", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
