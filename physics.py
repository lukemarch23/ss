import multiprocessing
import pygame
from random import randint,randrange
from math import *
import math
import time

def ins_sort(k,key = lambda x:x):
    for i in range(1,len(k)):
        j = i
        while j > 0 and key(k[j]) < key(k[j-1]):
            k[j], k[j-1] = k[j-1], k[j]
            j=j-1
    return k

class physicsEngine(multiprocessing.Process):
    def __init__(self,dvd):
        super(physicsEngine,self).__init__()
        self.dvd = dvd
        self.w,self.h = self.dvd.screen.get_size()
        self.us = [particle(self.dvd,self) for _ in range(self.dvd.particleCount)]
        self.ps = self.us[:]
        self.running = self.dvd.running

    def run(self):
        while self.running:
            st = time.time()

            #move
            for u in self.us:
                u.move()

            #collision detection
            #broad range
            #self.us.sort(key = lambda x:x.x-x.rad)
            ins_sort(self.us,key = lambda x:x.x-x.rad)
            for ui in range(0,len(self.us)):
                u = self.us[ui]
                for vi in range(ui+1,len(self.us)):
                    v = self.us[vi]
                    if v.x-v.rad>u.x+u.rad:break
                    #narrow range
                    if  u.collide(v):
                        u.bounce(v)

            #find close neighbours
            if self.dvd.drawLines:
                lw = self.dvd.drawLineDistance
                for ui in range(0,len(self.us)):
                    u = self.us[ui]
                    close = []
                    for vi in range(ui+1,len(self.us)):
                        v = self.us[vi]
                        if v.x-u.x>lw:break
                        if u.distsq(v)<lw**2:close.append(v)
                    u.close=close

            #send objects to draw and get stats back
            self.dvd.child_conn.send(self.getDrawableObjects())
            (width,height),self.running = self.dvd.child_conn.recv()
            #check for resize
            if self.w!=width or self.h!=height:
                self.w,self.h=width,height
                self.us = [particle(self.dvd,self) for _ in range(self.dvd.particleCount)]
                self.ps = self.us[:]


            st = time.time()-st
            time.sleep(max(0,1./self.dvd.fps-st))
            print ("Physics FPS: "+str(1./max(0.00001,st)))


    def getDrawableObjects(self):
        return [u.getData() for u in self.ps]

    def renderObjects(self,background):
        for u in self.getObjects():
            u.draw(background)


class particle():
    def __init__(self,dvd,ph):
        self.dvd=dvd
        self.ph=ph

        self.rad = randint(5,12)
        self.x,self.y = (randint(self.rad,self.ph.w-self.rad),randint(self.rad,self.ph.h-self.rad))
        self.systemspeed = randrange(2,3)
        angle = randint(1,360)*pi/180.
        self.dx = cos(angle)*self.systemspeed
        self.dy = sin(angle)*self.systemspeed
        self.close=[]

    def move(self):
        w,h = self.ph.w,self.ph.h
        nx = self.x+self.dx
        ny = self.y+self.dy
        if nx+self.rad>w:
            self.dx = -self.dx
            nx = w-self.rad
        elif nx-self.rad<0:
            self.dx = -self.dx
            nx = self.rad
        elif ny+self.rad>h:
            self.dy = -self.dy
            ny = h-self.rad
        elif ny-self.rad<0:
            self.dy = -self.dy
            ny = self.rad
        self.x,self.y = nx,ny

    def collide(self,other):
        return (self.x-other.x)**2+(self.y-other.y)**2<(self.rad+other.rad)**2

    def bounce(self,other):
        dx = other.x-self.x
        dy = other.y-self.y
        dist = sqrt(dx**2+dy**2)
        impulse = self.rad+other.rad - dist
        ang = atan2(dy,dx)
        ax = impulse*cos(ang)
        ay = impulse*sin(ang)
        self.x-=ax
        self.y-=ay
        speed = (self.systemspeed+other.systemspeed)/2.
        chx = speed*cos(ang)
        chy = speed*sin(ang)
        self.dx -= chx
        self.dy -= chy
        other.dx += chx
        other.dy += chy

    def __str__(self):
        return self.x+","+self.y

    def dist(self,o):
        return sqrt((self.x-o.x)**2+(self.y-o.y)**2)

    def distsq(self,o):
        return (self.x-o.x)**2+(self.y-o.y)**2

    def getData(self):
        return self.x,self.y,self.rad,[(u.x,u.y) for u in self.close]
