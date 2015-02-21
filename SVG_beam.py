# name: SVG_beam.py
# type: text/x-python
# size: 4309 bytes 
# ---- 
from SVG_lib import point, Line
from CurveManip import Spline, rotate, mirror
import os
from numpy import ceil, log10

class beam(object):
    "For displaying a beam failure"
    def __init__(self):
        self.L_CL = point(10,10)  # These should be renamed, (they are not center lines)
        self.R_CL = point(300,10) # These should be renamed, (they are not center lines)
        self._sag = 0
        self.thickness = 30
        t = self._t
        top = Spline(self.L_CL.List(),self.R_CL.List(),self.sag)
        top.circles=False
        self.top = [top]
        bottom = Spline(self.L_CL.offset_y(t).List(),self.R_CL.offset_y(t).List(), self.sag)
        bottom.circles=False
        self.bottom = [bottom]
        self.line_width=1
#         End = namedtuple("End",")
        Left = Line(self.L_CL,self.L_CL.offset_y(t))
        Left.width = 1
        self.L_end_orig = [Left] # Need to make Line object
        Right = Line(self.R_CL,self.R_CL.offset_y(t))
        Right.width = 1
        self.R_end_orig = [Right] # Need to make Line object
        self.L_end = self.L_end_orig.copy()
        self.R_end = self.R_end_orig.copy()
        self._filename = None
        self._path = None
        self._extension = None
#         self._filename = None
        self._warned = False # for setting the maximum file number in save method
        self.manual_ends = False
        
    
    @property
    def line_width(self):
        return self._line_width
    @line_width.setter
    def line_width(self, val):
        for top in self.top:
            top.width = str(val)
        for bottom in self.bottom
            bottom.width = str(val)
        self._line_width = val
    
    @property
    def thickness(self):
        return self._t
    @thickness.setter
    def thickness(self,val):
        self._t = val
        
    @property
    def sag(self):
        return self._sag
    @sag.setter
    def sag(self,val):
        if len(self.top)==1:
            self.top[0].sag = val
            angs = self.top.end_angles(suppress=True)
        else:
            angs_0 = self.top[0].end_angles(suppress=True)
            angs_1 = self.top[-1].end_angles(suppress=True)
            angs = [angs_0[0],angs_1[1]] # I am assuming these are ordered this way (Feb 21, 2015)
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            self.bottom[0].sag = val
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        
        x0_base,y0_base = self.L_CL.List()
        #Left_bottom = rotate([self._t,y0_base],base=[x0_base,y0_base],angle=angs.theta_0+pi/4)
        #bx0, by0 = Left_bottom
        #self.bottom.origin = [float(bx0), float(by0)]
        if not self.manual_ends:
            L_end =[]
            for line in self.L_end_orig:
                x0, y0 = line.p0.List()
                x0_, y0_ = rotate([x0,y0],base=[x0_base,y0_base],angle=angs.theta_0)
                x0 = float(x0_)
                y0 = float(y0_)
                x1, y1 = line.p1.List()
                x1_, y1_ = rotate([x1,y1],base=[x0_base,y0_base],angle=angs.theta_0)
                x1 = float(x1_)
                y1 = float(y1_)
                new_Line = Line(point(x0,y0), point(x1,y1))
                new_Line.width = self.line_width
                L_end.append(new_Line)
            self.L_end = L_end
        bot = self.L_end[-1]
        bx0,by0 = bot.p1.List()
        if len(self.bottom)==1:
            self.bottom.origin = [bx0,by0]
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        
        x0_base,y0_base = self.R_CL.List()
        #Right_bottom = rotate([self._t,y0_base],base=[x0_base,y0_base],angle=angs.theta_2+pi/4)
        #bx0, by0 = Right_bottom
        #self.bottom.end = [float(bx0), float(by0)]
        if not self.manual_ends:
            R_end =[]
            for line in self.R_end_orig:
                x0, y0 = line.p0.List()
                x0_, y0_ = rotate([x0,y0],base=[x0_base,y0_base],angle=angs.theta_2)
                x0 = float(x0_)
                y0 = float(y0_)
                x1, y1 = line.p1.List()
                x1_, y1_ = rotate([x1,y1],base=[x0_base,y0_base],angle=angs.theta_2)
                x1 = float(x1_)
                y1 = float(y1_)
                new_Line = Line(point(x0,y0), point(x1,y1))
                new_Line.width = self.line_width
                R_end.append(new_Line)
            self.R_end = R_end
        bot = self.R_end[-1]
        bx0,by0 = bot.p1.List()
        if len(self.bottom)==1:
            self.bottom.end = [bx0,by0]
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        
    def mirror_end(self, source='left'):
        source = source.lower().strip()
        if len(self.top)==1:
            a = self.top._center
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            b = self.bottom._center
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if source == 'left':
            R_end=[]
            for line in self.L_end:
                p0 = line.p0.List()
                p1 = line.p1.List()
                p0 = mirror(p0,[a,b])
                p1 = mirror(p1,[a,b])
                R_end.append(Line(point(*p0),point(*p1)))
            self.R_end = R_end
        elif source == 'right':
            L_end = []
            for line in self.R_end:
                p0 = line.p0.List()
                p1 = line.p1.List()
                p0 = mirror(p0,[a,b])
                p1 = mirror(p1,[a,b])
                L_end.append(Line(point(*p0),point(*p1)))
            self.L_end = L_end
        else:
            er= "The only sources that may be specified are left or right."
            raise(ValueError(er))
        
    def __repr__(self):
        pass
    
    def _repr_svg_(self):
        #txt = "<svg>\n"
        if len(self.top)==1:
            Top = self.top._points_of_intrest()
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            Bot = self.bottom._points_of_intrest()
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        # a = ['<svg  viewBox = "%f %f %f %f">'%(left,top,width,height),
        left = min(Top.x0,Top.x1,Top.x2, Bot.x0,Bot.x1,Bot.x1)-10
        top = min(Top.y0,Top.y1,Top.y2, Bot.y0,Bot.y1,Bot.y1)-10
        right = max(Top.x0,Top.x1,Top.x2, Bot.x0,Bot.x1,Bot.x1)+10
        bottom = max(Top.y0,Top.y1,Top.y2, Bot.y0,Bot.y1,Bot.y1)+10
        width = abs(right-left)+10
        # print("top_b.height, bottom_b.height = {}".format((top_b.height, bottom_b.height)))
        height = abs(bottom-top)+10
        txt = '<svg  viewBox = "%f %f %f %f">\n'%(left,top,width,height)
        for top_ in self.top:
            txt+= top_._svg_path_()+'\n'
        for bottom_ in self.bottom:
            txt+= bottom_._svg_path_()+'\n'
        
        for line in self.L_end:
            txt+= line.svg_line_txt()+'\n'
        for line in self.R_end:
            txt+= line.svg_line_txt()+'\n'
        txt +="</svg>"
        return txt
    
    def save(self, filename=""):
        if not self._warned:
            max_file_num = input(("What is the maximum number of versions "
                                  "of this beam do you want to save? "
                                  "[1000]")) or '1000'
            self.max_file_number = int(max_file_num)
            self._warned = True
            self._suffix_count = int(ceil(log10(self.max_file_number)))
        if filename == "" and self._filename!=None:
            filename = self._filename # reuse last filename
            path = self._path
            extension = self._extension
            count = self._count
        elif filename != "":
            path = '/'.join(filename.split('/')[:-1])
            path = '.' if path =='' else path
            self._path = path
            filename = filename.split('/')[-1]
            extension = filename.split('.')[-1].lower()
            filename = '.'.join(filename.split('.')[:-1]) if extension == 'svg' else filename
            self._filename = filename
            extension = '.svg'
            self._extension = extension
            count = 0
            self._count = count
        else:
            er="A file name must be provided at least once."
            raise(ValueError(er))
            
        def Filename(num):
            sufix = '-{:{fill}>{width}}'.format(num,fill='0',width=self._suffix_count)
            File = path+'/'+filename+sufix+extension
            return File
            
        if os.path.exists(Filename(count)):
            files_ = os.listdir(self._path)
            numbers = []
            for name in files_:
                if filename in name:
                    numbers.append(int(name.strip(extension).strip(filename).strip('-')))
            count = max(numbers)+1
            self._count=count
        if count == 0:
            print("Saving first svg drawing to: {}".format(Filename(count)))
        with open(Filename(count),'w') as f:
            f.write(self._repr_svg_())