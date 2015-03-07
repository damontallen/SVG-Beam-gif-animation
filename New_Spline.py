import numpy.polynomial.polynomial as poly
import numpy as np

from IPython.display import SVG
from numpy import matrix
from numpy.linalg import inv, pinv
from numpy import transpose as T
from collections import namedtuple


Coeffecients = namedtuple('Coeffecients','a b c d e')
_Default_coef = Coeffecients(0,0,0,0,0)

def control_points(P0,P3,Intercept,m0,m1):
    xm,ym = Intercept
    x0,y0 = P0
    x3,y3 = P3
    Y = T(np.matrix(((y0-m0*x0),(y3-m1*x3),(xm-(x0+x3)/8),(ym-(y0+y3)/8))))
    E = np.matrix(((-m0,0,1,0),(0,-m1,0,1),(3/8,3/8,0,0),(0,0,3/8,3/8)))
    C = pinv(E)*Y
    x1 = round(float(C[0])*1E11)/1E11
    x2 = round(float(C[1])*1E11)/1E11
    y1 = round(float(C[2])*1E11)/1E11
    y2 = round(float(C[3])*1E11)/1E11
    Control = namedtuple('Control','P0,P1,P2,P3')
    control = Control((x0,y0),(x1,y1),(x2,y2),(x3,y3))
    return control

def intercept(P0,P3,coef):
    """Returns a namedtuple containing intersection point.
    
    The point is the intersection of the perpendicular 
    bisector of the cord between P0 and P3 and the 
    defection curve that joins them.  The curve is
    defined in by the coeffecients which should be 
    a namedtuple with "a" being the coefficient of
    the fourth order term and "e" being the vertical
    offset (zeroth order term).
    """
    x0,y0 = P0
    x3,y3 = P3
    x_c = (x0+x3)/2
    y_c = (y0+y3)/2
    m = (y3-y0)/(x3-x0)
    if np.abs(m)>1E-6:
        m_perp = -1/m
        b_perp = -m_perp*x_c +y_c
        a,b,c,d,e = coef.a, coef.b, coef.c, coef.d, coef.e
        d -= m_perp
        e -= b_perp
        roots = poly.polyroots(np.array([e,d,c,b,a]))
        found = []
        X = []
        for root in roots:
            if root.imag !=0:
                #print('root.imag = {}'.format(root.imag))
                continue
            x = root.real
            if x>max(x0,x3) or x<min(x0,x3):
                continue
            y_i = a*x**4+b*x**3+c*x**2+coef.d*x+coef.e
            y_p = m_perp*(x)+b_perp
            #print('y_i,y_p = {}'.format((y_i,y_p)))
            if round(y_i*1E4) == round((y_p)*1E4):
                X.append(x)
                found.append(y_i)
        if len(found)>1:
            er="We have a problem, {} all are the y interscepts".format(found)
            raise(RuntimeError(er))
        else:
            try:
                y_i = found[0]
                x_i = X[0]
            except:
                val = {'m':m,'x_c':x_c,'y_c':y_c,'m_perp':m_perp,'b_perp':b_perp,'x0':x0,'x3':x3,'roots':roots}
                er = 'Error! No soluion found. {}'.format(val)
                raise(RuntimeError(er))
    else:
        a,b,c,d,e = coef.a, coef.b, coef.c, coef.d, coef.e
        y_i = a*x_c**4+b*x_c**3+c*x_c**2+coef.d*x_c+coef.e
        x_i = x_c
    Intercept = namedtuple('Intercept','x_i y_i')
    inter = Intercept(x_i,y_i)
    return inter

def dist(p0,p1):
    x0,y0 = p0
    x1,y1 = p1
    return ((x1-x0)**2+(y1-y0)**2)**0.5

class Spline(object):
    def __init__(self,P0=[0,0],P3=[100,0],coef=_Default_coef):
        self.P0 = P0
        self.P3 = P3
        self.fill = 'none'
        self.color = 'black'
        self.width = '1'
        self.points = True
        self.coef = coef
        self._EI = 1
        self.sag = 0
        self.buffer = 10
        if coef != _Default_coef:
            self.coef = coef
            self.automatic_coef = False
        else:
            self.automatic_coef = True
        self.centerline = False
        
    @property
    def L(self):
        return dist(self.P0,self.P3)
    
    @property
    def _w(self):
        """Returns the assumed uniform load based on the current deflection
        
        This is used in the locating of coordinates on the spline and
        the slopes at those points."""
        L = self.L
        D = self.sag
        EI = self._EI
        w = D*384*EI/(5*L**4)
        return w
        
    def Y_(self,x):
        """Returns the vertical location based on an absolute horizontal location
        
        This is done using a curve based on the coefficients and adjusting for 
        the end point location."""
        a,b,c,d,e = self.Coefficients()
        y = a*x**4+b*x**3+c*x**2+d*x+e
        return y
    
    
    def Coefficients(self):
        if self.automatic_coef:
            x0, y0 = self.P0
            EI = self._EI
            w = self._w
            L = self.L
            mod = w/(2*EI)
            a = mod/12
            b = mod/3*-(L/2 + x0)
            c = mod/2*(L*x0+x0**2)
            d = mod*(L**3/12-L*x0**2/2-x0**3/3)
            e = mod/6*(-L**3*x0/2+L*x0**3+x0**4/2)+y0  # 0 if spline starts at 0,0
            coef = Coeffecients(a,b,c,d,e)
        else:
            coef = self.coef
        return coef
    
    def P_M(self):
        "Returns the point that the spline is passing through."
        M = intercept(self.P0,self.P3,self.Coefficients())
        return M
        
    def end_angles(self):
        m0 = self.instant_slope(self.P0)
        m1 = self.instant_slope(self.P3)
        θ_0 = np.arctan2(m0,1)
        θ_1 = np.arctan2(m1,1)
        Angles = namedtuple('Angles','θ_0 θ_1')
        return Angles(θ_0,θ_1)
    
    def instant_slope(self,P):
        x,y = P
        a,b,c,d,e = self.Coefficients()
        m = 4*a*x**3+3*b*x**2+2*c*x+d
        return m
    
    def control_points(self):
        P0 = self.P0
        P3 = self.P3
        Intercept = self.P_M()
        m0 = self.instant_slope(P0)
        m1 = self.instant_slope(P3)
        C = control_points(P0,P3,Intercept,m0,m1)
        return C
    
    def __repr__(self):
        txt = 'Spline data:\n'
        for item, value in self.__dict__.items():
            txt +="{} = {}\n".format(item, value)
        return txt
    
    def bounds(self):
        C = self.control_points()
        top = min([P[1] for P in C])
        bottom = max([P[1] for P in C])
        height = bottom - top
        left = min([P[0] for P in C])
        right = max([P[0] for P in C])
        width = right-left
        Bounds = namedtuple('Bounds','left top width height')
        buf = self.buffer
        b = Bounds(left-buf, top-buf, width+2*buf, height+2*buf)
        return b
        
    def svg_txt(self):
        circle = '<circle cx="{}" cy="{}" r="2" stroke="{}" stroke-width="1" fill="none" />'+'\n'
        cL = ' stroke-dasharray="20,5,5,5" ' 
        path = ('<path%s\n'
                'style="fill:none;fill-rule:evenodd;stroke:{};stroke-width:{}px;stroke-'
                'linecap:square;stroke-linejoin:miter;stroke-opacity:1"\n'
                'd="M {},{} C {},{} {},{} {},{}"\n'
                'inkscape:connector-curvature="0" />\n')
        path = path%cL if self.centerline else path%''
        txt=''
        if self.points:
            txt += circle.format(self.P0[0],self.P0[1],self.color)
            txt += circle.format(self.P3[0],self.P3[1],self.color)
            M = self.P_M()
            txt += circle.format(M[0],M[1],self.color)
        C = self.control_points()
        txt += path.format(self.color,self.width,C.P0[0],C.P0[1],C.P1[0],C.P1[1],C.P2[0],C.P2[1],C.P3[0],C.P3[1])
        return txt
                   
    def _repr_svg_(self):
        b = self.bounds()
        txt='<svg  viewBox = "%f %f %f %f">\n'%(b.left,b.top,b.width,b.height)
        txt += self.svg_txt()
        txt += '</svg>'
        return txt



