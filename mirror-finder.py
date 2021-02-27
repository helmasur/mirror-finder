# coding: utf-8
import os, pygame
import sys
import time
from pygame.locals import *
import random
import math
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
    def __init__(self, dispsurf):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('test.jpg')
        self.disprect = dispsurf.get_rect()
        scale = min(1.0 * self.disprect.height / self.rect.height, 1.0 * self.disprect.width/2.0 / self.rect.width)
        width = int(scale * self.rect.width)
        height = int(scale * self.rect.height)
        self.Limage = pygame.Surface((width,height),0,self.image)
        pygame.transform.scale(self.image, (width, height), self.Limage)
        self.Rimage = pygame.transform.flip(self.Limage, True, False)

        self.Lrect = self.Limage.get_rect()
        self.Rrect = self.Rimage.get_rect()
        self.Lcrop = self.Lrect.copy()
        self.Rcrop = self.Rrect.copy()
        
        self.Lrect.centery = self.disprect.height / 2
        self.Rrect.centery = self.disprect.height / 2

    def resize(self, dispsurf):
        self.disprect = dispsurf.get_rect()
        scale = min(1.0 * self.disprect.height / self.rect.height, 1.0 * self.disprect.width/2.0 / self.rect.width)
        width = int(scale * self.rect.width)
        height = int(scale * self.rect.height)
        self.Limage = pygame.Surface((width,height),0,self.image)
        pygame.transform.scale(self.image, (width, height), self.Limage)
        self.Rimage = pygame.transform.flip(self.Limage, True, False)

        self.Lrect = self.Limage.get_rect()
        self.Rrect = self.Rimage.get_rect()
        self.Lcrop = self.Lrect.copy()
        self.Rcrop = self.Rrect.copy()

        self.Lrect.centery = self.disprect.height / 2
        self.Rrect.centery = self.disprect.height / 2

    def update(self):
        mouse = pygame.mouse.get_pos()
        crop = min(mouse[0], self.Lrect.width)
        self.Lcrop.width = crop
        self.Rrect.left = crop
        self.Rcrop.width = crop
        self.Rcrop.left = self.Lrect.width-crop

def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0)
    fullscreen = False
    
    bild = Bild(screen)
    allsprites = pygame.sprite.Group(bild) #lägger till spriten 'bild' i gruppen allsprites

    #mainloop
    going=True
    while going:

        #Handle Input Events
        for event in pygame.event.get():        
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key == K_f:
                if fullscreen:
                    fullscreen = False
                    pygame.display.set_mode((640,480))
                    bild.resize(screen)
                else:
                    fullscreen = True
                    pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
                    bild.resize(screen)

        allsprites.update()
        screen.fill ((50, 0, 0))
        screen.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        screen.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        pygame.display.flip()

if __name__ == '__main__':
    main()