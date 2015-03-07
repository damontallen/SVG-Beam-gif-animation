from SVG_lib import point, Line
from CurveManip import rotate, mirror
from New_Spline import Spline
import os
from numpy import ceil, log10
from Supports import pinned, roller

class beam(object):
    "For displaying a beam failure"
    def __init__(self):
        self.L_CL = point(10,0)  # These should be renamed, (they are not center lines)
        self.R_CL = point(310,0) # These should be renamed, (they are not center lines)
        self._sag = 0
        self.thickness = 30
        off = self._t/2
        self.centerline = Spline(self.L_CL.List(),self.R_CL.List())
        self.centerline.centerline=True
        top = Spline(self.L_CL.offset_y(-off).List(),self.R_CL.offset_y(-off).List())
        # top.circles=False
        self.top = [top]
        bottom = Spline(self.L_CL.offset_y(off).List(),self.R_CL.offset_y(off).List())
        # bottom.circles=False
        self.bottom = [bottom]
        self.line_width=1
#         End = namedtuple("End",")
        Left = Line(self.L_CL.offset_y(-off),self.L_CL.offset_y(off))
        Left.width = 1
        self.L_end_orig = [Left] # Need to make Line object
        Right = Line(self.R_CL.offset_y(-off),self.R_CL.offset_y(off))
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
        self.splits = []
        self.show_center_line = True
        self.break_line=''
        
    
    @property
    def line_width(self):
        return self._line_width
    @line_width.setter
    def line_width(self, val):
        for top in self.top:
            top.width = str(val)
        for bottom in self.bottom:
            bottom.width = str(val)
        self._line_width = val
    
    @property
    def thickness(self):
        return self._t
    @thickness.setter
    def thickness(self,val):
        self._t = val
    
    @property
    def display_points(self):
        return self._display_points
    @display_points.setter
    def display_points(self,val):
        if type(val)!=type(True):
            raise(ValueError('Must be True or False only!'))
        self._display_points = val
        self.centerline.points = val
        for top in self.top:
            top.points = val
        for bottom in self.bottom:
            bottom.points = val
        for split in self.splits:
            split.points = val
    
    def _set_poly_origin(self,poly_list,end_point):
        x, y = end_point
        poly_list[0].P0 = [x,y]
    
    def _set_poly_end(self,poly_list,end_point):
        x, y = end_point
        poly_list[-1].P3 = [x,y]
    
    @property
    def sag(self):
        return self._sag
    @sag.setter
    def sag(self,val):
        self._sag = val
        self.centerline.sag = val
        angs = self.centerline.end_angles()
        x0_base,y0_base = self.centerline.P0

        if not self.manual_ends:
            L_end =[]
            for line in self.L_end_orig:
                x0, y0 = line.p0.List()
                x0_, y0_ = rotate([x0,y0],base=[x0_base,y0_base],angle=angs.θ_0)
                x0 = float(x0_)
                y0 = float(y0_)
                x1, y1 = line.p1.List()
                x1_, y1_ = rotate([x1,y1],base=[x0_base,y0_base],angle=angs.θ_0)
                x1 = float(x1_)
                y1 = float(y1_)
                new_Line = Line(point(x0,y0), point(x1,y1))
                new_Line.width = self.line_width
                L_end.append(new_Line)
            self.L_end = L_end
        self._set_poly_origin(self.bottom,self.L_end[-1].p1.List())
        self._set_poly_origin(self.top,self.L_end[0].p0.List())
        
        x0_base,y0_base = self.R_CL.List()
        if not self.manual_ends:
            R_end =[]
            for line in self.R_end_orig:
                x0, y0 = line.p0.List()
                x0_, y0_ = rotate([x0,y0],base=[x0_base,y0_base],angle=angs.θ_1)
                x0 = float(x0_)
                y0 = float(y0_)
                x1, y1 = line.p1.List()
                x1_, y1_ = rotate([x1,y1],base=[x0_base,y0_base],angle=angs.θ_1)
                x1 = float(x1_)
                y1 = float(y1_)
                new_Line = Line(point(x0,y0), point(x1,y1))
                new_Line.width = self.line_width
                R_end.append(new_Line)
            self.R_end = R_end
        self._set_poly_end(self.bottom,self.R_end[-1].p1.List())
        self._set_poly_end(self.top,self.R_end[0].p0.List())
        
        if len(self.top)==1:
            self.top[0].sag = val
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            self.bottom[0].sag = val
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        
        
    def mirror_end(self, source='left'):
        source = source.lower().strip()
        if len(self.top)==1:
            a = [float(p) for p in np.array(self.top.P1)-np.array(self.top.P0)]
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            b = [float(p) for p in np.array(self.bottom.P1)-np.array(self.bottom.P0)]
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
        txt =  'sag = {}\n'.format(self.sag)
        txt += 'Origin = {}\n'.format(self.L_CL)
        txt += 'End = {}\n'.format(self.R_CL)
        txt += 'd = {}\n'.format(self.thickness)
        return txt
        
    
    def svg_alt(self):
        path = ('<path\n'
                'style="fill:#CF9B42;fill-rule:evenodd;stroke:{};stroke-width:{}px;stroke-'
                'linecap:square;stroke-linejoin:miter;stroke-opacity:1"\n'
                'd="M {}"\n'
                'inkscape:connector-curvature="0" />\n')
        txt = ''
        top = self.top[0]
        C = top.control_points()
        txt += '{},{} C {},{} {},{} {},{} \n'.format(C.P0[0],
                                                  C.P0[1],
                                                  C.P1[0],
                                                  C.P1[1],
                                                  C.P2[0],
                                                  C.P2[1],
                                                  C.P3[0],
                                                  C.P3[1])
        for line in self.R_end:
            txt+= 'L {},{} '.format(line.p1.x,line.p1.y)+'\n'
        
        if len(self.bottom)==1:
            bot = self.bottom[0]
            C = bot.control_points()
            txt += '{},{} C {},{} {},{} {},{} \n'.format(C.P3[0],
                                                         C.P3[1],
                                                         C.P2[0],
                                                         C.P2[1],
                                                         C.P1[0],
                                                         C.P1[1],
                                                         C.P0[0],
                                                         C.P0[1])
        else:
            bot = self.bottom[-1]
            C = bot.control_points()
            txt += '{},{} C {},{} {},{} {},{} \n'.format(C.P3[0],
                                                         C.P3[1],
                                                         C.P2[0],
                                                         C.P2[1],
                                                         C.P1[0],
                                                         C.P1[1],
                                                         C.P0[0],
                                                         C.P0[1])
            for line in self.break_line:
                txt+= 'L {},{} '.format(line.p1.x,line.p1.y)+'\n'
            bot = self.bottom[0]
            C = bot.control_points()
            txt += '{},{} C {},{} {},{} {},{} \n'.format(C.P3[0],
                                                         C.P3[1],
                                                         C.P2[0],
                                                         C.P2[1],
                                                         C.P1[0],
                                                         C.P1[1],
                                                         C.P0[0],
                                                         C.P0[1])
        for line in self.L_end[::-1]:
            txt+= 'L {},{} '.format(line.p0.x,line.p0.y)+'\n'
        path_txt = path.format(top.color,top.width,txt)
        if len(self.top)==1:
            Top = self.top[0].bounds()
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            Bot = self.bottom[0].bounds()
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        left = min(Top.left, Bot.left)-10
        top = min(Top.top, Bot.top)
        right = max(Top.left+Top.width, Bot.left+Bot.width)+10
        bottom = max(Top.top+Top.height, Bot.top+Bot.height)+30- self.top[0].sag
        width = abs(right-left)
        height = abs(bottom-top)
        txt = '<svg  viewBox = "%f %f %f %f">\n'%(left,top,width,height)
        txt += pinned(self.bottom[-1].P0)
        txt += roller(self.bottom[0].P3)
        txt += path_txt
        
        if self.show_center_line:
            txt += self.centerline.svg_txt()   
        
        for split in self.splits: # for displaying all cracks
            txt+= split.svg_txt()+'\n'
        txt += roller(self.bottom[0].P3)
        txt += pinned(self.bottom[-1].P0)  
        txt +="</svg>"
        return txt
    
    def _repr_svg_(self):
        if len(self.top)==1:
            Top = self.top[0].bounds()
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        if len(self.bottom)==1:
            Bot = self.bottom[0].bounds()
        else:
            er="not implemented!!!!!!"
            raise(RuntimeError(er))
        left = min(Top.left, Bot.left)-10
        top = min(Top.top, Bot.top)
        right = max(Top.left+Top.width, Bot.left+Bot.width)+10
        bottom = max(Top.top+Top.height, Bot.top+Bot.height)+30 - self.top[0].sag
        width = abs(right-left)
        height = abs(bottom-top)
        txt = '<svg  viewBox = "%f %f %f %f">\n'%(left,top,width,height)
        for index,top_ in enumerate(self.top):
            txt+= top_.svg_txt()+'\n'
        for index, bottom_ in enumerate(self.bottom):
            txt+= bottom_.svg_txt()+'\n'
        if self.show_center_line:
            txt += self.centerline.svg_txt()   
        
        for split in self.splits: # for displaying all cracks
            txt+= split.svg_txt()+'\n'
        
        for line in self.L_end:
            txt+= line.svg_line_txt()+'\n'
        for line in self.R_end:
            txt+= line.svg_line_txt()+'\n'
        txt += roller(self.bottom[0].P3)
        txt += pinned(self.bottom[-1].P0)  
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

