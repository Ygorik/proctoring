import cv2

FONT = cv2.FONT_HERSHEY_PLAIN

# Функция для отображения текста на изображении с задним фоном
def colorBackgroundText(img, text, font, fontScale, textPos, textThickness=1,textColor=(0,255,0), bgColor=(0,0,0), pad_x=3, pad_y=3):
    """
    Draws text with background, with  control transparency
    @param img:(mat) which you want to draw text
    @param text: (string) text you want draw
    @param font: fonts face, like FONT_HERSHEY_COMPLEX, FONT_HERSHEY_PLAIN etc.
    @param fontScale: (double) the size of text, how big it should be.
    @param textPos: tuple(x,y) position where you want to draw text
    @param textThickness:(int) fonts weight, how bold it should be
    @param textPos: tuple(x,y) position where you want to draw text
    @param textThickness:(int) fonts weight, how bold it should be.
    @param textColor: tuple(BGR), values -->0 to 255 each
    @param bgColor: tuple(BGR), values -->0 to 255 each
    @param pad_x: int(pixels)  padding of in x direction
    @param pad_y: int(pixels) 1 to 1.0 (), controls transparency of  text background 
    @return: img(mat) with draw with background
    """
    (t_w, t_h), _= cv2.getTextSize(text, font, fontScale, textThickness) # getting the text size
    x, y = textPos
    cv2.rectangle(img, (x-pad_x, y+ pad_y), (x+t_w+pad_x, y-t_h-pad_y), bgColor,-1) # draw rectangle 
    cv2.putText(img,text, textPos, font, fontScale, textColor, textThickness) # draw in text

    return img

def fps_scale(w, h):

    x = int(w / 32)
    y = int(h / 9)

    font_size = w * 0.8 / 320 
    font_bold = int(w / 320)

    front = int(w / 128)

    return font_size, x, y, font_bold, front

def eyes_scale(w, h):

    x = int(w / 32)
    #y_left = int(h / 4)
    #y_right = int(h * 11 / 32)


    y_right = 140
    y_left = 170

    font_size = w * 0.8 / 320
    font_bold = int(w / 320)

    front = int(w / 128)

    return font_size, x, y_right, y_left, font_bold, front

def head_scale(w, h):

    x = int(w / 32)
    #y = int(h * 16 / 32)
    y = int(h / 4)

    font_size = w * 0.8 / 320
    font_bold = int(w / 320)

    front = int(w / 128)

    return font_size, x, y, font_bold, front

def counter_scale(w, h):
        
    x = int(w / 32)
    y = int(h * 17 / 18)

    font_size = w * 0.8 / 320
    font_bold = int(w / 320)

    front = int(w / 128)

    return font_size, x, y, font_bold, front

def lips_scale(w, h):

    x = int(w / 32)
    y = int(h * 11 / 18)

    font_size = w * 0.8 / 320
    font_bold = int(w / 320)

    front = int(w / 128)

    return font_size, x, y, font_bold, front