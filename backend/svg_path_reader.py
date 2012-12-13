
import math
import re
import logging



class SVGPathReaderClass:
    """
    Handle SVG path data.

    This is where all the geometry gets converted for the
    boundarys output.

    Use this by importing the singleton:
    from svg_path_reader import svgPathReader
    """

    def __init__(self, tolerance2):
        # tolerance2 is in pixel units
        self._tolerance2_global = tolerance2
        self._tolerance2 = tolerance2

    def addPath(self, d, node):
        # http://www.w3.org/TR/SVG11/paths.html#PathData

        def _matrixExtractScale(mat):
            # extract absolute scale from matrix
            sx = math.sqrt(mat[0]*mat[0] + mat[1]*mat[1])
            sy = math.sqrt(mat[2]*mat[2] + mat[3]*mat[3])
            # return dominant axis
            if sx > sy:
                return sx
            else:
                return sy

        # adjust tolerance for possible transforms
        self._tolerance2 = self._tolerance2_global
        totalMaxScale = _matrixExtractScale(node.xformToWorld)
        if totalMaxScale != 0 and totalMaxScale != 1.0:
            self._tolerance2 /= (totalMaxScale)**2
        
        # parse path string
        # HINT: d would perform better as a linked list or iterator (re.finditer)
        d = re.findall('([A-Za-z]|-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)', d)
        for i in range(len(d)):
            try:
                num = float(d[i])
                d[i] = num
            except ValueError:
                # probably a letter, do not convert
                pass
        
        def nextIsNum():
            return (len(d) > 0) and (type(d[0]) is float)
        }
        
        def getNext():
            if len(d) > 0:
                next = d[0]
                d = d[1:] # remove first item
                return next
            else:
                logging.error("not enough parameters")
                return None
        
        x = 0
        y = 0
        cmdPrev = ''
        xPrevCp
        yPrevCp
        subpath = []    
        
        while d:
            cmd = getNext()
            if cmd == 'M':  # moveto absolute
                # start new subpath
                if subpath:
                    node.path.append(subpath)
                    subpath = []
                implicitVerts = 0
                while nextIsNum():
                    x = getNext()
                    y = getNext()
                    subpath.append([x, y])
                    implicitVerts += 1
            elif cmd == 'm':  # moveto relative
                # start new subpath
                if subpath:
                    node.path.append(subpath)
                    subpath = []
                if cmdPrev == '':
                    # first treated absolute
                    x = getNext()
                    y = getNext()
                    subpath.append([x, y])
                implicitVerts = 0       
                while nextIsNum():
                    # subsequent treated realtive
                    x += getNext()
                    y += getNext()
                    subpath.append([x, y])
                    implicitVerts += 1            
            elif cmd == 'Z':  # closepath
                # loop and finalize subpath
                if subpath:
                    subpath.append(subpath[0])  # close
                    node.path.append(subpath);
                    subpath = [];
                }      
            elif cmd == 'z':  # closepath
                # loop and finalize subpath
                if subpath:
                    subpath.append(subpath[0])  # close
                    node.path.append(subpath)
                    subpath = []
            elif cmd == 'L':  # lineto absolute
                while nextIsNum():
                    x = getNext()
                    y = getNext()
                    subpath.append([x, y])
            elif cmd == 'l':  # lineto relative
                while nextIsNum():
                    x += getNext()
                    y += getNext()
                    subpath.append([x, y])
            elif cmd == 'H':  # lineto horizontal absolute
                while nextIsNum():
                    x = getNext()
                    subpath.append([x, y])
            elif cmd == 'h':  # lineto horizontal relative
                while nextIsNum():
                    x += getNext()
                    subpath.append([x, y])
            elif cmd == 'V':  # lineto vertical absolute
                while nextIsNum():
                    y = getNext()
                    subpath.append([x, y])
            elif cmd == 'v':  # lineto vertical realtive
                while nextIsNum():
                    y += getNext()
                    subpath.append([x, y])
            elif cmd == 'C':  # curveto cubic absolute
                while nextIsNum():
                    x2 = getNext()
                    y2 = getNext()
                    x3 = getNext()
                    y3 = getNext()
                    x4 = getNext()
                    y4 = getNext()
                    subpath.append([x,y])
                    self.addCubicBezier(subpath, x, y, x2, y2, x3, y3, x4, y4, 0)
                    subpath.append([x4,y4])
                    x = x4
                    y = y4
                    xPrevCp = x3
                    yPrevCp = y3
            elif cmd == 'c':  # curveto cubic relative
                while nextIsNum():
                    x2 = x + getNext()
                    y2 = y + getNext()
                    x3 = x + getNext()
                    y3 = y + getNext()
                    x4 = x + getNext()
                    y4 = y + getNext()
                    subpath.append([x,y])
                    self.addCubicBezier(subpath, x, y, x2, y2, x3, y3, x4, y4, 0)
                    subpath.append([x4,y4])
                    x = x4
                    y = y4
                    xPrevCp = x3
                    yPrevCp = y3
            elif cmd == 'S':  # curveto cubic absolute shorthand
                while nextIsNum():
                    if cmdPrev in 'CcSs]':
                        x2 = x-(xPrevCp-x)
                        y2 = y-(yPrevCp-y) 
                    else:
                        x2 = x
                        y2 = y              
                    x3 = getNext()
                    y3 = getNext()
                    x4 = getNext()
                    y4 = getNext()
                    subpath.append([x,y])
                    self.addCubicBezier(subpath, x, y, x2, y2, x3, y3, x4, y4, 0)
                    subpath.append([x4,y4])
                    x = x4
                    y = y4
                    xPrevCp = x3
                    yPrevCp = y3
            elif cmd == 's':  # curveto cubic relative shorthand
                while nextIsNum():
                    if cmdPrev in 'CcSs]':
                        x2 = x-(xPrevCp-x)
                        y2 = y-(yPrevCp-y) 
                    else:
                        x2 = x
                        y2 = y              
                    x3 = x + getNext()
                    y3 = y + getNext()
                    x4 = x + getNext()
                    y4 = y + getNext()
                    subpath.append([x,y])
                    self.addCubicBezier(subpath, x, y, x2, y2, x3, y3, x4, y4, 0)
                    subpath.append([x4,y4])
                    x = x4
                    y = y4
                    xPrevCp = x3
                    yPrevCp = y3
            elif cmd == 'Q':  # curveto quadratic absolute
                while nextIsNum():
                    x2 = getNext()
                    y2 = getNext()
                    x3 = getNext()
                    y3 = getNext()
                    subpath.append([x,y])
                    self.addQuadraticBezier(subpath, x, y, x2, y2, x3, y3, 0)
                    subpath.append([x3,y3])
                    x = x3
                    y = y3
            elif cmd == 'q':  # curveto quadratic relative
                while nextIsNum():
                    x2 = x + getNext()
                    y2 = y + getNext()
                    x3 = x + getNext()
                    y3 = y + getNext()
                    subpath.append([x,y])
                    self.addQuadraticBezier(subpath, x, y, x2, y2, x3, y3, 0)
                    subpath.append([x3,y3])
                    x = x3
                    y = y3        
            elif cmd == 'T':  # curveto quadratic absolute shorthand
                while nextIsNum():
                    if cmdPrev in 'QqTt':
                        x2 = x-(xPrevCp-x)
                        y2 = y-(yPrevCp-y) 
                    else:
                        x2 = x
                        y2 = y              
                    x3 = getNext()
                    y3 = getNext()
                    subpath.append([x,y])
                    self.addQuadraticBezier(subpath, x, y, x2, y2, x3, y3, 0)
                    subpath.append([x3,y3])
                    x = x3
                    y = y3 
                    xPrevCp = x2
                    yPrevCp = y2
            elif cmd == 't':  # curveto quadratic relative shorthand
                while nextIsNum():
                    if cmdPrev in 'QqTt':
                        x2 = x-(xPrevCp-x)
                        y2 = y-(yPrevCp-y) 
                    else:
                        x2 = x
                        y2 = y
                    x3 = x + getNext()
                    y3 = y + getNext()
                    subpath.append([x,y])
                    self.addQuadraticBezier(subpath, x, y, x2, y2, x3, y3, 0)
                    subpath.append([x3,y3])
                    x = x3
                    y = y3 
                    xPrevCp = x2
                    yPrevCp = y2
            elif cmd == 'A':  # eliptical arc absolute
                while nextIsNum():
                    rx = getNext()
                    ry = getNext()
                    xrot = getNext()
                    large = getNext()
                    sweep = getNext()
                    x2 = getNext()
                    y2 = getNext()        
                    self.addArc(subpath, x, y, rx, ry, xrot, large, sweep, x2, y2)
                    x = x2
                    y = y2
            elif cmd == 'a':  # elliptical arc relative
                while nextIsNum():
                    rx = getNext()
                    ry = getNext()
                    xrot = getNext()
                    large = getNext()
                    sweep = getNext()
                    x2 = x + getNext()
                    y2 = y + getNext()
                    self.addArc(subpath, x, y, rx, ry, xrot, large, sweep, x2, y2)
                    x = x2
                    y = y2

            cmdPrev = cmd

        # finalize subpath
        if subpath:
            node.path.append(subpath)
            subpath = []
        
    

    def addCubicBezier(self, subpath, x1, y1, x2, y2, x3, y3, x4, y4, level):
        # for details see:
        # http://www.antigrain.com/research/adaptive_bezier/index.html
        # based on DeCasteljau Algorithm
        # The reason we use a subdivision algo over an incremental one
        # is we want to have control over the deviation to the curve.
        # This mean we subdivide more and have more curve points in
        # curvy areas and less in flatter areas of the curve.
        
        if level > 18:
            # protect from deep recursion cases
            # max 2**18 = 262144 segments
            return
        
        # Calculate all the mid-points of the line segments
        x12   = (x1 + x2) / 2.0
        y12   = (y1 + y2) / 2.0
        x23   = (x2 + x3) / 2.0
        y23   = (y2 + y3) / 2.0
        x34   = (x3 + x4) / 2.0
        y34   = (y3 + y4) / 2.0
        x123  = (x12 + x23) / 2.0
        y123  = (y12 + y23) / 2.0
        x234  = (x23 + x34) / 2.0
        y234  = (y23 + y34) / 2.0
        x1234 = (x123 + x234) / 2.0
        y1234 = (y123 + y234) / 2.0

        # Try to approximate the full cubic curve by a single straight line
        dx = x4-x1
        dy = y4-y1

        d2 = math.abs(((x2 - x4) * dy - (y2 - y4) * dx))
        d3 = math.abs(((x3 - x4) * dy - (y3 - y4) * dx))

        if (d2+d3)**2 < 5.0 * self._tolerance2 * (dx*dx + dy*dy):
            # added factor of 5.0 to match circle resolution
            subpath.append([x1234, y1234])
            return

        # Continue subdivision
        self.addCubicBezier(subpath, x1, y1, x12, y12, x123, y123, x1234, y1234, level+1)
        self.addCubicBezier(subpath, x1234, y1234, x234, y234, x34, y34, x4, y4, level+1)



    def addQuadraticBezier(self, subpath, x1, y1, x2, y2, x3, y3, level):
        if level > 18:
            # protect from deep recursion cases
            # max 2**18 = 262144 segments
            return
        
        # Calculate all the mid-points of the line segments
        x12   = (x1 + x2) / 2.0                
        y12   = (y1 + y2) / 2.0
        x23   = (x2 + x3) / 2.0
        y23   = (y2 + y3) / 2.0
        x123  = (x12 + x23) / 2.0
        y123  = (y12 + y23) / 2.0

        dx = x3-x1
        dy = y3-y1
        d = math.abs(((x2 - x3) * dy - (y2 - y3) * dx))

        if d*d <= 5.0 * self._tolerance2 * (dx*dx + dy*dy):
            # added factor of 5.0 to match circle resolution      
            subpath.append([x123, y123])
            return                 
        
        # Continue subdivision
        self.addQuadraticBezier(subpath, x1, y1, x12, y12, x123, y123, level + 1)
        self.addQuadraticBezier(subpath, x123, y123, x23, y23, x3, y3, level + 1)

    
    
    def addArc(self, subpath, x1, y1, rx, ry, phi, large_arc, sweep, x2, y2):
        # Implemented based on the SVG implementation notes
        # plus some recursive sugar for incrementally refining the
        # arc resolution until the requested tolerance is met.
        # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        cp = math.cos(phi)
        sp = math.sin(phi)
        dx = 0.5 * (x1 - x2)
        dy = 0.5 * (y1 - y2)
        x_ = cp * dx + sp * dy
        y_ = -sp * dx + cp * dy
        r2 = ((rx*ry)**2-(rx*y_)**2-(ry*x_)**2) / ((rx*y_)**2+(ry*x_)**2)
        if r2 < 0:
            r2 = 0
        r = math.sqrt(r2)
        if large_arc == sweep:
            r = -r
        cx_ = r*rx*y_ / ry
        cy_ = -r*ry*x_ / rx
        cx = cp*cx_ - sp*cy_ + 0.5*(x1 + x2)
        cy = sp*cx_ + cp*cy_ + 0.5*(y1 + y2)
        
        def _angle(u, v):
            a = math.acos((u[0]*v[0] + u[1]*v[1]) /
                            math.sqrt(((u[0])**2 + (u[1])**2) *
                            ((v[0])**2 + (v[1])**2)))
            sgn = -1
            if u[0]*v[1] > u[1]*v[0]:
                sgn = 1
            return sgn * a
    
        psi = _angle([1,0], [(x_-cx_)/rx, (y_-cy_)/ry])
        delta = _angle([(x_-cx_)/rx, (y_-cy_)/ry], [(-x_-cx_)/rx, (-y_-cy_)/ry])
        if sweep && delta < 0:
            delta += Math.PI * 2
        if !sweep && delta > 0:
            delta -= Math.PI * 2
        
        def _getVertex(pct):
            theta = psi + delta * pct
            ct = Math.cos(theta)
            st = Math.sin(theta)
            return [cp*rx*ct-sp*ry*st+cx, sp*rx*ct+cp*ry*st+cy]        
        
        # let the recursive fun begin
        def _recursiveArc(t1, t2, c1, c5, level, tolerance2):
            def _vertexDistanceSquared(self, v1, v2):
                return (v2[0]-v1[0])**2 + (v2[1]-v1[1])**2
            
            def _vertexMiddle(self, v1, v2):
                return [ (v2[0]+v1[0])/2.0, (v2[1]+v1[1])/2.0 ]

            if level > 18:
                # protect from deep recursion cases
                # max 2**18 = 262144 segments
                return

            tRange = t2-t1
            tHalf = t1 + 0.5*tRange
            c2 = _getVertex(t1 + 0.25*tRange)
            c3 = _getVertex(tHalf)
            c4 = _getVertex(t1 + 0.75*tRange)
            if _vertexDistanceSquared(c2, _vertexMiddle(c1,c3)) > tolerance2:
                _recursiveArc(t1, tHalf, c1, c3, level+1, tolerance2)
            subpath.append(c3)
            if _vertexDistanceSquared(c4, _vertexMiddle(c3,c5)) > tolerance2:
                _recursiveArc(tHalf, t2, c3, c5, level+1, tolerance2)
                
        t1Init = 0.0
        t2Init = 1.0
        c1Init = _getVertex(t1Init)
        c5Init = _getVertex(t2Init)
        subpath.append(c1Init)
        _recursiveArc(t1Init, t2Init, c1Init, c5Init, 0, self._tolerance2)
        subpath.append(c5Init)


# singelton
svgPathReader = SVGPathReaderClass()
