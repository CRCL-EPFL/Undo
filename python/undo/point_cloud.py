from undo import PLY_DATA_DIR
from plyfile import PlyData
import numpy as np
import polyscope as ps
import random

class PointCloud:
    def __init__(self, filename = None):
        if filename is not None:
            self.load_from_file(filename)

    def get_vec(self, names=["x", "y", "z"]):
        x = []
        for name in names:
            xi = (self.plydata['vertex'][name]).astype(float)
            x.append(xi)
        return np.vstack(x).T

    def load_from_file(self, filename = 'points.ply'):
        path = PLY_DATA_DIR + "/" + filename
        with open(path, 'rb') as f:
            self.plydata = PlyData.read(f)
            self.vertex = self.get_vec(["x", "y", "z"])
            #self.normal = self.get_vec(["nx", "ny", "nz"])
            self.color = self.get_vec(["red", "green", "blue"]) / 255.0

    def register_points(self):
        self.render = ps.register_point_cloud(name="Point Cloud", points=self.vertex, point_render_mode='quad', radius=0.001)
        self.render.add_color_quantity("color", self.color)

    def register_quantity(self, beam):
        vinds = beam.points_on_planes(self.vertex, beam.planes)
        face = np.zeros(self.vertex.shape[0])
        for id, vind in enumerate(vinds):
            face[vind] = float(id + 1) / len(vinds)
        self.render.add_scalar_quantity("face", face)
        part = np.zeros(self.vertex.shape[0])
        _, inds = beam.trim_points_with_planes(self.vertex, beam.planes)
        part[inds] = 1
        self.render.add_scalar_quantity("part", part)

    def trim(self, inds):
        #self.normal = self.normal[inds]
        self.vertex = self.vertex[inds]
        self.color = self.color[inds]
        self.register_points()

    def trim_with_beam(self, beam):
        flag = beam.cuboid.within_box(self.vertex, beam.args.beam_tol)
        flag = np.logical_not(flag)
        self.trim(flag)

    def n(self):
        return len(self.vertex)

    def sample(self, n):
        id_samples = random.sample(range(0, self.vertex.shape[0]), n)
        self.trim(id_samples)