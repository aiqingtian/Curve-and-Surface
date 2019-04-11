import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Generate Bezier curves with de casteljau algorithm
def deca(ps, start, end, step):
    if end == 0:
        return ps[start]
    return (1-step)* deca(ps, start, end-1, step) + step* deca(ps, start+ 1, end -1, step)

def bezier_pts(pts):
    steps = np.linspace(0, 1, num=10000)
    pts_len = len(pts)
    pts_x = pts[:,0]
    pts_y = pts[:,1]
    pts_z = pts[:,2]
    cur_x = []
    cur_y = []
    cur_z = []
    for step in steps:
        cur_x.append(deca(pts_x, 0, pts_len-1, step))
        cur_z.append(deca(pts_z, 0, pts_len-1, step))
        cur_y.append(deca(pts_y, 0, pts_len-1, step))
    cur = np.empty(shape=(len(cur_x), 3))
    cur[:,0] = cur_x
    cur[:,1] = cur_y
    cur[:,2] = cur_z
    return cur_x, cur_y, cur_z, cur

def readVertices(fileName):
    vertices = []
    for line in open(fileName, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'v':
            vertex = []
            vertex.append(float(values[1]))
            vertex.append(float(values[2]))
            vertex.append(float(values[3]))
            # print('v is: ', vertex)
            vertices.append(vertex)
    return vertices

file_path = "curve.txt"
verts = readVertices(file_path)
verts = np.asarray(verts)
cur_x, cur_y, cur_z, cur = bezier_pts(verts)
first_point = (cur_x[0], cur_y[0], cur_z[0])
last_point = (cur_x[-1], cur_y[-1], cur_z[-1])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(xs=cur_x, ys=cur_y, zs=cur_z)
plt.show()
