# coding: utf-8
import os, pygame
import sys
#import time
from pygame.locals import *
#import random
import math
#import colorsys
from PIL import Image
import numpy
import glob
from operator import mul, add
from wand.image import Image as wImage


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
files = glob.glob(os.path.join(data_dir, '*.tif'))
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
    rect = surface.get_rect()
    image_string = pygame.image.tostring(surface, 'RGB', False)
    image_pil = Image.fromstring('RGB', rect.size, image_string)
    image_pil = image_pil.convert('L')
    image_pil = image_pil.convert('RGB')
    image_string = image_pil.tostring()
    surface = pygame.image.fromstring(image_string, rect.size, 'RGB', False)
    return surface

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
        #set image rotation and colormode
        self.greyscale()
        self.rotate()
        if self.vFlip: self.flip('vFlip')
        if self.hFlip: self.flip('hFlip')
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
        self.mouse_pos_ratio = 1.0 * (mouse[0]+1) / self.disprect.width #used for save
        #self.croppos = min((mouse[0]+1)/2, self.Lrect.width)
        self.croppos = (mouse[0]+1)/2

        self.Lrect.left = self.disprect.centerx - self.croppos
        self.Rrect.left = self.disprect.centerx
        self.Lcrop.width = self.croppos
        self.Rcrop.width = self.croppos
        self.Rcrop.left = self.Rrect.width - self.croppos

        if self.rot90 == True:
            self.rotateString = 'R90'
        else:
            self.rotateString = ''
        if self.hFlip == True:
            self.mirrorString = 'fH'
        else:
            self.mirrorString = ''
        if self.vFlip == True:
            self.flipString = 'fV'
        else:
            self.flipString = ''
        if self.isGrey == True:
            self.greyString = 'G'
        else:
            self.flipString = ''

    def save(self):
        print "Pil saving..."
        pilImage = Image.open(files[fileNr])
        print pilImage.mode
        if self.isGrey: pilImage = pilImage.convert('L')
        if self.rot90: pilImage = pilImage.rotate(90, 'NEAREST', True)
        if self.hFlip: pilImage = pilImage.transpose('FLIP_LEFT_RIGHT')
        if self.vFlip: pilImage = pilImage.transpose('FLIP_TOP_BOTTOM')
        mirror_size = int(pilImage.size[0] * self.mouse_pos_ratio)
        pilImage = pilImage.crop((0,0,mirror_size,pilImage.size[1]))
        new_image = Image.new(pilImage.mode, (mirror_size*2, pilImage.size[1]))
        new_image.paste(pilImage, (0,0))
        pilImage = pilImage.transpose(0)
        new_image.paste(pilImage, (mirror_size,0))
        new_image.save('outtest.png')
        print "...save done."

    def wand_save(self):
        print "Wand saving..."
        wandImage = wImage(filename=files[fileNr])
        if self.isGrey: wandImage.type = 'grayscale'
        if self.rot90: wandImage = wandImage.rotate(90)
        if self.hFlip: wandImage = wandImage.flop()
        if self.vFlip: wandImage = wandImage.flip()
        mirror_size = int(wandImage.width * self.mouse_pos_ratio)
        wandImage.crop(0,0,mirror_size,wandImage.height)
        new_image = wImage(width=mirror_size*2, height=wandImage.size[1])
        new_image.depth = 16
        new_image.composite(wandImage, left=0, top=0)
        wandImage.flop()
        new_image.composite(wandImage, left=mirror_size, top=0)
        new_image.save(filename='outtest.tif')
        print "...save done."        

def main():

    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0)
    screen_rect = screen.get_rect()

    fullscreen = False

    font = pygame.font.Font(os.path.join(data_dir, 'vgafix.fon'), 14)
    
    bild = Bild()

    show_info = True


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
            elif event.type == KEYDOWN and event.key == K_r:
                bild.toggle('grey')
            elif event.type == KEYDOWN and event.key == K_f:
                if fullscreen:
                    pygame.display.set_mode((640,480))
                    fullscreen = False
                    screen_rect = screen.get_rect()
                    bild.resize()
                else:
                    pygame.display.set_mode((1680,1050), pygame.FULLSCREEN)
                    fullscreen = True
                    screen_rect = screen.get_rect()
                    bild.resize()
            elif event.type == KEYDOWN and event.key == K_n:
                bild.load_next(True)
            elif event.type == KEYDOWN and event.key == K_b:
                bild.load_next(False)
            elif event.type == KEYDOWN and event.key == K_TAB:
                show_info = show_info == False
            elif event.type == KEYDOWN and event.key == K_s:
                bild.wand_save()

        bild.update()

        imagearea = pygame.Surface((bild.Lrect.width*2, bild.Lrect.height), 0, screen)
        imageareaRect = imagearea.get_rect()
        imageareaRect.centery = pygame.display.Info().current_h / 2


        
        screen.fill ((50, 0, 0))
        imagearea.fill ((50, 0, 0))
        imagearea.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        imagearea.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        screen.blit(imagearea, imageareaRect)

        #create text surfaces
        if bild.rot90: rot_text = font.render('Q: Rotate 90', False, (0,255,0))
        else: rot_text = font.render('Q: Rotate 90', False, (128,128,128))
        if bild.hFlip: hflip_text = font.render('W: Flip H', False, (0,255,0))
        else: hflip_text = font.render('W: Flip H', False, (128,128,128))
        if bild.vFlip: vflip_text = font.render('E: Flip V', False, (0,255,0))
        else: vflip_text = font.render('E: Flip V', False, (128,128,128))
        if bild.isGrey: grey_text = font.render('R: Greyscale', False, (0,255,0))
        else: grey_text = font.render('R: Greyscale', False, (128,128,128))
        full_text = font.render('F: Fullscreen', False, (128,128,128))
        info_text = font.render('Tab: Hide', False, (128,128,128))
        next_text = font.render('N: Next', False, (128,128,128))
        prev_text = font.render('B: Prev.', False, (128,128,128))
        file_text = font.render(files[fileNr], False, (128,128,128))
        #pos_text = font.render('Pos: '+ str(bild.croppos), False, (128,128,128))
        #pos_text_rect = pos_text.get_rect()

        #render texts
        if show_info:
            screen.blit(rot_text, (0,0))
            screen.blit(hflip_text, (120,0))
            screen.blit(vflip_text, (210,0))
            screen.blit(grey_text, (300,0))
            screen.blit(full_text, (420,0))
            screen.blit(info_text, (screen_rect.width-90,0))
            screen.blit(next_text, (screen_rect.width-74,14))
            screen.blit(prev_text, (screen_rect.width-74,28))
            screen.blit(file_text, (0,screen_rect.height-15))
            #screen.blit(pos_text, (screen_rect.width-pos_text_rect.width ,screen_rect.height-15))
            


        pygame.display.flip()

if __name__ == '__main__':
    main()