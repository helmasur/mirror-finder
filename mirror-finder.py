﻿# coding: utf-8
import os, pygame
import sys
import time
from pygame.locals import *
import random
from math import *
import colorsys
from PIL import Image
import numpy

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(filename):
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    return image, image.get_rect()    

class Bild(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('test.jpg')
        
class Bild2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('test.jpg')        
        self.image = pygame.transform.flip(self.image, True, False)



def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0, 32)
    
    bild = Bild()
    bild2 = Bild2()

    allsprites = pygame.sprite.Group(bild2) #lägger till spriten 'bild' i gruppen allsprites

       
    allsprites.draw(screen)
    pygame.display.flip()
    allsprites.draw(screen)
    pygame.display.flip()    

    

    #mainloop
    going=True
    while going:

        #Handle Input Events
        for event in pygame.event.get():        
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN:
                going = False                #plot.setLevel(int(event.unicode))
    
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()