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
    def __init__(self, dispsurf):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('test.jpg')
        #self.Limage, self.Rimage = load_n_resize('stor.tif')
        #self.Limage = pygame.Surface((10,10),0,self.image)
        #self.Rimage = pygame.Surface((10,10),0,self.image)
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
        #dispsurf = pygame.display.get_surface()
        
        self.Lrect.centery = self.disprect.height / 2
        self.Rrect.centery = self.disprect.height / 2
        #self.mirrorrect = self.rect.copy()
        #self.mirrorcrop = self.rect.copy()
        #self.mirrorimage = pygame.transform.flip(self.image, True, False)
        


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

        # factor = (displaywidth/2.0) / self.rect.width
        # width = int(self.rect.width * factor)
        # height = int(self.rect.height * factor)
        # self.rect.width = width
        # self.rect.height = height
        # self.mirrorrect.width = width
        # self.mirrorrect.height = height
        # self.crop.height = height
        # self.mirrorcrop.height = height
        # self.image = pygame.transform.scale(self.image, (width, height))
        # self.mirrorimage = pygame.transform.scale(self.mirrorimage, (width, height))
        # self.rect.centery = (displayheight/2)
        # self.mirrorrect.centery = (displayheight/2)


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
                    pygame.display.set_mode((640,480))
                    bild.resize(screen)
                    #bild = Bild()
                    #allsprites = pygame.sprite.Group(bild)
                else:
                    fullscreen = True
                    pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
                    #bild = Bild()
                    #allsprites = pygame.sprite.Group(bild)
                    bild.resize(screen)

            
    
        allsprites.update()
        screen.fill ((50, 0, 0))
        screen.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        screen.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        #allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()