# Path CurveManip.py



from IPython.display import SVG
from numpy import matrix
from numpy.linalg import inv
from numpy import transpose as T
from collections import namedtuple
# from collections import OrderedDict as Dict # Not used yet, intended for beam end lines.
from numpy import sin, cos, tan, array, pi, abs, arctan, sign
import numpy as np
# from SVG_lib import point

def rotate(point, base, angle, DEBUG = False):
    R = matrix(((cos(angle),-sin(angle)),(sin(angle),cos(angle))))
    point = array(point)
    base = array(base)
    tmp = point - base
    R_tmp = array(T(R*T(matrix(tmp)))).reshape((1,2))
    R_point = array(R_tmp[0]+T(base))#.reshape((1,2))
    if DEBUG:
        Debug_rotate = namedtuple('Debug_rotate','point angle_deg tmp R_tmp_size R_tmp base R_point')
        debug = Debug_rotate(point, angle/pi*180, tmp, R_tmp.size, R_tmp, base, R_point)
        print(debug)
        print()
    return R_point

def translate(point, vector):
    "Returns a point (list) that is displaced from the original point be the vector (list)"
    new_point = [x0+dx for x0,dx in zip(point, vector)]
    return new_point

def reflect_y_axis(point):
    "returns a point mirrored about the y axis"
    px, py = point
    return [-px, py]

def reflect_x_axis(point):
    "returns a point mirrored about the x axis"
    px, py = point
    return [px, -py]

def mirror(point, mirror_line = [(0,0),(0,-1)]):
    "Mirror a point about a line defined by two points"
    p0, p1 = mirror_line
    #(p0_x, p0_y), (p1_x, p1_y) = mirror_line
    # Find angle of mirror line
    angle = np.arctan2((p1[1]-p0[1]),(p1[0]-p0[0]))
    # Rotate all points to make mirror line parallel to y-axis
    flip_angles = [-angle,-pi/2]
    for flip_angle in flip_angles:
        p0 = rotate(p0,[0,0],flip_angle)
        p1 = rotate(p1,[0,0],flip_angle)
        point = rotate(point,[0,0],flip_angle) 
    if round((p0[0]-p1[0])*10000)!=0: #check for errors
        er = "problem with fil_angle.  post rotate x0, x1 = {}, {}".format(p0[0],p1[0])
        raise(RuntimeError(er))
    # translaste points so mirror line is on y-axis
    point = translate(point,[-p0[0],0])
    point = reflect_y_axis(point)
    # translate back to original location
    point = translate(point,[p0[0],0])
    # rotate to original angle
    flip_angles = [pi/2,angle]
    for flip_angle in flip_angles:
        point = rotate(point,[0,0],flip_angle)
    p_x, p_y = float(point[0]), float(point[1])
    return [p_x, p_y]

def points(sag, angle=0, DEBUG=False):
    y0 = 5
    p0_i = array([0, y0])
    p1_i = array([100, sag+y0])
    p2_i = array([200, y0])
    rad = angle/180 * pi
    p1 = rotate(p1_i, p0_i, rad, DEBUG=DEBUG)
    p2 = rotate(p2_i, p0_i, rad)
    p0 = [float(p0_i[0]),float(p0_i[1])]
    p1 = [float(p1[0]),float(p1[1])]
    p2 = [float(p2[0]),float(p2[1])]
    if DEBUG:
        Debug_point = namedtuple('Debug_point','p0_i p1_i p2_i angle rad p0 p1 p2')
        debug = Debug_point(p0_i, p1_i, p2_i, angle, rad, p0, p1, p2)
        print(debug)
        print()
    return (p0,p1,p2)
    
def unrotate(p0,p1,p2, DEBUG=False):
    x0,y0 = p0
    x1,y1 = p1
    x2,y2 = p2
    if x2-x1!=0:
        angle = arctan((float(y2)-float(y0))/(float(x2)-float(x0)))
    else:
        angle = pi/2 if y2>y1 else -pi/2
    p1_o = rotate(p1,p0,-angle)
    p2_o = rotate(p2,p0,-angle)
    if DEBUG:
        Debug_unrotate = namedtuple('Debug_unrotate','p0 p1 p2 rad angle p1_o p2_o')
        debug = Debug_unrotate(p0, p1, p2, angle, angle/pi*180, p1_o, p2_o)
        print(debug)
        print()
    return(p0,p1_o,p2_o,float(angle))

def arb_spline(X=[0,0,0],Y=[0,0,0],k0=0,k1=0,k2=0,rot_angle=0,
               fill='none', stroke='black', stroke_width='2'):
    """Returns the information necessary to draw a spline through three points
    
    X is the three x coordinates
    Y is the three y coordinates
    k0,k1,k2 are the slopes at the three points
    rot_angle is the angle that the spline should be rotated after it is drawn
    fill is the fill color of the curve
    stroke is the curves color
    stroke_width is the width of the curve in pixels
    """
    x0,x1,x2 = X
    y0,y1,y2 = Y
    angle = rot_angle
    # Control Points
    cx0 = x0 + x1/2
    cy0 = (x2-x0)*float(k0)/2.25
    cx2 = x2 - x1/2
    cy2 = (x0-x2)*float(k2)/2.25
    
    p0 = [x0,y0]
    p1 = [x1,y1]
    p2 = [x2,y2]
    if angle !=0:
        p1 = rotate(p1,p0,angle,DEBUG=DEBUG)
        p2 = rotate(p2,p0,angle,DEBUG=DEBUG)
        if DEBUG:
            print('\ncx2,cy2 = {},{}'.format(cx2,cy2))
        cx0,cy0 = rotate([cx0,cy0],p0,angle,DEBUG=DEBUG)
        cx0,cy0 = float(cx0),float(cy0)
        cx2,cy2 = rotate([cx2,cy2],p0,angle,DEBUG=DEBUG)
        cx2,cy2 = float(cx2),float(cy2)
    x0,y0 = p0
    x1,y1 = p1
    x1,y1 = float(x1),float(y1)
    x2,y2 = p2
    x2,y2 = float(x2),float(y2)

    dx = x2-x0
    dy = y2-y0
    Coords = namedtuple("Coords", "x0 y0 x1 y1 x2 y2")
    SVG_values = namedtuple("SVG_values","x0 y0 cx0 cy0 cx2 cy2 dx dy")
    coords = Coords(x0,y0,x1,y1,x2,y2)
    svg_values = SVG_values(x0, y0, cx0, cy0, cx2, cy2, dx, dy)
    style = 'fill:%s;stroke:%s;stroke-width:%spx'%(fill, stroke, stroke_width)
    svg_txt = '<path style="%s" d="m %f,%f c %f,%f %f,%f %f,%f"/>'%(style,x0,y0,cx0,cy0,cx2,cy2,dx,dy)
    _path_svg_ = lambda: svg_txt
    Results = namedtuple("Results","coords svg_values _path_svg_")
    results = Results(coords, svg_values, _path_svg_)
    return results

### *** Spline Class *** ###

class Spline(object):
    def __init__(self,p0=[0,10],p2=[100,10], sag = 10):
        self.origin = p0
        self.end = p2
        self.DEBUG = False
        self.fill = 'none'
        self.color = 'black'
        self.width = '2'
        self.sag = sag
        self.circles = True
        
    @property
    def angle(self):
        "Slope from one end to the ofther as a straight line"
        p0 = self.origin
        p2 = self.end
        x0,y0 = p0
        x2,y2 = p2
        return arctan((y2-y0)/(x2-x0))/pi*180
        
    def rotate(self,angle):
        "Rotates the end point about the origin.  The middle is recalculated."
#         angle = self.angle + angle
        rad = angle/180*pi
        self.end = rotate(self.end,self.origin,rad)
        self.sag = self.sag #for a recalculation of the middle point
        #self._angle = angle

    def _center(self):
        "Returns the coordinates exactly in between origin and end."
        p0 = self.origin
        p2 = self.end
        return list((array(p2)-array(p0))/2+array(p0))
    
    @property
    def middle(self):
        return self._middle
    @middle.setter
    def middle(self,p1):
        x0, y0 = self._center
        x1, y1 = p1
        sag = ((x1-x0)^2 + (y1-y0)^2)*sign(y1-y0)*-1
        self.sag = sag
        
    @property
    def sag(self):
        return self._sag
    @sag.setter
    def sag(self,value):
        sag = value
        direct = sign(value)*-1
        angle = self.angle 
        perp = angle-90
        perp_rad = perp/180*pi
        m = tan(perp_rad)
        x0, y0 = self._center()
        x = (sag**2/(1+m**2))**0.5*direct + x0
        y= (sag**2 -(x-x0)**2)**0.5 + y0
        self._middle = [x,y]
        self._sag = sag
        
    def end_angles(self, suppress=False):
        "Returns the angles at both ends of the beam"
        p0, p1, p2, x0, x1, x2, y0, y1, y2, angle = self._points_of_intrest()
        # Calculate angles at ends
        X_1 = inv(matrix(([x0**2,x0,1],[x1**2,x1,1],[x2**2,x2,1])))
        Y = matrix(([y0],[y1],[y2]))
        abc = X_1 * Y
        a, b, c = abc
        a = float(a)
        b = float(b)
        c = float(c)
        # $$\frac{dy}{dx} = 2 a x +b $$
        # $$\theta = \arctan \left( \frac{dy}{dx} \right)$$
        dy_dx = lambda x: 2 *a * x + b
        t0 = np.arctan2(dy_dx(x0),1)+angle
        t2 = np.arctan2(dy_dx(x2),1)+angle
        if not suppress:
            print('abc = {}'.format(abc))
            print(a,b,c)
            print("t0 = {}, t2 = {}, angle = {}".format(np.degrees(t0),
                                                        np.degrees(t2),
                                                        angle))
        Coefficents = namedtuple("Coefficents","a b c")
        coefficents = Coefficents(a,b,c)
        Angles = namedtuple("Angles","theta_0 theta_2 angle coefficents")
        angles = Angles(t0,t2,angle,coefficents)
        return angles
        
    def _points_of_intrest(self):
        DEBUG = self.DEBUG
        p0 = self.origin
        p1 = self.middle
        p2 = self.end
        x0,y0 = p0
        x2,y2 = p2
        
        if y2-y0 !=0:
            p0,p1,p2,angle = unrotate(p0,p1,p2,DEBUG=DEBUG)
        else:
            angle = 0
        if DEBUG:
            print('(p0,p1,p2,angle) = {}'.format((p0,p1,p2,angle)))
        x0,y0 = p0
        x1,y1 = tuple(p1)
        x1,y1 = float(x1),float(y1)
        x2,y2 = p2
        x2,y2 = float(x2),float(y2)
        Points = namedtuple("Points", 'p0 p1 p2 x0 x1 x2 y0 y1 y2, angle')
        points = Points(p0, p1, p2, x0, x1, x2, y0, y1, y2, angle)
        return points

    def _spline(self):
        """Returns the values for a SVG cubic spline that passes through the three points.
        
        This algorithm is based on information found on a Wikipedia page about 
        Spline Interpolation - http://en.wikipedia.org/wiki/spline_interpolation
        Last visited on Feb 26, 2015
        Additional information is available at,
        http://en.wikipedia.org/wiki/B%3C%A9zier_curve (Bezier Curve)
        """
        p0, p1, p2, x0, x1, x2, y0, y1, y2, angle = self._points_of_intrest()
        DEBUG = self.DEBUG
        A = 1/(x1-x0)
        B = 1/(x2-x1)
        A_ = y1-y0
        B_ = y2-y1
        a = matrix(([2*A, A , 0], [A, 2*(A+B), B], [0, B, 2*B]))
        b_ = matrix(((3*A_*A**2), (3*(A_*A**2 + B_*B**2)), (3*(B_*B**2))))
        b = T(b_)
        a_inv = inv(a)
        k = a_inv * b
        k0, k1, k2 = k
        results = self._arb_spline(X=[x0,x1,x2],
                                   Y=[y0,y1,y2],
                                   k0=k0,k1=k1,k2=k2,
                                   rot_angle=angle)
        self.coords = results.coords
        self.svg_values = results.svg_values
        Slopes = namedtuple("Slopes", "k0 k1 k2")
        self.slopes = Slopes(float(k0), float(k1), float(k2))
        
    
    def _repr_svg_(self):
        self._spline()
        path = self._svg_path_()
        x0,y0,x1,y1,x2,y2 = self.coords
        x0, y0, cx0, cy0, cx2, cy2, dx, dy = self.svg_values
        top = min(y0,y1,y2,cy0,cy2)-10
        height = abs(max(y0,y1,y2,cy0,cy2) - top +10)
        left = min(x0,x1,x2,cx0,cx2)-10
        width = abs(max(x0,x1,x2,cx0,cx2) - left +10)
#         br = max(height, width)
    
        style = 'fill:%s;stroke:%s;stroke-width:%spx;'%(self.fill,self.color,self.width)

        a = ['<svg  viewBox = "%f %f %f %f">'%(left,top,width,height),
             path]
        cir = ['<circle cx="%f" cy="%f" r="2" stroke="red" />'%(x0,y0),
               '<circle cx="%f" cy="%f" r="2" stroke="red" />'%(x1,y1),
               '<circle cx="%f" cy="%f" r="2" stroke="red" />'%(x2,y2)]
        b = ['</svg>']
        if self.circles:
            a += cir+b
        else:
            a += b
        svg_txt = '\n'.join(a)
        return svg_txt
    
    def _svg_bounds(self):
        self._spline()
        #p0, p1, p2, x0, x1, x2, y0, y1, y2, angle =self._points_of_intrest()
        x0,y0,x1,y1,x2,y2 = self.coords
        x0, y0, cx0, cy0, cx2, cy2, dx, dy = self.svg_values
        top = min(y0,y1,y2,cy0,cy2)-10
        print("y0,y1,y2,cy0,cy2 = {}".format((y0,y1,y2,cy0,cy2)))
        print("top = {}".format(top))
        height = abs(max(y0,y1,y2,cy0,cy2) - top +10)
        left = min(x0,x1,x2,cx0,cx2)-10
        width = abs(max(x0,x1,x2,cx0,cx2) - left +10)
        Bounds = namedtuple("Bounds","left top width height")
        bounds = Bounds(left,top,width,height)
        return bounds
    
    def _svg_path_(self):
        self._spline()
        x0,y0,x1,y1,x2,y2 = self.coords
        x0, y0, cx0, cy0, cx2, cy2, dx, dy = self.svg_values
    
        style = 'fill:%s;stroke:%s;stroke-width:%spx;'%(self.fill,self.color,self.width)
        path = '<path style="%s" d="m %f,%f c %f,%f %f,%f %f,%f"/>'%(style,x0,y0,cx0,cy0,cx2,cy2,dx,dy)
        return path
    
    def __repr__(self):
        x0, y0 = self.origin
        x1, y1 = self.middle
        x2, y2 = self.end
        sag = self.sag
        center = self._center()
        txt = ['Origin = {}, {}'.format(x0,y0),
               'Middle = {}, {}'.format(x1,y1),
               'End = {}, {}'.format(x2,y2),
               'Center = {}'.format(center),
               'Sag = {}'.format(sag),
               'Angle = {}'.format(self.angle),
               'Circles = {}'.format(self.circles)]
        return '\n'.join(txt)