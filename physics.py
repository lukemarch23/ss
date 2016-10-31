import multiprocessing
import pygame
import random
from math import *
import math
import time
from quadtree import Quadtree

class physicsEngine(multiprocessing.Process):
    def __init__(self,dvd):
        super(physicsEngine,self).__init__()
        self.dvd = dvd
        self.density = 1000.
        self.mass_of_air = .2
        self.attraction_force = 0.2
        self.w,self.h = self.dvd.screen.get_size()
        self.createQuadtreeParticleSystem()
        self.running = self.dvd.running

    def run(self):
        while self.running:
            st = time.time()

            #move
            for u in self.us:
                u.move()

            #update quadtree
            self.quadtree.update()
            
            #check for collisions in quadtree broadrange
            for u in self.us:
                vs = self.quadtree.retrieveCollisions(u)
                for v in vs:
                    #narrow range collision check
                    collide(u,v)
                    #if u.collide(v):
                    #    u.bounce(v)

            for i in range(0,len(self.us)):
                for v in range(i+1,len(self.us)):
                	self.us[i].attract(self.us[v])
            
            #quadtree neighbours    
            if self.dvd.drawLines:    
                p = particle(self.dvd,self,-1)
                lw = self.dvd.drawLineDistance
                for u in self.us:
                    close = []
                    p.rect = pygame.Rect(u.x-lw,u.y-lw,2*lw,2*lw)
                    vs = self.quadtree.retrieveCollisions(p)
                    for v in vs:
                        if u.distsq(v)<lw**2:
                            close.append(v)
                    u.close=close  

            

            #send objects to draw and get settings back
            self.dvd.child_conn.send(self.getDrawableObjects())
            (width,height),self.running = self.dvd.child_conn.recv()
            #check for resize
            if self.w!=width or self.h!=height:
                self.w,self.h=width,height
                self.createQuadtreeParticleSystem()

            st = time.time()-st
            #tick rate is governed by Pipe passings
            #time.sleep(max(0,1./self.dvd.fps-st))
            print ("Physics FPS: "+str(1./max(0.00001,st)))


    def getDrawableObjects(self):
        return [u.getData() for u in self.ps]

    def createQuadtreeParticleSystem(self):
        self.us = [particle(self.dvd,self,i) for i in range(self.dvd.particleCount)]
        self.ps = self.us[:]
        self.quadtree = Quadtree(0,pygame.Rect(0,0,self.w,self.h),None)
        for u in self.us:
            u.rect = pygame.Rect(u.x-u.rad,u.y-u.rad,u.rad*2,u.rad*2)
            self.quadtree.insert(u)


class particle():
    def __init__(self,dvd,ph,i):
        self.dvd=dvd
        self.ph=ph

        self.rad = random.randint(5, 8)
        self.size = self.rad
        self.x,self.y = (random.randint(self.rad,self.ph.w-self.rad),random.randint(self.rad,self.ph.h-self.rad))
        self.i=i
        self.speed = random.random()*10
        self.angle = random.uniform(0, math.pi*2)
        self.elasticity=.9
        self.mass = math.pi*self.rad**2*self.ph.density
        self.mass = self.ph.density
        self.drag = (self.mass/(self.mass + self.ph.mass_of_air)) ** self.size
        self.close=[]

    def move(self):
        w,h = self.ph.w,self.ph.h
        nx = self.x+sin(self.angle)*self.speed
        ny = self.y-cos(self.angle)*self.speed
        if nx+self.rad>w:
            self.angle = -self.angle
            nx = w-self.rad
            self.speed*=self.elasticity
        elif nx-self.rad<0:
            self.angle = -self.angle
            nx = self.rad
            self.speed*=self.elasticity
        elif ny+self.rad>h:
            self.angle = math.pi-self.angle
            ny = h-self.rad
            self.speed*=self.elasticity
        elif ny-self.rad<0:
            self.angle = math.pi-self.angle
            ny = self.rad
            self.speed*=self.elasticity
        self.x,self.y = nx,ny

    def accelerate(self, vector):
        (self.angle, self.speed) = addVectors(self.angle, self.speed, vector[0],vector[1])
        
    def attract(self, other):
        
        dx = (self.x - other.x)
        dy = (self.y - other.y)
        dist  = math.hypot(dx, dy)
        
        if dist < self.size + self.size:
            return True

        theta = math.atan2(dy, dx)
        force = self.ph.attraction_force * self.mass * other.mass / dist**2
        self.accelerate((theta- 0.5 * math.pi, force/self.mass))
        other.accelerate((theta+ 0.5 * math.pi, force/other.mass))

    def experienceDrag(self):
        self.speed *= self.drag

    def __str__(self):
        return str(self.x)+","+str(self.y)+","+str(self.dx)+","+str(self.dy)

    def dist(self,o):
        return sqrt((self.x-o.x)**2+(self.y-o.y)**2)

    def distsq(self,o):
        return (self.x-o.x)**2+(self.y-o.y)**2

    def getData(self):
        return self.x,self.y,self.rad,[(u.x,u.y) for u in self.close]

def addVectors(angle1, length1, angle2, length2):
    
    x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
    
    angle  = 0.5 * math.pi - math.atan2(y, x)
    length = math.hypot(x, y)

    return (angle, length)

def collide(p1, p2):
    """ Tests whether two particles overlap
        If they do, make them bounce, i.e. update their angle, speed and position """
    
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    
    dist = math.hypot(dx, dy)
    if dist <= p1.size + p2.size:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = p1.mass + p2.mass

        (p1.angle, p1.speed) = addVectors(p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass, angle,         2*p2.speed*p2.mass/total_mass)
        (p2.angle, p2.speed) = addVectors(p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass, angle+math.pi, 2*p1.speed*p1.mass/total_mass)
        elasticity = p1.elasticity * p2.elasticity
        p1.speed *= elasticity
        p2.speed *= elasticity
        #p1.speed = max(p1.speed,1)
        #p2.speed = max(p2.speed,1)

        overlap = 0.5*(p1.size + p2.size - dist+2)
        p1.x += math.sin(angle)*overlap
        p1.y -= math.cos(angle)*overlap
        p2.x -= math.sin(angle)*overlap
        p2.y += math.cos(angle)*overlap

