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

def load_n_resize(filename):
    fullpath = os.path.join(data_dir, filename)
    dispsurf = pygame.display.get_surface()
    disprect = dispsurf.get_rect()
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    imagerect = image.get_rect()
    scale = min(1.0 * disprect.height / imagerect.height, 1.0 * disprect.width/2.0 / imagerect.width)
    width = int(scale * imagerect.width)
    height = int(scale * imagerect.height)
    Limage = pygame.Surface((width,height),0,image)
    pygame.transform.scale(image, (width, height), Limage)
    Rimage = pygame.transform.flip(Limage, True, False)
    return Limage, Rimage

class Bild(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.Limage, self.Rimage = load_n_resize('test.jpg')
        self.Lrect = self.Limage.get_rect()
        self.Rrect = self.Rimage.get_rect()
        self.Lcrop = self.Lrect.copy()
        self.Rcrop = self.Rrect.copy()
        #self.mirrorrect = self.rect.copy()
        #self.mirrorcrop = self.rect.copy()
        #self.mirrorimage = pygame.transform.flip(self.image, True, False)
        

    def update(self):
        mouse = pygame.mouse.get_pos()
        crop = min(mouse[0], self.Lrect.width)
        self.Lcrop.width = crop
        self.Rrect.left = crop
        self.Rcrop.width = crop
        self.Rcrop.left = self.Lrect.width-crop

    # def resize(self, displaywidth, displayheight):
    #     factor = (displaywidth/2.0) / self.rect.width
    #     width = int(self.rect.width * factor)
    #     height = int(self.rect.height * factor)
    #     self.rect.width = width
    #     self.rect.height = height
    #     self.mirrorrect.width = width
    #     self.mirrorrect.height = height
    #     self.crop.height = height
    #     self.mirrorcrop.height = height
    #     self.image = pygame.transform.scale(self.image, (width, height))
    #     self.mirrorimage = pygame.transform.scale(self.mirrorimage, (width, height))
    #     self.rect.centery = (displayheight/2)
    #     self.mirrorrect.centery = (displayheight/2)

        
class Bild2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('test.jpg')        
        self.image = pygame.transform.flip(self.image, True, False)
        self.crop = self.rect.copy()
        self.rect.centery = (240)

    def update(self):
        mouse = pygame.mouse.get_pos()
        self.crop.width = mouse[0]


def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0)
    fullscreen = False
    
    bild = Bild()
    #bild2 = Bild2()

    allsprites = pygame.sprite.Group(bild) #lägger till spriten 'bild' i gruppen allsprites
    #bild.resize(640,480)


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
                    #bild.resize(640,480)
                    pygame.display.set_mode((640,480))
                    bild = Bild()
                    allsprites = pygame.sprite.Group(bild)
                else:
                    fullscreen = True
                    pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
                    bild = Bild()
                    allsprites = pygame.sprite.Group(bild)
                    #bild.resize(1680,1050)

            
    
        allsprites.update()
        screen.fill ((50, 0, 0))
        screen.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        screen.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        #allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()