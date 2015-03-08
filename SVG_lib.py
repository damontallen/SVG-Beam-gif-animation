# name: SVG_lib.py
# type: text/x-python
# size: 4256 bytes 
# ---- 
from collections import OrderedDict as Dict

class point(object):
    def __init__(self, x = 0, y = 0):
        iterator = {type([]),type(())}
        if type(x) in iterator and y==0:
            x,y = x
        self.x = x
        self.y = y
    
    def __repr__(self):
        txt = 'class: point(x = %g, y = %g)'%(self.x, self.y)
        return txt
    
    def __iter__(self):
        yield [self.x,self.y]
    
    def offset_y(self,val):
        return point(self.x,self.y+val)
    def offset_x(self,val):
        return point(self.x+val,self.y)
    def List(self):
        return [self.x, self.y]

colors = Dict()

with open('SVG_colors.txt','r') as f:
    for i, line in enumerate(f):
        if i==0:
            continue
        line = line.strip()
        parts = line.split('\t')
        pieces = []
        for part in parts:
            p = part.strip()
            if len(p)==0:
                continue
            pieces.append(part)
        colors[pieces[0].strip()]=pieces

class Line(object):
    def __init__(self, p0=point(0,0), p1=point(100,100)):
        """p0, and p1 must be passed in as point class memebers or named tuples with x and y"""
        if type(p0)==list:
            p0=point(p0[0],p0[1])
        self.p0 = p0
        if type(p1)==list:
            p1=point(p1[0],p1[1])
        self.p1 = p1
        self.color = 'black'
        self.width = 1
        
    def svg_line_txt(self):
        txt  = '<line x1="%g" y1="%g" '%(self.p0.x, self.p0.y)
        txt += 'x2="%g" y2="%g" '%(self.p1.x, self.p1.y)
        txt += 'style="stroke:%s;'%self.color
        txt += 'stroke-width:%d" />'%self.width
        return txt
    
    def svg_txt(self):
        return self.svg_line_txt()

    @property
    def svg(self):
        txt = '<svg>'
        txt += '<line x1="%g" y1="%g" '%(self.p0.x, self.p0.y)
        txt += 'x2="%g" y2="%g" '%(self.p1.x, self.p1.y)
        txt += 'style="stroke:%s;'%self.color
        txt += 'stroke-width:%d" />'%self.width
        txt += '</svg>'
        return txt
    
    def _repr_svg_(self):
        return self.svg
    
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        value = value.lower()
        check = False
        if value in colors.keys():
            #name
            self._color = value
            check = True
        elif ',' in value:
            #rgb
            try:
                r,g,b = value.split(',')
                self._color = 'rgb(%d,%d,%d)'%(r,g,b)
                check = True
            except:
                pass
        elif 6<=len(value)<=7:
            #hex
            value = value.strip('#')
            try:
                r = int(value[0:2],16)
                g = int(value[2:4],16)
                b = int(value[4:6],16)
                self._color = 'rgb(%d,%d,%d)'%(r,g,b)
                check = True
            except:
                pass
        if not check:
            er = '%s is not a valid SVG color'%value
            raise(ValueError(er))
    
    @property
    def colors(self):
        print(', '.join(colors.keys()))
    
    @property
    def length(self):
        x0,y0 = self.p0.List()
        x1,y1 = self.p1.List()
        return ((x1-x0)**2+(y1-y0)**2)**0.5
    @property
    def direction(self):
        x0,y0 = self.p0.List()
        x1,y1 = self.p1.List()
        return [(x1-x0),(y1-y0)]

class arrow(Line):
    def __init__(self, p0=point(0,0), p1=point(100,100)):
        Line.__init__(self, p0, p1)
    
    @property
    def svg(self):
        txt = '<svg viewBox = "0 0 400 200"> '
        txt += '  <defs>'
        txt += '    <marker id="head" orient="auto" markerWidth="50" markerHeight="100"'
        txt += '            refX="0.25" refY="5">'
        txt += '      <path d="M0,0 V10 L5,5 " fill="red" />'
        txt += '    </marker>'
        txt += '  </defs>    '
        txt += '  <path'
        txt += '    marker-end="url(#head)"'
        txt += '    stroke-width="%d" fill="none" stroke=%s  '%(self.width, self.color)
        txt += '    d="M%d,%d '%(self.p0.x, self.p0.y)
        txt += 'L%d,%d"'%(self.p1.x, self.p1.y)
        txt += '    />    '
#         txt += '<line x1="%d" y1="%d" '%(self.p0.x, self.p0.y)
#         txt += 'x2="%d" y2="%d" '%(self.p1.x, self.p1.y)
#         txt += 'marker-end=url(#head); '
#         txt += 'style="stroke:%s;'%self.color
#         txt += 'stroke-width:%d" />'%self.width
        txt += '</svg>'
        return txt
    
    def _repr_svg_(self):
        return self.svg
