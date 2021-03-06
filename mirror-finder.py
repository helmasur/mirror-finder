﻿import os, pygame, sys, glob, pickle
from pygame.locals import *
from PIL import Image
# from smc.freeimage import Image as smcImage
import cv2


import os
os.mkdir("test")
os.chdir("test")
print(os.getcwd())
os.chdir("..")
print(os.getcwd())
os.rmdir("test")

main_dir = os.getcwd()
data_dir = os.path.join(main_dir, 'data')
img_dir = os.path.join(main_dir, 'input')
out_dir = os.path.join(main_dir, 'output')

files = glob.glob(os.path.join(img_dir, '*.jpg'))
# files.insert(0, os.path.join(data_dir, '01test.jpg')) #inserts a test image/splash at the beginning of file list, allows quick startup and never empty filelist
current_file = -1
statusString = ''

def get_file_path(position):
    global current_file
    if position == 'first': 
        current_file = 0
    elif position == 'next': #next file
        if current_file < len(files)-1: current_file+=1
        else: current_file=0
    elif position == 'current':
        return files[current_file]
    else: #previous file
        if current_file > 0: current_file-=1
        else: current_file = len(files)-1
    return files[current_file]

def save_state(filename):
    state_file = open(filename, 'w') #w for write mode
    pickle.dump(current_file, state_file)
    state_file.close()

def load_state(filename):
    global current_file
    global statusString
    try:
        state_file = open(filename)
        current_file = pickle.load(state_file)
        state_file.close()
    except pygame.error:
        statusString = 'No such file yet.'
        raise SystemExit(str(geterror()))

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

""" def smc_to_surface(image):
    size = image.size
    mode = image.color_type_name
    image = image.toPIL()
    if mode == 'Black':
        image = image.convert('RGB')
    image = image.tostring()
    image = pygame.image.fromstring(image, size, 'RGB', False)
    return image """

class Bild(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.load('first')  #load file

        self.croppos = 0    #position of the mirror
        
    def load(self, position):
        self.rot90 = False
        self.hFlip = False
        self.vFlip = False
        self.fitHeightOnly = False
        self.totalRotation = 0
        self.rotationAdjustment = 0        
        global statusString
        statusString = ''
        self.original = cv2.imread(get_file_path(position))
        self.size = (self.original.shape[1], self.original.shape[0])
        self.original = pygame.image.frombuffer(self.original.tobytes(), self.size, 'BGR')
        self.adaptToView()

    def adaptToView(self):
        self.createFittingImages()
        self.Limage = self.imageForView
        self.Rimage = pygame.transform.flip(self.Limage, True, False)
        self.update_rects()
        
    def createFittingImages(self):
        self.dispsurf = pygame.display.get_surface()
        self.disprect = self.dispsurf.get_rect()
        original_width = self.original.get_rect().width
        original_height = self.original.get_rect().height
        #---get fitting factors for all cases
        #fit view
        self.scaleView = min(1.0 * self.disprect.height / original_height, 1.0 * self.disprect.width/2.0 / original_width)
        self.scaleViewRotated = min(1.0 * self.disprect.height / original_width, 1.0 * self.disprect.width/2.0 / original_height)        
        #fit height only
        self.scaleHeight = 1.0 * self.disprect.height / original_height
        self.scaleHeightRotated = 1.0 * self.disprect.height / original_width
        #---make images for all cases
        #fit view
        width = int(self.scaleView * original_width)
        height = int(self.scaleView * original_height)
        self.imageForView = pygame.Surface((width,height),HWSURFACE,self.original)
        pygame.transform.smoothscale(self.original, (width, height), self.imageForView)
        self.imageForView = pygame.Surface.convert_alpha(self.imageForView)
        #fit height only
        width = int(self.scaleHeight * original_width)
        height = int(self.scaleHeight * original_height)
        self.imageForHeight = pygame.Surface((width,height),HWSURFACE,self.original)
        pygame.transform.smoothscale(self.original, (width, height), self.imageForHeight)
        self.imageForHeight = pygame.Surface.convert_alpha(self.imageForHeight)
        #rotated fit view
        width = int(self.scaleViewRotated * original_width)
        height = int(self.scaleViewRotated * original_height)
        self.imageForViewRotated = pygame.Surface((width,height),HWSURFACE,self.original)
        pygame.transform.smoothscale(self.original, (width, height), self.imageForViewRotated)
        self.imageForViewRotated = pygame.transform.rotate(self.imageForViewRotated, 270)
        self.imageForViewRotated = pygame.Surface.convert_alpha(self.imageForViewRotated)
        #rotated fit height only
        width = int(self.scaleHeightRotated * original_width)
        height = int(self.scaleHeightRotated * original_height)
        self.imageForHeightRotated = pygame.Surface((width,height),HWSURFACE,self.original)
        pygame.transform.smoothscale(self.original, (width, height), self.imageForHeightRotated)
        self.imageForHeightRotated = pygame.transform.rotate(self.imageForHeightRotated, 270)
        self.imageForHeightRotated = pygame.Surface.convert_alpha(self.imageForHeightRotated)

    def resize(self):   #create images fitting the current resolution
        print("INTO RESIZE")

    def remake(self):
        self.rotate()
        self.rotateAdjust(self.rotationAdjustment)
        self.flip()
        self.Rimage = pygame.transform.flip(self.Limage, True, False)
        self.update_rects()

    def toggle(self, item):
        if item == 'rot0':
            self.totalRotation -= self.rotationAdjustment
            self.rotationAdjustment = 0
        if item == 'rot1+':
            self.rotationAdjustment += 1
            self.totalRotation += 1
        if item == 'rot1-':
            self.rotationAdjustment -= 1
            self.totalRotation -= 1
        if item == 'rot5+':
            self.rotationAdjustment += 5
            self.totalRotation += 5
        if item == 'rot5-':
            self.rotationAdjustment -= 5
            self.totalRotation -= 5
        if item == 'rot90':
            self.rot90 = self.rot90 == False
            if self.rot90: self.totalRotation = self.rotationAdjustment + 90
            else: self.totalRotation = self.rotationAdjustment
        elif item == 'hFlip':
            self.hFlip = self.hFlip == False
        elif item == 'vFlip':
            self.vFlip = self.vFlip == False
        elif item == 'fit':
            self.fitHeightOnly = self.fitHeightOnly == False
        self.remake()

    def update_rects(self):
        self.Lrect = self.Limage.get_rect()
        self.Rrect = self.Rimage.get_rect()
        self.Lcrop = self.Lrect.copy()
        self.Rcrop = self.Rrect.copy()

    def rotate(self):
        if self.rot90:
            if self.fitHeightOnly: self.Limage = self.imageForHeightRotated
            else: self.Limage = self.imageForViewRotated
        else:
            if self.fitHeightOnly: self.Limage = self.imageForHeight
            else: self.Limage = self.imageForView

    def rotateAdjust(self, amount):
        self.Limage = pygame.transform.rotate(self.Limage, amount)

    def flip(self):
        if self.hFlip:
            self.Limage = pygame.transform.flip(self.Limage, True, False)
        if self.vFlip:
            self.Limage = pygame.transform.flip(self.Limage, False, True)

    def update(self):
        mouse = pygame.mouse.get_pos()
        mouse = max(mouse[0]-10, 0) #move active area 10px to the right and limit to min 0
        mouse = min(1.0 * mouse / (self.disprect.width-20), 1) #crop active area 10px right and limit to 1
        self.mouse_pos_ratio = mouse
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

    def smc_save(self):
        global statusString
        mirror_pos = self.mouse_pos_ratio
        image = smcImage(files[current_file])

        if self.isGrey: image = image.greyscale()
        if self.rot90: image = image.rotate(90)
        if self.hFlip: image = image.flipHorizontal()
        if self.vFlip: image = image.flipVertical()

        mirror_size = int(image.size[0] * mirror_pos)
        image = image.crop(0,0,mirror_size,image.height)
        new_image = image.clone()
        new_image = new_image.resize(mirror_size*2-1, image.size[1])
        new_image.paste(image, 0, 0)
        image = image.crop(0,0,mirror_size-1,image.height)  #-1 to avoid double center column
        image = image.flipHorizontal()
        new_image.paste(image, mirror_size, 0)

        filename = os.path.basename(files[current_file])
        filename_root = os.path.splitext(filename)[0]
        filename_ext = os.path.splitext(filename)[1]
        filename = filename_root+self.rotateString+self.mirrorString+self.flipString+self.greyString+'_'+str(mirror_size)+filename_ext
        filepath = os.path.join(out_dir, filename)
        new_image.save(filepath)
        statusString = 'Saved: '+filename

def main():

    pygame.init()

    fullwidth = pygame.display.Info().current_w
    fullheight = pygame.display.Info().current_h
    screen = pygame.display.set_mode((840, 900), 0)
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
            elif event.type == KEYDOWN and event.key == K_UP:
                bild.toggle('rot1+')
            elif event.type == KEYDOWN and event.key == K_DOWN:
                bild.toggle('rot1-')
            elif event.type == KEYDOWN and event.key == K_PAGEUP:
                bild.toggle('rot5+')
            elif event.type == KEYDOWN and event.key == K_PAGEDOWN:
                bild.toggle('rot5-')
            elif event.type == KEYDOWN and event.key == K_HOME:
                bild.toggle('rot0')
            elif event.type == KEYDOWN and event.key == K_w:
                bild.toggle('hFlip')
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                bild.toggle('hFlip')
            elif event.type == KEYDOWN and event.key == K_e:
                bild.toggle('vFlip')
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                bild.toggle('vFlip')
            elif event.type == KEYDOWN and event.key == K_f:
                if fullscreen:
                    screen = pygame.display.set_mode((1024,768))
                    fullscreen = False
                    screen_rect = screen.get_rect()
                    bild.adaptToView()
                else:
                    screen = pygame.display.set_mode((fullwidth,fullheight), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
                    fullscreen = True
                    screen_rect = screen.get_rect()
                    bild.adaptToView()
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                bild.load('next')
            elif event.type == MOUSEBUTTONDOWN and event.button == 2:
                bild.load('next')
            elif event.type == KEYDOWN and event.key == K_LEFT:
                bild.load('prev')
            elif event.type == KEYDOWN and event.key == K_TAB:
                show_info = show_info == False
            elif event.type == KEYDOWN and (event.key == K_s or event.key == K_RETURN):
                statusString = 'Saving...'
                show_status = True
                bild.smc_save()
            elif event.type == KEYDOWN and event.key == K_z:
                bild.toggle('fit')
            elif event.type == MOUSEBUTTONDOWN and event.button == 4:
                bild.toggle('fit')
            elif event.type == KEYDOWN and event.key == K_p:
                save_state('save.mir')
                statusString = 'Saved state.'
                show_status = True
            elif event.type == KEYDOWN and event.key == K_l:
                load_state('autosave.mir')
                bild.load('current')
                statusString = 'Loaded autosave.'
                show_status = True
            elif event.type == KEYDOWN and event.key == K_o:
                load_state('save.mir')
                bild.load('current')
                statusString = 'Loaded saved state.'
                show_status = True
            elif event.type == KEYDOWN:
                print(event.key)

        bild.update()

        imagearea = pygame.Surface((pygame.display.Info().current_w, bild.Lrect.height), 0, screen)
        imageareaRect = imagearea.get_rect()
        imageareaRect.centery = pygame.display.Info().current_h / 2
        
        screen.fill ((30, 30, 30))
        imagearea.fill ((30, 30, 30))
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

        keyrot_text = font.render('Q, Wheel down: Rotate 90', False, (128,128,128))
        keyfliph_text = font.render('W, Mouse L: Flip H', False, (128,128,128))
        keyflipv_text = font.render('E, Mouse R: Flip V', False, (128,128,128))
        rot1uptext = font.render('Arrow up: +1 deg.', False, (128,128,128))
        rot1downtext = font.render('Arrow down: -1 deg.', False, (128,128,128))
        rot5uptext = font.render('Page Up: +5 deg.', False, (128,128,128))
        rot5downtext = font.render('Page Down: -5 deg.', False, (128,128,128))
        rot0text = font.render('Home: Reset rotation', False, (128,128,128))
        zoom_text = font.render('Z, Wheel up: Zoom', False, (128,128,128))

        full_text = font.render('F: Fullscreen', False, (128,128,128))
        info_text = font.render('Tab: Hide info', False, (128,128,128))
        next_text = font.render('Right arrow, Wheel click: Next image', False, (128,128,128))
        prev_text = font.render('Left arrow: Previous image', False, (128,128,128))
        saveimage_text = font.render('S, Enter: Save image', False, (128,128,128))
        savestate_text = font.render('P: Save state', False, (128,128,128))
        openstate_text = font.render('O: Open saved state', False, (128,128,128))
        prevstate_text = font.render('L: Load autosaved state', False, (128,128,128))
        stat_text = font.render(statusString, False, (128,128,128))
        file_text = font.render(files[current_file], False, (128,128,128))
        pos_text = font.render('Pos: '+ str(int(bild.mouse_pos_ratio*10000)/100.0)+'...%', False, (128,128,128))
        pos_text_rect = pos_text.get_rect()
        rotation_text = font.render('Rot: '+str(bild.totalRotation), False, (128,128,128))
        rotation_text_rect = rotation_text.get_rect()

        #render texts (8px/letter, 14px/row)
        if show_info:
            screen.blit(rot_text, (0,0))
            screen.blit(hflip_text, (120,0))
            screen.blit(vflip_text, (210,0))

            textpos2 = screen_rect.width-200
            screen.blit(keyrot_text, (textpos2-96,0))
            screen.blit(keyfliph_text, (textpos2-72,14))
            screen.blit(keyflipv_text, (textpos2-72,28))
            screen.blit(rot1uptext, (textpos2-56,42))
            screen.blit(rot1downtext, (textpos2-72,56))
            screen.blit(rot5uptext, (textpos2-48,70))
            screen.blit(rot5downtext, (textpos2-64,84))
            screen.blit(rot0text, (textpos2-24,98))

            screen.blit(zoom_text, (textpos2-80,112))
            screen.blit(next_text, (textpos2-184,126))
            screen.blit(prev_text, (textpos2-72,140))
            screen.blit(full_text, (textpos2,154))
            screen.blit(info_text, (textpos2-16,168))
            screen.blit(saveimage_text, (textpos2-56,182))
            screen.blit(savestate_text, (textpos2,196))
            screen.blit(openstate_text, (textpos2,210))
            screen.blit(prevstate_text, (textpos2,224))
            
            screen.blit(file_text, (0,screen_rect.height-15))
            screen.blit(rotation_text, (screen_rect.width-pos_text_rect.width-rotation_text_rect.width-16,screen_rect.height-15))
            screen.blit(pos_text, (screen_rect.width-pos_text_rect.width ,screen_rect.height-15))

            screen.blit(stat_text, (0,screen_rect.height-29))
        
        if show_status:
            screen.blit(stat_text, (0,screen_rect.height-29))

        pygame.display.update()

if __name__ == '__main__':
    main()