#
#  The $1 Gesture Recognizer
#
#      Jacob O. Wobbrock
#      The Information School
#      University of Washington
#      Mary Gates Hall, Box 352840
#      Seattle, WA 98195-2840
#      wobbrock@u.washington.edu
#
#      Andrew D. Wilson
#      Microsoft Research
#      One Microsoft Way
#      Redmond, WA 98052
#      awilson@microsoft.com
#
#      Yang Li
#      Department of Computer Science and Engineering
#      University of Washington
#      The Allen Center, Box 352350
#      Seattle, WA 98195-2840
#      yangli@cs.washington.edu
#
# Python port:
# Charlie Von Metzradt, November 2008
# http://sleepygeek.org
#
# Usage example:
#
# from dollar import Recognizer
#
# r = Recognizer()
# r.addTemplate('square', [(1, 10), (3, 8) ... ])
# r.addTemplate('circle', [(4, 7), (5, 13) ... ])
#
# (name, score) = r.recognize([(5, 6), (7, 12), ... ])
#

import math
import numpy as np
import pandas as pd
import os

from sklearn.metrics import ConfusionMatrixDisplay


def read(filepath):
    '''Function that reads a file at the given filepath and returns the informations
    in a dataframe  '''
    try:
        df = pd.DataFrame(columns=['number', 'id', 'time_sequence'])
        lines = [line.strip() for line in open(filepath,'r')]
        number = int(lines[1].split(" ")[3])
        id = int(lines[2].split(" ")[3])
        matrix = []
        for i in range(5,len(lines)):
            line = lines[i].split(",")
            line = np.array(line).astype(np.float64)
            matrix.append([*line[:3]])
        
        df.loc[0] = [number, id, matrix]
        return df
    except IOError as e:
        print("Unable to read dataset file!\n")

directory = 'Sketch-Data-master\SketchData\SketchData\Domain01'

# Contants. Tweak at your peril. :)

numPoints      = 100
cubeSize       = 250.0
halfDiagonal   = 0.5 * math.sqrt(cubeSize * cubeSize + cubeSize * cubeSize + cubeSize * cubeSize)
angleRange     = 45.0
anglePrecision = 2.0
phi            = 0.5 * (-1.0 + math.sqrt(5.0)) # Golden Ratio
 
class Recognizer:
   """The $1 gesture recognizer. See http://sleepygeek.org/projects.dollar for more, or http://depts.washington.edu/aimgroup/proj/dollar/ for the original implementation and paper."""
   

   def __init__(self):
      self.templates=[]

   def recognize(self, points):
      """Determine which gesture template most closely matches the gesture represented by the input points. 'points' is a list of tuples, eg: [(1, 10), (3, 8) ...]. Returns a tuple of the form (name, score) where name is the matching template, and score is a float [0..1] representing the match certainty."""

      points = [Point(point[0], point[1], point[2]) for point in points]
      points = _resample(points, numPoints)
      points = _rotateToZero(points)
      points = _scaleToCube(points, cubeSize)
      points = _translateToOrigin(points)
      
      
      bestDistance = float("infinity")
      bestTemplate = None
      for template in self.templates:
         distance = _distanceAtBestAngle(points, template, -angleRange, +angleRange, anglePrecision)
         if distance < bestDistance:
            bestDistance = distance
            bestTemplate = template

      score = 1.0 - (bestDistance / halfDiagonal)
      return (bestTemplate.name, score)

   def addTemplate(self, name, points):
      """Add a new template, and assign it a name. Multiple templates can be given the same name, for more accurate matching. Returns an integer representing the number of templates matching this name."""
      self.templates.append(Template(name, points))
      
      # Return the number of templates with this name.
      return len([t for t in self.templates if t.name == name])      

   def deleteTemplates(self, name):
      """Remove all templates matching a given name. Returns an integer representing the new number of templates."""

      self.templates = [t for t in self.templates if t.name != name]
      return len(self.templates)

class Point:
   """Simple representation of a point."""
   def __init__(self, x, y, z):
      self.x = x
      self.y = y
      self.z = z

class Rectangle:
   """Simple representation of a rectangle."""
   def __init__(self, x, y, z, width, height, depth):
      self.x = x
      self.y = y
      self.z = z
      self.width = width
      self.height = height
      self.depth = depth

class Template:
   """A gesture template. Used internally by Recognizer."""
   def __init__(self, name, points):
      """'name' is a label identifying this gesture, and 'points' is a list of tuple co-ordinates representing the gesture positions. Example: [(1, 10), (3, 8) ...]"""
      self.name = name
      self.points = [Point(point[0], point[1], point[2]) for point in points]
      self.points = _resample(self.points, numPoints);
      self.points = _rotateToZero(self.points);
      self.points = _scaleToCube(self.points, cubeSize);
      self.points = _translateToOrigin(self.points);
      

def _resample(points, n):
   """Resample a set of points to a roughly equivalent, evenly-spaced set of points."""
   I = _pathLength(points) / (n - 1) # interval length
   D = 0.0
   newpoints = [points[0]]
   i = 1
   while i < len(points) - 1:
      d = _distance(points[i - 1], points[i])
      if (D + d) >= I:
         qx = points[i - 1].x + ((I - D) / d) * (points[i].x - points[i - 1].x)
         qy = points[i - 1].y + ((I - D) / d) * (points[i].y - points[i - 1].y)
         qz = points[i - 1].z + ((I - D) / d) * (points[i].z - points[i - 1].z)
         q = Point(qx, qy, qz)
         newpoints.append(q)
         # Insert 'q' at position i in points s.t. 'q' will be the next i
         points.insert(i, q)
         D = 0.0
      else:
         D += d
      i += 1
    
   #
   # Sometimes we fall a rounding-error short of adding the last point, so add it if so.   
   while (len(newpoints) < n):
      newpoints.append(points[-1])   
   return newpoints

def _rotateToZero(points):
   """Rotate a set of points such that the angle between the first point and the centre point is 0."""
   c = _centroid(points)
   theta2 = math.atan2(c.y - points[0].y, c.x - points[0].x)
   points = _rotateBy(points, -theta2, 2)
   theta1 = math.atan2(c.x - points[0].x, c.z - points[0].z)
   points = _rotateBy(points, -theta1, 1)
   theta0 = math.atan2(c.y - points[0].y, c.z - points[0].z)
   return _rotateBy(points, -theta0, 0)

def _rotateBy(points, theta, axis):
   """Rotate a set of points by a given angle."""
   c = _centroid(points)
   cos = math.cos(theta)
   sin = math.sin(theta)      

   newpoints = []
   for point in points:
      if axis == 2:
         qx = (point.x - c.x) * cos - (point.y - c.y) * sin + c.x
         qy = (point.x - c.x) * sin + (point.y - c.y) * cos + c.y
         qz = point.z
      if axis == 1:
         qx = (point.x - c.x) * cos + (point.z - c.z) * sin + c.x
         qy = point.y
         qz = - (point.x - c.x) * sin + (point.z - c.z) * cos + c.z
      else:
         qx = point.x
         qy = (point.y - c.y) * cos - (point.z - c.z) * sin + c.y
         qz = (point.y - c.y) * sin + (point.z - c.z) * cos + c.z
      newpoints.append(Point(qx, qy, qz))
   return newpoints

def _scaleToCube(points, size):
   """Scale a scale of points to fit a given bounding box."""
   B = _boundingBox(points)
   newpoints = []
   for point in points:
      if B.width==0: qx=0
      else :qx = point.x * (size / B.width)
      if B.height==0: qy=0
      else :qy = point.y * (size / B.height)
      if B.depth==0: qz=0
      else :qz = point.z * (size / B.depth)
      newpoints.append(Point(qx, qy, qz))
   return newpoints

def _translateToOrigin(points):
   """Translate a set of points, placing the centre point at the origin."""
   c = _centroid(points)
   newpoints = []
   for point in points:
      qx = point.x - c.x
      qy = point.y - c.y
      qz = point.z - c.z
      newpoints.append(Point(qx, qy, qz))
   return newpoints

def _distanceAtBestAngle(points, T, a_or, b_or, threshold):
   """Search for the best match between a set of points and a template, using a set of tolerances. Returns a float representing this minimum distance."""
   for ax in range(3):
      a = a_or
      b = b_or
      x1 = phi * a + (1.0 - phi) * b
      f1, theta1 = _distanceAtAngle(points, T, x1, ax)
      x2 = (1.0 - phi) * a + phi * b
      f2, theta2 = _distanceAtAngle(points, T, x2, ax)

      while abs(b - a) > threshold:
         if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = phi * a + (1.0 - phi) * b
            f1, theta1 = _distanceAtAngle(points, T, x1, ax)
         else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = (1.0 - phi) * a + phi * b
            f2, theta2 = _distanceAtAngle(points, T, x2, ax)
      theta = theta1
      if min(f1, f2)==f2:
         theta = theta2
      points = _rotateBy(points, theta,ax)
   return min(f1, f2)

def _distanceAtAngle(points, T, theta, axis):
   """Returns the distance by which a set of points differs from a template when rotated by theta."""
   newpoints = _rotateBy(points, theta,axis)
   return _pathDistance(newpoints, T.points), theta

def _centroid(points):
   """Returns the centre of a given set of points."""
   x = 0.0
   y = 0.0
   z = 0.0
   for point in points:
      x += point.x
      y += point.y
      z += point.z
   x /= len(points)
   y /= len(points)
   z /= len(points)
   return Point(x, y, z)

def _boundingBox(points):
   """Returns a Rectangle representing the bounding box that contains the given set of points."""
   minX = float("+Infinity")
   maxX = float("-Infinity")
   minY = float("+Infinity")
   maxY = float("-Infinity")
   minZ = float("+Infinity")
   maxZ = float("-Infinity")

   for point in points:
      if point.x < minX:
         minX = point.x
      if point.x > maxX:
         maxX = point.x
      if point.y < minY:
         minY = point.y
      if point.y > maxY:
         maxY = point.y
      if point.z < minZ:
         minZ = point.z
      if point.z > maxZ:
         maxZ = point.z

   return Rectangle(minX, minY, minZ, maxX - minX, maxY - minY, maxZ - minZ)

def _pathDistance(pts1, pts2):
   """'Distance' between two paths."""
   d = 0.0
   for index in range(len(pts1)): # assumes pts1.length == pts2.length
      d += _distance(pts1[index], pts2[index])
   return d / len(pts1)

def _pathLength(points):
   """Sum of distance between each point, or, length of the path represented by a set of points."""
   d = 0.0
   for index in range(1, len(points)):
      d += _distance(points[index - 1], points[index])
   return d

def _distance(p1, p2):
   """Distance between two points."""
   dx = p2.x - p1.x
   dy = p2.y - p1.y
   dz = p2.z - p1.z
   return math.sqrt(dx * dx + dy * dy + dz * dz)

#Reading all the files and puting themn in a dataframe
directory = 'Sketch-Data-master\SketchData\SketchData\Domain01'
df = pd.DataFrame(columns=['number', 'id', 'time_sequence'])
for filename in range(1,1001):
    f = os.path.join(directory, str(filename)+".txt")
    # checking if it is a file
    if os.path.isfile(f):
        df=pd.concat([df,read(f)], ignore_index=True)

'''Dollar One Recognizer cross-validation'''

scores = np.zeros((10))
conf_matrix=np.zeros((10,10))
for u in range(10):
    recognizer = Recognizer()
    for user in range(10):
        if user!=u:
            for num in range(10):
                for i in range(10):
                    recognizer.addTemplate(str(num+1), df['time_sequence'][user*100+num*10+i])
    
    for i in range(10):
        for j in range(10):
            result = recognizer.recognize(df['time_sequence'][u*100+i*10+j])
            conf_matrix[int(result[0]) - 1, i] += 1
            if result[0]==str(i+1):
                scores[u]+=1
    scores[u] /= 100
                
print("Average accuracy 3D $1 = "+str(np.mean(scores)))
print("Standard Deviation 3D $1 = "+str(np.std(scores)))
print("Median 3D $1 = "+str(np.median(scores)))
disp=ConfusionMatrixDisplay(conf_matrix)
disp.plot()