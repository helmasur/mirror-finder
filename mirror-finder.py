# coding: utf-8
import os, pygame
import sys
#import time
from pygame.locals import *
#import random
#import math
#import colorsys
from PIL import Image
#import numpy
import glob
#from operator import mul, add
from wand.image import Image as wImage
import pickle

#TODO
#cms https://pypi.python.org/pypi/smc.freeimage
#saturation*L
#error management of load non existing state


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
img_dir = "d:/_gruvan_sat/jpg"
out_dir = "d:/_gruvan_out"
files = glob.glob(os.path.join(img_dir, '*.jpg'))
fileNr = -1
statusString = ''

def save_state(filename):
    state_file = open(filename, 'w') #w for write mode
    pickle.dump(fileNr, state_file)
    state_file.close()

def load_state(filename):
    global fileNr
    global statusString
    try:
        state_file = open(filename)
        fileNr = pickle.load(state_file)
        state_file.close()
    except pygame.error:
        statusString = 'No such file yet.'
        raise SystemExit(str(geterror()))

def load_image(number):
    try:
        image = pygame.image.load(files[number])
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
        self.original = load_next_image(True)
        #create toggles
        self.rot90 = False
        self.rotateString = '0deg'
        self.hFlip = False
        self.mirrorString = 'Rmirror'
        self.vFlip = False
        self.flipString = '0flip'
        self.isGrey = False
        self.fit_height = False

        self.resize()

        self.croppos = 0    #position of the mirror

    def load_next(self, isNext):
        self.rot90 = False
        self.hFlip = False
        self.vFlip = False
        self.isGrey = False
        self.fit_height = False
        global statusString
        statusString = ''
        self.original = load_next_image(isNext)
        self.resize()

    def load_image(self, number):
        self.rot90 = False
        self.hFlip = False
        self.vFlip = False
        self.isGrey = False
        self.fit_height = False
        global statusString
        statusString = ''
        self.original = load_image(number)
        self.resize()        

    def resize(self):   #create images fitting the current resolution
        self.dispsurf = pygame.display.get_surface()
        self.disprect = self.dispsurf.get_rect()
        self.rectOriginal = self.original.get_rect()
        #get fitting factors for both cases of rotation
        if self.fit_height:
            self.normScale = 1.0 * self.disprect.height / self.rectOriginal.height
            self.rotScale = 1.0 * self.disprect.height / self.rectOriginal.width
        else:
            self.normScale = min(1.0 * self.disprect.height / self.rectOriginal.height, 1.0 * self.disprect.width/2.0 / self.rectOriginal.width)
            self.rotScale = min(1.0 * self.disprect.height / self.rectOriginal.width, 1.0 * self.disprect.width/2.0 / self.rectOriginal.height)
        #scale non rotated
        width = int(self.normScale * self.rectOriginal.width)
        height = int(self.normScale * self.rectOriginal.height)
        self.image = pygame.Surface((width,height),0,self.original)
        pygame.transform.smoothscale(self.original, (width, height), self.image)
        #scale and rotate
        width = int(self.rotScale * self.rectOriginal.width)
        height = int(self.rotScale * self.rectOriginal.height)
        self.imageRot = pygame.Surface((width,height),0,self.original)
        pygame.transform.smoothscale(self.original, (width, height), self.imageRot)
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
        elif item == 'fit':
            self.fit_height = self.fit_height == False
            self.resize()

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
        #mouse = mouse[0]+1 #the first column of pixels is 1 in relation to width of screen
        mouse = max(mouse[0]-10, 0) #move active area 10px to the right and limit to min 0
        mouse = min(1.0 * mouse / (self.disprect.width-20), 1) #crop active area 10px right and limit to 1
        self.mouse_pos_ratio = mouse
        #self.mouse_pos_ratio = 1.0 * (mouse[0]+1) / self.disprect.width #used for save
        #self.croppos = min((mouse[0]+1)/2, self.Lrect.width) #since tall images might not fill the width
        self.croppos = min(int(mouse*self.Lrect.width), self.Lrect.width) #since tall images might not fill the width

        self.Lrect.left = self.disprect.centerx - self.croppos
        self.Rrect.left = self.disprect.centerx
        self.Lcrop.width = self.croppos
        self.Rcrop.width = self.croppos
        self.Rcrop.left = self.Rrect.width - self.croppos

        if self.rot90 == True:
            self.rotateString = '_90'
        else:
            self.rotateString = ''
        if self.hFlip == True:
            self.mirrorString = '_Fh'
        else:
            self.mirrorString = ''
        if self.vFlip == True:
            self.flipString = '_Fv'
        else:
            self.flipString = ''
        if self.isGrey == True:
            self.greyString = '_G'
        else:
            self.greyString = ''

    def wand_save(self):
        global statusString
        pos = self.mouse_pos_ratio

        wandImage = wImage(filename=files[fileNr])
        depth = wandImage.depth
        if self.isGrey: wandImage.type = 'grayscale'
        if self.rot90: wandImage.rotate(90)
        if self.hFlip: wandImage.flop()
        if self.vFlip: wandImage.flip()
        mirror_size = int(wandImage.width * pos)
        wandImage.crop(0,0,mirror_size,wandImage.height)
        new_image = wImage(width=mirror_size*2-1, height=wandImage.size[1])  #-1 to avoid double center column
        new_image.depth = depth
        new_image.composite(wandImage, left=0, top=0)
        wandImage.crop(0,0,mirror_size-1,wandImage.height)  #-1 to avoid double center column
        wandImage.flop()
        new_image.composite(wandImage, left=mirror_size, top=0)
        filename = os.path.basename(files[fileNr])
        filename_root = os.path.splitext(filename)[0]
        filename_ext = os.path.splitext(filename)[1]
        filename = filename_root+self.rotateString+self.mirrorString+self.flipString+self.greyString+'_'+str(mirror_size)+filename_ext
        filepath = os.path.join(out_dir, filename)
        new_image.save(filename=filepath)
        statusString = 'Saved: '+filename

def main():

    pygame.init()

    fullwidth = pygame.display.Info().current_w
    fullheight = pygame.display.Info().current_h
    screen = pygame.display.set_mode((1024, 768), 0)
    screen_rect = screen.get_rect()

    fullscreen = False

    font = pygame.font.Font(os.path.join(data_dir, 'vgafix.fon'), 14)
    
    bild = Bild()

    show_info = True
    show_status = False

    global statusString

    #mainloop
    going=True
    while going:

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                show_status = False
            if event.type == QUIT:
                save_state('autosave.mir')
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                save_state('autosave.mir')
                going = False
            elif event.type == KEYDOWN and event.key == K_q:
                bild.toggle('rot90')
            elif event.type == MOUSEBUTTONDOWN and event.button == 5:
                bild.toggle('rot90')
            elif event.type == KEYDOWN and event.key == K_w:
                bild.toggle('hFlip')
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                bild.toggle('hFlip')
            elif event.type == KEYDOWN and event.key == K_e:
                bild.toggle('vFlip')
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                bild.toggle('vFlip')
            elif event.type == KEYDOWN and event.key == K_r:
                bild.toggle('grey')
            elif event.type == KEYDOWN and event.key == K_f:
                if fullscreen:
                    screen = pygame.display.set_mode((1024,768))
                    fullscreen = False
                    screen_rect = screen.get_rect()
                    bild.resize()
                else:
                    screen = pygame.display.set_mode((fullwidth,fullheight), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
                    fullscreen = True
                    screen_rect = screen.get_rect()
                    bild.resize()
            elif event.type == KEYDOWN and event.key == K_d:
                bild.load_next(True)
            elif event.type == MOUSEBUTTONDOWN and event.button == 2:
                bild.load_next(True)
            elif event.type == KEYDOWN and event.key == K_a:
                bild.load_next(False)
            elif event.type == KEYDOWN and event.key == K_TAB:
                show_info = show_info == False
            elif event.type == KEYDOWN and (event.key == K_s or event.key == K_RETURN):
                statusString = 'Saving...'
                show_status = True
                bild.wand_save()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                bild.toggle('fit')
            elif event.type == MOUSEBUTTONDOWN and event.button == 4:
                bild.toggle('fit')
            elif event.type == KEYDOWN and event.key == K_p:
                save_state('save.mir')
                statusString = 'Saved state.'
                show_status = True
            elif event.type == KEYDOWN and event.key == K_l:
                load_state('autosave.mir')
                bild.load_image(fileNr)
                statusString = 'Loaded autosave.'
                show_status = True
            elif event.type == KEYDOWN and event.key == K_o:
                load_state('save.mir')
                bild.load_image(fileNr)
                statusString = 'Loaded saved state.'
                show_status = True
            elif event.type == KEYDOWN:
                print event.key




        bild.update()

        imagearea = pygame.Surface((pygame.display.Info().current_w, bild.Lrect.height), 0, screen)
        imageareaRect = imagearea.get_rect()
        imageareaRect.centery = pygame.display.Info().current_h / 2


        
        screen.fill ((50, 0, 0))
        imagearea.fill ((50, 0, 0))
        imagearea.blit(bild.Limage, bild.Lrect, bild.Lcrop)
        imagearea.blit(bild.Rimage, bild.Rrect, bild.Rcrop)
        screen.blit(imagearea, imageareaRect)

        #create text surfaces
        if bild.rot90: rot_text = font.render('Rotate 90', False, (0,255,0))
        else: rot_text = font.render('Rotate 90', False, (128,128,128))
        if bild.hFlip: hflip_text = font.render('Flip H', False, (0,255,0))
        else: hflip_text = font.render('Flip H', False, (128,128,128))
        if bild.vFlip: vflip_text = font.render('Flip V', False, (0,255,0))
        else: vflip_text = font.render('Flip V', False, (128,128,128))
        if bild.isGrey: grey_text = font.render('Greyscale', False, (0,255,0))
        else: grey_text = font.render('Greyscale', False, (128,128,128))

        keyrot_text = font.render('Q, Wheel down: Rotate 90', False, (128,128,128))
        keyfliph_text = font.render('W, Mouse L: Flip H', False, (128,128,128))
        keyflipv_text = font.render('E, Mouse R: Flip V', False, (128,128,128))
        zoom_text = font.render('Space, Wheel up: Zoom', False, (128,128,128))

        full_text = font.render('F: Fullscreen', False, (128,128,128))
        info_text = font.render('Tab: Hide info', False, (128,128,128))
        next_text = font.render('D, Wheel click: Next image', False, (128,128,128))
        prev_text = font.render('A: Previous image', False, (128,128,128))
        saveimage_text = font.render('S, Enter: Save image', False, (128,128,128))
        savestate_text = font.render('P: Save state', False, (128,128,128))
        openstate_text = font.render('O: Open saved state', False, (128,128,128))
        prevstate_text = font.render('L: Load autosaved state', False, (128,128,128))
        stat_text = font.render(statusString, False, (128,128,128))
        file_text = font.render(files[fileNr], False, (128,128,128))
        pos_text = font.render('Pos: '+ str(int(bild.mouse_pos_ratio*10000)/100.0)+'...%', False, (128,128,128))
        pos_text_rect = pos_text.get_rect()

        #render texts
        if show_info:
            screen.blit(rot_text, (0,0))
            screen.blit(hflip_text, (120,0))
            screen.blit(vflip_text, (210,0))
            screen.blit(grey_text, (300,0))

            textpos2 = screen_rect.width-200
            screen.blit(keyrot_text, (textpos2-96,0))
            screen.blit(keyfliph_text, (textpos2-72,14))
            screen.blit(keyflipv_text, (textpos2-72,28))
            screen.blit(zoom_text, (textpos2-112,42))
            screen.blit(next_text, (textpos2-104,56))
            screen.blit(prev_text, (textpos2,70))
            screen.blit(full_text, (textpos2,84))
            screen.blit(info_text, (textpos2-16,98))
            screen.blit(saveimage_text, (textpos2-56,112))
            screen.blit(savestate_text, (textpos2,126))
            screen.blit(openstate_text, (textpos2,140))
            screen.blit(prevstate_text, (textpos2,154))
            
            screen.blit(file_text, (0,screen_rect.height-15))
            screen.blit(pos_text, (screen_rect.width-pos_text_rect.width ,screen_rect.height-15))

            screen.blit(stat_text, (0,screen_rect.height-29))
        
        if show_status:
            screen.blit(stat_text, (0,screen_rect.height-29))
            


        pygame.display.flip()

if __name__ == '__main__':
    main()