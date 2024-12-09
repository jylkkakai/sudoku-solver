from PIL import Image, ImageGrab

screen_shot = ImageGrab.grab()

screen_shot.resize((800, 600))

fn = lambda x : 255 if x > 150 else 0
screen_shot = screen_shot.convert('L').point(fn, mode='1')

screen_shot.show("Hello")
