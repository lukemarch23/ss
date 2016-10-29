import pygame

class Quadtree():
    def __init__(self,level,bounds):
        self.max_levels = 10
        self.max_objects = 10
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
        if self.nodes[0]!=None:
            for i in range(0,4):
                if self.nodes[i].bounds.contains(obj.rect):
                    return i
        return -1

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
        #if obj fits in sub square then recurse
        if index!=-1 :
            ret+=self.nodes[index].retrieveCollisions(obj)
            return ret
        ret+=[u for u in self.objects if u.i>obj.i ]
        #if obj is larger than any, recurse all that it goes into
        if index==-1 and self.nodes[0]!=None:
            for i in range(0,4):
                if obj.rect.colliderect(self.nodes[i].bounds):
                    ret+=self.nodes[i].retrieveCollisions(obj)
        return ret
