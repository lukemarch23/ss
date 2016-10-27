import pygame

class Quadtree():
    def __init__(self,level,bounds):
        self.max_levels = 100
        self.max_objects = 1
        self.level = level
        self.objects = []
        self.bounds = bounds
        self.nodes = [None]*4

    def clear(self):
        self.objects = []
        for i in range(4):
            if self.nodes[i]!=None:
                self.nodes[i].clear()
                self.nodes[i]=None

    def split(self):
        subWidth = int(self.bounds.w/2)
        subHeight = int(self.bounds.h/2)
        x = int(self.bounds.x)
        y = int(self.bounds.y)
        self.nodes[0] = Quadtree(self.level+1,pygame.Rect(x+subWidth,   y,          subWidth,subHeight))
        self.nodes[1] = Quadtree(self.level+1,pygame.Rect(x,            y,          subWidth,subHeight))
        self.nodes[2] = Quadtree(self.level+1,pygame.Rect(x,            y+subHeight,subWidth,subHeight))
        self.nodes[3] = Quadtree(self.level+1,pygame.Rect(x+subWidth,   y+subHeight,subWidth,subHeight))

    def getIndex(self,obj):
        index = -1
        verticalMidpoint = self.bounds.x+self.bounds.w/2
        horizontalMidpoint = self.bounds.y+self.bounds.h/2

        topQuadrant = obj.rect.y<horizontalMidpoint and obj.rect.y+obj.rect.h<horizontalMidpoint
        bottomQuadrant = obj.rect.y>horizontalMidpoint

        if obj.rect.x<verticalMidpoint and obj.rect.x+obj.rect.w<verticalMidpoint:
            if topQuadrant:
                index = 1
            elif bottomQuadrant:
                index = 2
        elif obj.rect.x>verticalMidpoint:
            if topQuadrant:
                index = 0
            elif bottomQuadrant:
                index = 3
        return index

    def insert(self,obj):
        if self.nodes[0]!=None:
            index = self.getIndex(obj)
            if index!=-1:
                self.nodes[index].insert(obj)
                return
        self.objects.append(obj)

        if len(self.objects)>self.max_objects and self.level<self.max_levels:
            if self.nodes[0]==None:
                self.split()
            keep = []
            for i in self.objects:
                index = self.getIndex(i)
                if index!=-1:
                    self.nodes[index].insert(i)
                else:
                    keep.append(i)
            self.objects = keep


    def retrieveCollisions(self,obj):
        ret = []
        index = self.getIndex(obj)
        if index!=-1 and self.nodes[0]!=None:
            ret+=self.nodes[index].retrieveCollisions(obj)
        ret+=self.objects
        return ret
