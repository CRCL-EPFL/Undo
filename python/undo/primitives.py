import numpy as np
import random
from trimesh.primitives import Box
import copy
import polyscope as ps
class dotdict(dict):
    def __getattr__(self, name):
        return self[name]

class Plane:
    def __init__(self,  origin = np.zeros(3), xaxis = np.zeros(3), yaxis = np.zeros(3)):
        '''
        Plane Constructor
        :param origin: plane origin
        :param xaxis:  plane x axis
        :param yaxis:  plane y axis
        '''
        self.xaxis = np.copy(xaxis)
        self.yaxis = np.copy(yaxis)
        self.zaxis = np.cross(self.xaxis, self.yaxis)
        self.origin = np.copy(origin)
        self.normalize()

    def is_same(self, plane):
        '''
        Check if the current plane is the same as the given plane (plane).
        :param plane: the given plane
        :return: True if two planes are the same
        '''
        normal_dist = 1.0 - abs(np.dot(plane.zaxis, self.zaxis))
        zdist = abs(np.dot(plane.origin - self.origin, plane.zaxis))
        if normal_dist < 0.1 and zdist < 0.05:
            return True
        else:
            return False

    def normalize(self):
        '''
        Normalize the plane x, y and z axis
        :return: False if the norms of plane' axes are too small
        '''
        if np.linalg.norm(self.xaxis) < 1E-3:
            return False
        if np.linalg.norm(self.yaxis) < 1E-3:
            return False
        if np.linalg.norm(self.zaxis) < 1E-3:
            return False
        self.xaxis /= np.linalg.norm(self.xaxis)
        self.yaxis /= np.linalg.norm(self.yaxis)
        self.zaxis /= np.linalg.norm(self.zaxis)
        return True

    def within_zdist(self, pts, dist, tol = 0):
        '''
        Check if the given points are within a given distance of this plane in z direction
        :param pts: the points to check
        :param dist: the given distance
        :param tol_ratio: tolerance
        :return: True if the given points are within this distance in the z direction
        '''
        zdist = np.abs((pts - self.origin) @ self.zaxis.T)
        return np.array(zdist <= dist + tol, dtype=bool)

    def within_ydist(self, pts, dist, tol = 0):
        '''
        Check if the given points are within a given distance of this plane in y direction
        :param pts: the points to check
        :param dist: the given distance
        :param tol_ratio: tolerance
        :return: True if the given points are within this distance in the y direction
        '''
        ydist = np.abs((pts - self.origin) @ self.yaxis.T)
        return np.array(ydist <= dist + tol, dtype=bool)

class Cuboid:
    def __init__(self,
                 origin = np.zeros(3),
                 xaxis=np.zeros(3),
                 yaxis=np.zeros(3),
                 extents = np.zeros(3)):
        self.xaxis = np.copy(xaxis)
        self.yaxis = np.copy(yaxis)
        self.zaxis = np.cross(self.xaxis, self.yaxis)
        self.origin = np.copy(origin) # CENTER OF THE CUBOID
        self.extents = np.copy(extents) # DIMENSIONS
        self.normalize()

    def data(self):
        sta = self.origin - self.zaxis * self.extents[2] / 2
        end = self.origin + self.zaxis * self.extents[2] / 2
        sta = list(sta)
        end = list(end)
        return [*sta, *end]

    def normalize(self):
        '''
        Normalize the plane x, y and z axis
        :return: False if the norms of plane' axes are too small
        '''
        if np.linalg.norm(self.xaxis) < 1E-3:
            return False
        if np.linalg.norm(self.yaxis) < 1E-3:
            return False
        if np.linalg.norm(self.zaxis) < 1E-3:
            return False
        self.xaxis /= np.linalg.norm(self.xaxis)
        self.yaxis /= np.linalg.norm(self.yaxis)
        self.zaxis /= np.linalg.norm(self.zaxis)
        return True

    def within_box(self, pts, tol):
        x = np.abs((pts - self.origin) @ self.xaxis.T)
        y = np.abs((pts - self.origin) @ self.yaxis.T)
        z = np.abs((pts - self.origin) @ self.zaxis.T)
        flag = np.ones(pts.shape[0], dtype=bool)
        for id, w in enumerate([x, y, z]):
            flag = flag * (w <= self.extents[id] / 2 + tol)
        return flag

    def get_mesh(self):
        T = np.eye(4)
        T[:3, 3] = self.origin
        T[:3, 0] = self.xaxis
        T[:3, 1] = self.yaxis
        T[:3, 2] = self.zaxis
        return Box(extents=self.extents, transform = T)

class Beam:
    def __init__(self, args):
        '''
        Create a Beam object with given parameters
        :param args: parameters for the beam
        '''
        self.planes = []
        self.cuboid = None
        self.args = args

    def sample_points(self, pts, n):
        '''
        Sample n points from given point cloud pts
        :param pts: point cloud
        :param n: number of points to sample
        :return: sampled points
        '''
        inds = random.sample(range(0, pts.shape[0]), n)
        return pts[inds]

    def trim_points_with_cuboid(self, Vs):
        '''
        Trim the given point cloud using cuboid
        :param pts: point cloud
        :return: trimmed point cloud and points' indices
        '''
        pts = np.copy(Vs)
        pts_inds = np.arange(pts.shape[0])
        flag = self.cuboid.within_box(pts, self.args.beam_tol)
        flag = np.bitwise_not(flag)
        return pts[flag], pts_inds[flag]

    def trim_points_within_point_dist(self, Vs, pt, dist):
        '''
        Trim the given point cloud outside a given distance (dist) to a given point (pt)
        :param Vs: point cloud
        :param pt: point in center
        :param dist: distance
        :return: trimmed point cloud and points' indices
        '''
        pts = np.copy(Vs)
        pts_inds = np.arange(pts.shape[0])
        flag = np.linalg.norm(pts - pt, axis=1) <= dist
        return pts[flag], pts_inds[flag]

    def trim_points_with_planes(self, Vs, planes, enable_yaxis = True):
        '''
        :param Vs: point cloud
        :param planes: planes
        :param enable_yaxis: enable trim in yaxis
        :return: trimmed point cloud and points' indices
        '''
        pts = np.copy(Vs)
        pts_inds = np.arange(pts.shape[0])
        flag = np.ones(pts.shape[0], dtype=bool)
        for plane in planes:
            zflag = plane.within_zdist(pts, self.args.beam_width, self.args.beam_tol)
            if enable_yaxis:
                yflag = plane.within_ydist(pts, self.args.beam_width, self.args.beam_tol)
            else:
                yflag = np.ones(pts.shape[0], dtype=bool)
            flag = (flag * zflag * yflag)
        pts = pts[flag]
        pts_inds = pts_inds[flag]
        return pts, pts_inds

    def points_on_planes(self, Vs, planes):
        '''
        get point set for each plane
        :param Vs: point cloud
        :param planes: planes
        :return: a list of points for each plane
        '''
        pts, pts_inds = self.trim_points_with_planes(Vs, planes)
        plane_pts_inds = []
        for plane in planes:
            flag = plane.within_zdist(pts, self.args.beam_tol) * plane.within_ydist(pts, self.args.beam_width)
            plane_pts_inds.append(np.copy(pts_inds[flag]))
        return plane_pts_inds

    def check_duplicate_plane(self, plane):
        '''
        Check if a plane is duplicated
        :param plane:
        :return: True if the plane is duplicated
        '''
        for prev_plane in self.planes:
            if prev_plane.is_same(plane):
                return True
        return False

    def ransac(self, pts):
        '''
        Use ransac to extract a plane from the given point cloud
        :param pts: point cloud
        :return: plane with most votes
        '''
        best_plane = None
        n_best = self.args.beam_min_points
        for it in range(self.args.max_iter):
            # Samples 2 random points
            samples = self.sample_points(pts, 3)
            origin = samples[2]
            xaxis = samples[1, :] - samples[0, :]
            zaxis = np.cross(xaxis, samples[0, :] - samples[2])
            yaxis = np.cross(zaxis, xaxis)
            plane = Plane(origin=origin, xaxis=xaxis, yaxis=yaxis)

            # skip the plane whether it has too short normal
            # or it is the same as previous planes
            if not plane.normalize():
                continue

            # pts on plane
            flag = plane.within_zdist(pts, self.args.beam_tol)

            # Select indexes where distance is biggers than the threshold
            n_inlier = np.sum(flag)
            if n_inlier > n_best:
                best_plane = plane
                n_best = n_inlier
        return best_plane

    def ransac_with_normal(self, pts, normal):
        '''
        Use ransac to extract a plane from the given point cloud which is perpendicular to a vector (normal)
        :param pts: point cloud
        :param normal: normal vector
        :return: plane with most votes
        '''
        best_plane = None
        n_best = self.args.beam_min_points
        for it in range(self.args.max_iter):
            # Samples 2 random points
            samples = self.sample_points(pts, 2)
            origin = samples[1, :]
            xaxis = samples[1, :] - samples[0, :]
            zaxis = np.cross(xaxis, normal)
            yaxis = np.cross(zaxis, xaxis)
            plane = Plane(origin=origin, xaxis=xaxis, yaxis=yaxis)

            # skip the plane whether it has too short normal
            # or it is the same as previous planes
            if not plane.normalize() or self.check_duplicate_plane(plane):
                continue

            # pts on plane
            flag = plane.within_ydist(pts, self.args.beam_width) * plane.within_zdist(pts, self.args.beam_tol)
            for prev_plane in self.planes:
                flag = flag * prev_plane.within_zdist(pts, self.args.beam_width)

            # Select indexes where distance is biggers than the threshold
            n_inlier = np.sum(flag)
            if n_inlier > n_best:
                best_plane = plane
                n_best = n_inlier
        return best_plane

    def fit_cuboid_with_axis(self, pts, xaxis, yaxis):
        '''
        Fit a cuboid to given point cloud using given axes
        :param pts: point cloud
        :param xaxis: x axis
        :param yaxis: y axis
        :return: a cuboid that fits the given point cloud
        '''

        # formula
        # (p0 + x * xdrt + y * ydrt - p1).dot(ydrt) = width / 2
        # (p0 + x * xdrt + y * ydrt - p0).dot(xdrt) = width / 2

        p0 = self.planes[0].origin
        p1 = self.planes[1].origin
        x = self.args.beam_width / 2
        y = self.args.beam_width / 2 - np.dot(p0 - p1, yaxis)
        origin = p0 + x * xaxis + y * yaxis
        zaxis = np.cross(xaxis, yaxis)

        z_pts = (pts - origin) @ zaxis.T
        z_mean = np.mean(z_pts)
        origin = origin + z_mean * zaxis

        return Cuboid(origin=origin, xaxis=xaxis, yaxis=yaxis, extents=[self.args.beam_width, self.args.beam_width, self.args.beam_width * self.args.beam_length])

    def adjust_cuboid_position(self, pts):
        '''
        Adjust the cuboid position to better fit a given point cloud
        :param pts: point cloud
        :return: a adjusted cuboid
        '''

        n_best = np.sum(self.cuboid.within_box(pts, self.args.beam_tol))
        origin = np.copy(self.cuboid.origin)
        zaxis = np.copy(self.cuboid.zaxis)

        for it in range(self.args.max_iter):
            ct = self.sample_points(pts, 1)[0]
            z_offset = (ct - origin) @ zaxis.T
            new_origin = origin + z_offset * zaxis
            new_cuboid = Cuboid(origin=new_origin, xaxis=self.cuboid.xaxis, yaxis=self.cuboid.yaxis, extents=[self.args.beam_width, self.args.beam_width, self.args.beam_width * self.args.beam_length])
            n_inlier = np.sum(new_cuboid.within_box(pts, self.args.beam_tol))
            if n_inlier > n_best:
                self.cuboid = new_cuboid

    def fit_cuboid(self, Vs):
        '''
        Fit a cuboid to given point cloud
        :param Vs: point cloud
        :return: a cuboid that fits the given point cloud
        '''

        pts, _ = self.trim_points_with_planes(Vs, self.planes)
        if len(self.planes) < 2:
            return None

        xdrts = [self.planes[0].zaxis, -self.planes[0].zaxis]
        ydrts = [self.planes[1].zaxis, -self.planes[1].zaxis]
        n_best = 0
        best_cuboid = None
        for xdrt in xdrts:
            for ydrt in ydrts:
                cuboid = self.fit_cuboid_with_axis(pts, xdrt, ydrt)
                flag = cuboid.within_box(pts, self.args.beam_tol)
                if np.sum(flag) > n_best:
                    n_best = np.sum(flag)
                    best_cuboid = cuboid

        if best_cuboid is not None:
            self.cuboid = best_cuboid
            self.adjust_cuboid_position(pts)
            return True
        return False

    def fit_planes(self, Vs):
        '''
        Fit multiple planes to given point cloud
        :param Vs: point cloud
        :return: False if fitting fails
        '''
        if self.fit_init_plane(Vs):
            return self.fit_plane(Vs)
        return False

    def fit_init_plane(self, Vs):
        '''
        Fit the first planes to given point cloud
        :param Vs: point cloud
        :return: False if fitting fails
        '''
        self.planes = []
        p0 = self.sample_points(Vs, 1)[0]
        pts, _ = self.trim_points_within_point_dist(Vs, p0, 2 * self.args.beam_width)
        if len(pts) < self.args.beam_min_points:
            return False
        init_plane = self.ransac(pts)
        if init_plane is not None:
            return self.fit_plane(Vs, init_plane)
        return False

    def fit_plane(self, Vs, init_plane = None):
        '''
        Fit the second planes to given point cloud
        :param Vs: point cloud
        :param init_plane: first plane
        :return: False if fitting fails
        '''
        if init_plane is None:
            planes = self.planes
            pts, _ = self.trim_points_with_planes(Vs, planes)
        else:
            planes = [*self.planes, init_plane]
            pts, _ = self.trim_points_with_planes(Vs, planes, False)
        for plane in planes:
            new_plane = self.ransac_with_normal(pts, plane.zaxis)
            if new_plane is not None:
                self.planes.append(new_plane)
                return True
        return False

    def register(self, beam_id, color=np.array([1, 0, 0, 1])):
        '''
        register a beam using its cuboid
        :param beam_id: beam id
        :return: Null
        '''
        np.random.seed(beam_id)
        if self.cuboid is not None:
            print(self.cuboid)
            cuboid = self.cuboid.get_mesh()
            return ps.register_surface_mesh(name=f"cuboid_{beam_id:02d}", vertices=cuboid.vertices, faces=cuboid.faces, color = color)

class BeamCollection:

    def __init__(self):
        self.beams = []
        self.beam_id = 0

    def add_beam(self, beam):
        self.beams.append(copy.copy(beam))
        self.beam_id += 1

    def register(self):
        group = ps.create_group("beams")
        for id, beam in enumerate(self.beams):
            render = beam.register(id, np.array([0.89, 0.79, 0.64, 0.8]))
            render.add_to_group(group)
        group.set_hide_descendants_from_structure_lists(True)
        group.set_show_child_details(False)

    def save_beam(self, filename, readable = True):
        from tabulate import tabulate
        import pickle
        result = []
        for beam in self.beams:
            cuboid_data = beam.cuboid.data()
            result.append(cuboid_data)
            #add also plane
            plane = beam.planes[0]
            result.append(plane.xaxis)
            #result.append(plane.yaxis)
        if readable:
            with open(filename, "w") as f:
                f.write(tabulate(result))
        else:
            with open(filename, "wb") as f:
                pickle.dump(result, f)


