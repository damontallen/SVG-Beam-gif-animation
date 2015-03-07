from collections import namedtuple
import numpy as np

class Point(object):
    def __init__(self, x=0, y=0):
        iteribles = {type([]),type(())}
        if type(x) in iteribles and y==0:
            x, y = x
        self.x = x
        self.y = y
    
    def translate(self,dx=0,dy=0):
        iteribles = {type([]),type(())}
        if type(dx) in iteribles and dy==0:
            dx, dy = dx
        x = self.x + dx
        y = self.y + dy
        return Point(x,y)
    
def pinned(P):
    base = """<path d = "M {},{} L {},{} {},{}"/>
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    """
    peak = Point(P)
    side = 20
    dh = side * np.cos(np.deg2rad(30))
    bR = peak.translate(side/2,dh)
    bL = bR.translate(-side,0)
    gT = []
    gB = []
    g = bL
    step = side/5
    for i in range(6):
        gT.append(g)
        gB.append(g.translate(-10,10))
        g = g.translate(step,0)
    gnd = []
    for t,b in zip(gT,gB):
        gnd+=[t.x,t.y,b.x,b.y]
    sup = base.format(peak.x,peak.y,bR.x,bR.y,bL.x,bL.y,*gnd)
    return sup

def roller(P):
    roller = """<path d = "M {},{} L {},{} {},{}"/>
    <circle cx="{}" cy="{}" r="4" stroke="black" stroke-width="1" fill="none" />
    <circle cx="{}" cy="{}" r="4" stroke="black" stroke-width="1" fill="none" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    <line x1="{}" y1="{}" x2="{}" y2="{}" style="stroke:black;stroke-width:1" />
    """

    peak = Point(P)
    side = 20
    dh = side * np.cos(np.deg2rad(30))
    bR = peak.translate(side/2,dh)
    bL = bR.translate(-side,0)
    gT = []
    gB = []
    cL = bL.translate(4,4)
    cR = bR.translate(-4,4)
    eL = cL.translate(-4,4)
    eR = eL.translate(side,0)
    g = eL
    step = side/5
    for i in range(6):
        gT.append(g)
        gB.append(g.translate(-10,10))
        g = g.translate(step,0)
    gnd = []
    for t,b in zip(gT,gB):
        gnd+=[t.x,t.y,b.x,b.y]

    osup = roller.format(peak.x,peak.y,bR.x,bR.y,bL.x,bL.y,cL.x,cL.y,cR.x,cR.y,eL.x,eL.y,eR.x,eR.y,*gnd)
    return osup

