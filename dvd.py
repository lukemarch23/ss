#!/usr/bin/python3

import pygame
from pygame.locals import *
import time
from physics import physicsEngine
from random import randint
import multiprocessing

def unitValue(x):
    if x>0:return 1
    elif x<0:return -1
    return 0

class dvd():
    def __init__(self):
        self.fps = 40.0
        self.particleCount = 150
        self.text="23"
        self.running = True

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((600,600),HWSURFACE|DOUBLEBUF|RESIZABLE)
        pygame.display.set_caption('23')

        self.background = pygame.Surface(self.screen.get_size()).convert()

        self.ncolour = [0,0,233]
        self.colour = [0,0,233]

        self.parent_conn, self.child_conn = multiprocessing.Pipe()

        self.ph = physicsEngine(self)
        self.ph.daemon = True


    def main(self):
        self.ph.start()
        while self.running:
            t1 = time.time()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    self.running = False
                elif event.type == VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w,event.h),HWSURFACE|DOUBLEBUF|RESIZABLE)
                    self.background = pygame.Surface(self.screen.get_size()).convert()
                elif (event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
                    self.running = False
            objects = self.parent_conn.recv()
            self.parent_conn.send(self.screen.get_size())
            self.render(objects)
            self.clock.tick(self.fps)
            print ("Render FPS:",1.0/(max(time.time()-t1,0.00001)))

    def render(self,objects):
        if self.colour == self.ncolour:self.ncolour = [randint(0,100),randint(0,200),randint(0,255)]
        self.colour[0]+=unitValue(self.ncolour[0]-self.colour[0])
        self.colour[1]+=unitValue(self.ncolour[1]-self.colour[1])
        self.colour[2]+=unitValue(self.ncolour[2]-self.colour[2])

        self.background.fill((0, 0, 0))
        #draw connecting lines
        for u in objects:
            x,y,r,c = u
            for v in c:
                pygame.draw.line(self.background,self.colour,(x,y),v)
        #draw objects infront of lines
        for u in objects:
            x,y,r,c = u
            pygame.draw.circle(self.background,(0,0,233),(int(x),int(y)),int(r))

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

def go():
    d = dvd()
    d.main()

if __name__ == '__main__':
    go()



