from undo.primitives import Beam, BeamCollection
from undo.point_cloud import PointCloud
from undo.primitives import dotdict
import polyscope as ps
import polyscope.imgui as psim
from undo import TXT_DATA_DIR
args = dotdict({
    "max_iter": 1000,
    "beam_width": 0.08,
    "beam_length": 20,
    "beam_tol": 0.01,
    "beam_min_points" : 50
})

beam = None
beam_collections = None
point_cloud = None


def parameters_ui(args):
    tot = False
    changed, args.max_iter = psim.InputInt("max iter", args.max_iter, 100)
    tot = tot or changed
    changed, args.beam_width = psim.InputFloat("beam width", args.beam_width, 0.01)
    tot = tot or changed
    changed, args.beam_length = psim.InputFloat("beam l/w ratio", args.beam_length, 0.1)
    tot = tot or changed
    changed, args.beam_tol = psim.InputFloat("beam tol", args.beam_tol, 0.001)
    tot = tot or changed
    return tot

def reset_render():
    global  beam_collections, point_cloud
    ps.remove_all_structures()
    ps.remove_all_groups()
    beam_collections.register()
    point_cloud.register_points()

def interface():
    global args, beam_collections, point_cloud, beam

    if parameters_ui(args):
        beam.args = args

    if psim.Button("fit"):

        reset_render()
        beam.fit_planes(point_cloud.vertex)
        beam.fit_cuboid(point_cloud.vertex)
        point_cloud.register_quantity(beam)
        beam.register(beam_collections.beam_id)

    psim.SameLine()
    if psim.Button("fit box"):
        beam.fit_cuboid(point_cloud.vertex)
        beam.register(beam_collections.beam_id)

    psim.SameLine()
    if psim.Button("accept"):
        if beam.cuboid is not None:
            #todo: scale a bit to cleam the sceen better
            point_cloud.trim_with_beam(beam)

            beam_collections.add_beam(beam)

            #start looking for next one
            beam = Beam(args)
            point_cloud.register_points()

    psim.SameLine()
    if psim.Button("save"):
        #True is txt, False is binary
        beam_collections.save_beam(TXT_DATA_DIR + "/result.txt", True)

if __name__ == '__main__':
    ps.init()
    ps.set_up_dir("z_up")
    point_cloud = PointCloud("state_C_clean.ply") 
    # downsample 10%
    point_cloud.sample(point_cloud.n())
    point_cloud.register_points()
    beam = Beam(args)
    beam_collections = BeamCollection()
    ps.set_user_callback(interface)
    ps.show()