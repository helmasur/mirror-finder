# coding: utf-8
import os, pygame
import sys
#import time
from pygame.locals import *
#import random
import math
#import colorsys
#from PIL import Image
import numpy
import glob


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
files = glob.glob(os.path.join(data_dir, '*.jpg'))
fileNr = -1

def load_image(filename):
    fullpath = os.path.join(data_dir, filename)
    try:
        image = pygame.image.load(fullpath)
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()
    return image

def load_next_image(isNext):
    #change the index of the file to load
    global fileNr
    if fileNr == -1: fileNr=0
    elif isNext: #next file
        if fileNr+1 < len(files): fileNr+=1
        else: fileNr=0
    else: #previous file
        if fileNr > 0: fileNr-=1
        else: fileNr = len(files)-1

    try:
        image = pygame.image.load(files[fileNr])
    except pygame.error:
        print ('Cannot load image:', fullpath)
        raise SystemExit(str(geterror()))
    image = image.convert()

    return image

def save_image(surface, filename):
    fullpath = os.path.join(data_dir, filename)
    pygame.image.save(surface, fullpath)

def surf_grey(surface):
    arr = pygame.surfarray.array3d(surface)
    #luminosity filter
    avgs = [[(r*0.298 + g*0.587 + b*0.114) for (r,g,b) in col] for col in arr]
    arr = numpy.array([[[avg,avg,avg] for avg in col] for col in avgs])
    return pygame.surfarray.make_surface(arr)

class Bild(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #load file
        #self.filename = 'test.jpg'
        self.original = load_next_image(True)
        #create toggles
        self.rot90 = False
        self.rotateString = '0deg'
        self.hFlip = False
        self.mirrorString = 'Rmirror'
        self.vFlip = False
        self.flipString = '0flip'
        self.isGrey = False

        self.resize()

        self.croppos = 0    #position of the mirror

    def load_next(self, isNext):
        self.original = load_next_image(isNext)
        self.resize()

    def resize(self):   #create images fitting the current resolution
        self.dispsurf = pygame.display.get_surface()
        self.disprect = self.dispsurf.get_rect()
        self.rectOriginal = self.original.get_rect()
        #get fitting factors for both cases of rotation
        self.normScale = min(1.0 * self.disprect.height / self.rectOriginal.height, 1.0 * self.disprect.width/2.0 / self.rectOriginal.width)
        self.rotScale = min(1.0 * self.disprect.height / self.rectOriginal.width, 1.0 * self.disprect.width/2.0 / self.rectOriginal.height)
        #scale non rotated
        width = int(self.normScale * self.rectOriginal.width)
        height = int(self.normScale * self.rectOriginal.height)
        self.image = pygame.Surface((width,height),0,self.original)
        pygame.transform.scale(self.original, (width, height), self.image)
        #scale and rotate
        width = int(self.rotScale * self.rectOriginal.width)
        height = int(self.rotScale * self.rectOriginal.height)
        self.imageRot = pygame.Surface((width,height),0,self.original)
        pygame.transform.scale(self.original, (width, height), self.imageRot)
        self.imageRot = pygame.transform.rotate(self.imageRot, 270)
        #make greyscale versions
        self.imageRGB = self.image.copy()
        self.imageRotRGB = self.imageRot.copy()
        self.imageGrey = surf_grey(self.image)
        self.imageRotGrey = surf_grey(self.imageRot)
        #set image rotation
        self.rotate()
        self.update_rects()

    def toggle(self, item):
        if item == 'rot90':
            self.rot90 = self.rot90 == False            #ändra boolvärdet
            self.rotate()
            if self.vFlip: self.flip('vFlip')
            if self.hFlip: self.flip('hFlip')
        elif item == 'hFlip':
            self.hFlip = self.hFlip == False            #ändra boolvärdet
            self.flip(item)
        elif item == 'vFlip':
            self.vFlip = self.vFlip == False            #ändra boolvärdet
            self.flip(item)
        elif item == 'grey':
            self.isGrey = self.isGrey == False            #ändra boolvärdet
            self.greyscale()
            self.rotate()
            if self.vFlip: self.flip('vFlip')
            if self.hFlip: self.flip('hFlip')

    def update_rects(self):
        #get rects
        self.Lrect = self.Limage.get_rect()
        self.Rrect = self.Rimage.get_rect()
        self.Lcrop = self.Lrect.copy()
        self.Rcrop = self.Rrect.copy()
        #center images vertical
        #self.Lrect.centery = self.disprect.height / 2
        #self.Rrect.centery = self.disprect.height / 2     

    def greyscale(self):
        if self.isGrey:
            self.image = self.imageGrey
            self.imageRot = self.imageRotGrey
        else:
            self.image = self.imageRGB
            self.imageRot = self.imageRotRGB

    def rotate(self):
        if self.rot90:
            self.Limage = self.imageRot
            self.Rimage = pygame.transform.flip(self.imageRot, True, False)
            self.update_rects()
        else:
            self.Limage = self.image
            self.Rimage = pygame.transform.flip(self.image, True, False)
            self.update_rects()

    def flip(self, direction):
        if direction == 'hFlip':
            self.Limage = pygame.transform.flip(self.Limage, True, False)
            self.Rimage = pygame.transform.flip(self.Rimage, True, False)
        if direction == 'vFlip':
            self.Limage = pygame.transform.flip(self.Limage, False, True)
            self.Rimage = pygame.transform.flip(self.Rimage, False, True)

    def update(self):
        mouse = pygame.mouse.get_pos()
        self.croppos = min((mouse[0]+1)/2, self.Lrect.width)

        self.Lrect.left = self.disprect.centerx - self.croppos
        self.Rrect.left = self.disprect.centerx
        self.Lcrop.width = self.croppos
        self.Rcrop.width = self.croppos
        self.Rcrop.left = self.Rrect.width - self.croppos

        if self.rot90 == True:
            self.rotateString = 'rot90'
        else:
            self.rotateString = ''
        if self.hFlip == True:
            self.mirrorString = 'hFlip'
        else:
            self.mirrorString = ''
        if self.vFlip == True:
            self.flipString = 'vFlip'
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
                global fileNr
                fileNr += 1
                print fileNr
            elif event.type == KEYDOWN and event.key == K_p:
                save_image(imagearea, bild.filename + ' ' + str(bild.croppos) + ' ' + bild.mirrorString + ' ' + bild.rotateString + ' ' + bild.rotateString + '.png')
            elif event.type == KEYDOWN and event.key == K_q:
                bild.toggle('rot90')
                print 'R', bild.rot90, 'H', bild.hFlip, 'V', bild.vFlip
            elif event.type == KEYDOWN and event.key == K_w:
                bild.toggle('hFlip')
                print 'R', bild.rot90, 'H', bild.hFlip, 'V', bild.vFlip
            elif event.type == KEYDOWN and event.key == K_e:
                bild.toggle('vFlip')
                print 'R', bild.rot90, 'H', bild.hFlip, 'V', bild.vFlip
            elif event.type == KEYDOWN and event.key == K_g:
                bild.toggle('grey')
                print "tog g"
            elif event.type == KEYDOWN and event.key == K_f:
                if fullscreen:
                    pygame.display.set_mode((640,480))
                    fullscreen = False
                    bild.resize()
                else:
                    pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
                    fullscreen = True
                    bild.resize()
            elif event.type == KEYDOWN and event.key == K_n:
                bild.load_next(True)
            elif event.type == KEYDOWN and event.key == K_b:
                bild.load_next(False)

        bild.update()

        imagearea = pygame.Surface((bild.Lrect.width*2, bild.Lrect.height), 0, screen)
        imageareaRect = imagearea.get_rect()
        imageareaRect.centery = pygame.display.Info().current_h / 2
        
        screen.fill ((50, 0, 0))
        imagearea.fill ((50, 0, 0))
        imagearea.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        imagearea.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        screen.blit(imagearea, imageareaRect)
        pygame.display.flip()

if __name__ == '__main__':
    main()