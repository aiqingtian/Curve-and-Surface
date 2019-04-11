# Generate a surface by revolving curve along Z axis with Bezier curve using Blender
import numpy as np
import math
import bpy
import bmesh
from math import radians

# Read vertices from file, check curve.txt for samples
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

# De casteljau algorithm
def deca(ps, start, end, step):
    if end == 0:
        return ps[start]
    return (1-step)* deca(ps, start, end-1, step) + step* deca(ps, start+ 1, end -1, step)

# Generate Bezier points with De casteljau algorithm
def bezier_pts(pts):
    steps = np.linspace(0, 1, num=1000)
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

def axis_unit(axis):
    axis = np.asarray(axis)
    unit_axis = axis/math.sqrt(np.dot(axis, axis))
    return unit_axis

def rotate_point(axis, angle, pt):
    unit_axis = axis_unit(axis)
    a = math.cos(angle/2.0)
    b, c, d = -unit_axis*math.sin(angle/2.0)
    rotate_mtx = np.array([[a*a + b*b - c*c - d*d, 2 * (b*c + a*d), 2 * (b*d - a*c)],
                           [2 * (b*c - a*d), a*a + c*c - b*b - d*d, 2 * (c*d + a*b)],
                          [2 * (b*d + a*c), 2 * (c*d - a*b), a*a + d*d - b*b - c*c]])
    rotated_pt = np.dot(rotate_mtx, pt)
    return rotated_pt

def vert_circle(axis, pt, steps):
    verts = []
    for i in range(steps):
        angle = 2*math.pi*(i/steps)
        verts.append(rotate_point(axis,angle, pt))
    return verts

def makeFace(steps, i, layer):
    if i == steps-1:
        start = steps*layer
        b = steps*(layer + 1)
        return (b-1, start, b, (b+steps)-1)
    else:
        b = (steps*layer) + i
        return (b, b+1, b+steps+1, b+steps)

def makeMesh(name, steps, pts, axis):
    verts = []
    faces = []
    npts = len(pts)
    for i in range(npts):
        verts.extend(vert_circle(axis, pts[i], steps))
    for j in range(steps):
        for layer in range(npts-1):
            faces.append(makeFace(steps, j, layer))
    return verts, faces

def triangulate_object(obj):
    me = obj.data
    # Get a BMesh representation
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    bm.free()
    return me

def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name + 'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True
    me.from_pydata(verts, [], faces)
    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True
    # Create mesh from given verts, faces.
    # Update mesh with new data
    me = triangulate_object(ob)
    me.update()
    return ob

def applyModifier(mod, objA, objB):
    target = objA
    bpy.context.scene.objects.active = target
    boo = target.modifiers.new('Booh', 'BOOLEAN')
    boo.object = objB
    boo.operation = mod
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Booh")
    bpy.context.scene.objects.unlink(objB)
    return target

file_path = r'c:\Github\curve.txt'
verts = readVertices(file_path)
verts = np.asarray(verts)
cur_x, cur_y, cur_z, cur = bezier_pts(verts)
pts_len = cur.shape[0]
axis = (0,0,1)
verts, faces = makeMesh('surface', steps=128, pts=cur, axis=axis)
createMeshFromData('surface', origin=(0, 0, 0), verts=verts, faces=faces)