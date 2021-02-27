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
    return image

class Bild(pygame.sprite.Sprite):
    def __init__(self, dispsurf):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.original = load_image('stor.tif')
        self.image = self.original.copy()
        self.rect = self.image.get_rect()
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

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.original, angle)
        self.rect = self.image.get_rect()

    def flip(self, isHorizontal):
        if isHorizontal:
            self.Limage = pygame.transform.flip(self.Limage, True, False)
            self.Rimage = pygame.transform.flip(self.Rimage, True, False)
        else:
            self.Limage = pygame.transform.flip(self.Limage, False, True)
            self.Rimage = pygame.transform.flip(self.Rimage, False, True)

    def update(self):
        mouse = pygame.mouse.get_pos()
        crop = min(mouse[0]/2, self.Lrect.width)

        self.Lrect.left = self.disprect.centerx - crop
        self.Rrect.left = self.disprect.centerx
        self.Lcrop.width = crop
        self.Rcrop.width = crop
        self.Rcrop.left = self.Rrect.width - crop

def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0)
    fullscreen = False
    
    bild = Bild(screen)

    #mainloop
    going=True
    while going:

        #Handle Input Events
        for event in pygame.event.get():        
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key == K_1:
                bild.rotate(0)
                bild.resize(screen)
            elif event.type == KEYDOWN and event.key == K_2:
                bild.rotate(90)
                bild.resize(screen)
            elif event.type == KEYDOWN and event.key == K_3:
                bild.rotate(180)
                bild.resize(screen)
            elif event.type == KEYDOWN and event.key == K_4:
                bild.rotate(270)
                bild.resize(screen)
            elif event.type == KEYDOWN and event.key == K_q:
                bild.flip(True)
            elif event.type == KEYDOWN and event.key == K_w:
                bild.flip(False)
            elif event.type == KEYDOWN and event.key == K_f:
                if fullscreen:
                    fullscreen = False
                    pygame.display.set_mode((640,480))
                    bild.resize(screen)
                else:
                    fullscreen = True
                    pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
                    bild.resize(screen)

        bild.update()
        screen.fill ((50, 0, 0))
        screen.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        screen.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        pygame.display.flip()

if __name__ == '__main__':
    main()