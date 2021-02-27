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

def save_image(surface, filename):
    fullpath = os.path.join(data_dir, filename)
    pygame.image.save(surface, fullpath)

class Bild(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.filename = 'stor.tif'
        self.original = load_image(self.filename)
        self.image = self.original.copy()
        self.rect = self.image.get_rect()
        self.dispsurf = pygame.display.get_surface()
        self.disprect = self.dispsurf.get_rect()
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

        self.croppos = 0

        self.rot90 = False
        self.rotateString = '0deg'
        self.hFlip = False
        self.mirrorString = 'Rmirror'
        self.vFlip = False
        self.flipString = '0flip'

    def toggle(self, item):
        if item == 'rot90':
            self.rot90 = self.rot90 == False            #ändra boolvärdet
            self.rotate90()
            self.resize()
            if self.vFlip: self.flip('vFlip')
            if self.hFlip: self.flip('hFlip')
        elif item == 'hFlip':
            self.hFlip = self.hFlip == False            #ändra boolvärdet
            self.flip(item)
        elif item == 'vFlip':
            self.vFlip = self.vFlip == False            #ändra boolvärdet
            self.flip(item)

    def rotate90(self):
        if self.rot90:
            self.image = pygame.transform.rotate(self.original, 270)
            self.rect = self.image.get_rect()
        else:
            self.image = self.original
            self.rect = self.image.get_rect()

    def flip(self, direction):
        if direction == 'hFlip':
            self.Limage = pygame.transform.flip(self.Limage, True, False)
            self.Rimage = pygame.transform.flip(self.Rimage, True, False)
        if direction == 'vFlip':
            self.Limage = pygame.transform.flip(self.Limage, False, True)
            self.Rimage = pygame.transform.flip(self.Rimage, False, True)


    def resize(self):
        self.dispsurf = pygame.display.get_surface()
        self.disprect = self.dispsurf.get_rect()
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
        self.croppos = min((mouse[0]+1)/2, self.Lrect.width)

        self.Lrect.left = self.disprect.centerx - self.croppos
        self.Rrect.left = self.disprect.centerx
        self.Lcrop.width = self.croppos
        self.Rcrop.width = self.croppos
        self.Rcrop.left = self.Rrect.width - self.croppos

        if self.rot90 == True:
            self.rotateString = '90deg'
        else:
            self.rotateString = ''
        if self.hFlip == True:
            self.mirrorString = 'Rmirror'
        else:
            self.mirrorString = 'Lmirror'
        if self.vFlip == True:
            self.flipString = 'Vflip'
        else:
            self.flipString = ''
def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0)
    fullscreen = False
    
    bild = Bild()

    #mainloop
    going=True
    while going:

        #Handle Input Events
        for event in pygame.event.get():        
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == KEYDOWN and event.key == K_d:
                print pygame.mouse.get_pos()
                print bild.croppos
            elif event.type == KEYDOWN and event.key == K_p:
                save_image(screen, bild.filename + ' ' + str(bild.croppos) + ' ' + bild.mirrorString + ' ' + bild.rotateString + ' ' + bild.rotateString + '.png')
            elif event.type == KEYDOWN and event.key == K_q:
                bild.toggle('rot90')
                print 'R', bild.rot90, 'H', bild.hFlip, 'V', bild.vFlip
            elif event.type == KEYDOWN and event.key == K_w:
                bild.toggle('hFlip')
                print 'R', bild.rot90, 'H', bild.hFlip, 'V', bild.vFlip
            elif event.type == KEYDOWN and event.key == K_e:
                bild.toggle('vFlip')
                print 'R', bild.rot90, 'H', bild.hFlip, 'V', bild.vFlip
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