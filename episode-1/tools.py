import numpy as np
import math

def v(x,y):
    # vectorize to numpy array which is also a vector 
    return np.array([x,y])

def uv(v):
    # Normalize the given vector to an unit vector
    # https://stackoverflow.com/questions/21030391/how-to-normalize-an-array-in-numpy
    norm = np.linalg.norm(v)
    return v if norm==0 else v/norm;

def norm(v):
    # length of a vector, where v (vector) is a np.array
    return np.linalg.norm(v)

def angle2uv(an):
    # Convert the given absolute angle in degrees to a unit vector that represents the angle
    # see "OneDrive\文件\Jupyter Notebooks\Codingame\Mars Lander\ControlPanel.png" 
    an1 = np.deg2rad(an + 90)  # [X] 09:46 2021/04/04 為何加 90? 可能是絕對角度與儀表板不同？加 90 變成以 X 軸為 0 度吧？
    return uv(v(math.cos(an1), math.sin(an1))) 

def angle15(a0,rotate):
    # rotate command, absolute target angle 最多改變 +-15度 範圍在 [-90,90] 度之間。
    if rotate > a0:
        result = a0 + min(rotate-a0,15)
    else :
        result = a0 - min(a0-rotate,15)
    return max(min(90,result),-90)

def thrust_1(power,thrust):
    # thrust_1 command ?? power ????? +1 or -1 
    result = power
    if thrust > power:
        result += 1
    if thrust < power:
        result -= 1
    return max(min(4,result),0)

# Calculate the euclidian distance between an array of points to a line segment in Python without for loop
# https://stackoverflow.com/questions/54442057/calculate-the-euclidian-distance-between-an-array-of-points-to-a-line-segment-in

def lineseg_dists(p, a, b):
    # where p is an array of points, a,b is the line segment
    if np.all(a == b):
        return np.linalg.norm(p - a, axis=1)

    # normalized tangent vector
    d = np.divide(b - a, np.linalg.norm(b - a))

    # signed parallel distance components
    s = np.dot(a - p, d)
    t = np.dot(p - b, d)

    # clamped parallel distance
    h = np.maximum.reduce([s, t, np.zeros(len(p))])

    # perpendicular distance component, as before
    # note that for the 3D case these will be vectors
    c = np.cross(p - a, d)

    # use hypot for Pythagoras to improve accuracy
    return np.hypot(h, c)
    
print('~~~ Finished loading tools.py ~~~') 