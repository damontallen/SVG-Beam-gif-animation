from IPython.display import SVG
from numpy import matrix
from numpy.linalg import inv, pinv
from numpy import transpose as T
from collections import namedtuple
from numpy import sin, cos, tan, array, pi
import numpy as np
# from SVG_lib import point

def rotate(point, base, angle, DEBUG = False):
    "Rotates the point about the bas by the angle"
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

