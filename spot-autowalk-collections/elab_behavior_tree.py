"""
lt6_mission.py -- build and run the LT6 patrol/dance mission on Spot.

Loads the recorded `lt6 inspection` autowalk, hand-builds a mission behavior tree
(navigate -> conditional dance A/B chosen by a Prompt+Switch -> navigate on),
uploads the GraphNav map, and plays it with the Mission service.

Usage:
    python lt6_mission.py ROBOT_IP --walk_dir "C:\\path\\to\\lt6 inspection.walk"
Credentials come from the BOSDYN_CLIENT_USERNAME / BOSDYN_CLIENT_PASSWORD env vars.

Not hardware-tested. Lines marked VERIFY use field/method names that can vary by
bosdyn version -- confirm them against your installed SDK (print the object once).
"""
import argparse
import glob
import os
import sys
import time

import bosdyn.client
import bosdyn.client.util
import bosdyn.client.lease
import bosdyn.client.estop
import bosdyn.geometry
from bosdyn.client.robot_command import RobotCommandBuilder
from bosdyn.client import math_helpers
from bosdyn.client.graph_nav import GraphNavClient
from bosdyn.mission.client import MissionClient, CompilationError

from bosdyn.api.autowalk import walks_pb2
from bosdyn.api.mission import nodes_pb2, util_pb2, mission_pb2
from bosdyn.api.graph_nav import map_pb2, graph_nav_pb2, nav_pb2

LOOP = True   # set True to wrap the whole patrol in a Repeat

# --------------------------------------------------------------------------- #
# Node helpers (a Node is the mission-tree atom; each wraps exactly one kind)
# --------------------------------------------------------------------------- #

def command_node(name, robot_command):
    """Wrap a RobotCommand payload in a BosdynRobotCommand mission node."""
    node = nodes_pb2.Node(name=name)
    node.bosdyn_robot_command.CopyFrom(nodes_pb2.BosdynRobotCommand(
        service_name='robot-command', host='localhost', command=robot_command))
    return node


def navigate_node(name, waypoint_id):
    """A BosdynNavigateTo node -- GraphNav navigation is a mission NODE, not a
    RobotCommand (RobotCommandBuilder cannot drive GraphNav)."""
    node = nodes_pb2.Node(name=name)
    node.bosdyn_navigate_to.CopyFrom(nodes_pb2.BosdynNavigateTo(
        service_name=GraphNavClient.default_service_name, host='localhost',
        destination_waypoint_id=waypoint_id))
    return node


def sleep_node(secs):
    node = nodes_pb2.Node(name=f'hold {secs}s')
    node.sleep.CopyFrom(nodes_pb2.Sleep(seconds=secs))   # Sleep.seconds is a FLOAT (not nanoseconds)
    return node


def pose_node(name, yaw=0.0, roll=0.0, pitch=0.0, height=0.0):
    """Stand with a body orientation. VERIFY the EulerZXY sign convention on the robot."""
    q = bosdyn.geometry.EulerZXY(yaw=yaw, roll=roll, pitch=pitch)
    return command_node(name, RobotCommandBuilder.synchro_stand_command(
        body_height=height, footprint_R_body=q))


def sequence_node(name, children):
    seq = nodes_pb2.Sequence()
    for child in children:
        seq.children.add().CopyFrom(child)
    node = nodes_pb2.Node(name=name)
    node.sequence.CopyFrom(seq)
    return node

def action_node(el):
    """Reissue an element's recorded body action (sit or pose) as a command node.
    BosdynNavigateTo only MOVES the robot -- it does NOT run the element's recorded
    action.
    """
    aw = el.action_wrapper
    print(el)
    if aw.HasField('robot_body_sit'):
        return command_node(f'{el.name} (sit)', RobotCommandBuilder.synchro_sit_command())
    if aw.HasField('robot_body_pose'):
        rot = aw.robot_body_pose.target_tform_body.rotation
        roll = math_helpers.Quat(w=rot.w, x=rot.x, y=rot.y, z=rot.z).to_roll() 
        pitch = math_helpers.Quat(w=rot.w, x=rot.x, y=rot.y, z=rot.z).to_pitch()  
        yaw = math_helpers.Quat(w=rot.w, x=rot.x, y=rot.y, z=rot.z).to_yaw()   
        R = bosdyn.geometry.EulerZXY(yaw=yaw, roll=roll, pitch=pitch)
        return command_node(f'{el.name} (pose)',
                            RobotCommandBuilder.synchro_stand_command(footprint_R_body=R))
    return None   # element records no body action


def edge_pose_node(graph, name, from_wp=None, to_wp=None):
    """Pull a recorded body pose off a map EDGE's body_control and issue it as a stand pose.

    The recorded crawl/pitch poses live on the GraphNav graph edges
    (Edge.Annotations.mobility_params.body_control), NOT in the Walk elements (whose
    target_tform_body is ~identity). Match the edge by its from/to waypoint, read the
    body offset (position z + rotation quaternion), convert the quaternion to EulerZXY
    the same way action_node does, and command a stand at that pose.
    """
    for e in graph.edges:
        if from_wp and e.id.from_waypoint != from_wp:
            continue
        if to_wp and e.id.to_waypoint != to_wp:
            continue
        pts = e.annotations.mobility_params.body_control.base_offset_rt_footprint.points
        if not pts:
            continue
        pose = pts[0].pose                       # SE3Pose: position (Vec3) + rotation (Quaternion)
        rot = pose.rotation
        q = math_helpers.Quat(w=rot.w, x=rot.x, y=rot.y, z=rot.z)
        R = bosdyn.geometry.EulerZXY(yaw=q.to_yaw(), roll=q.to_roll(), pitch=q.to_pitch())
        return command_node(name, RobotCommandBuilder.synchro_stand_command(
            body_height=pose.position.z, footprint_R_body=R))
    return None   # no matching edge / no recorded body offset


# --------------------------------------------------------------------------- #
# The two dances
# --------------------------------------------------------------------------- #

def build_dance_a():
    """Dance A -- custom: pitch forward, then roll left<->right three times."""
    wiggle = sequence_node('wiggle', [
        pose_node('roll left',  pitch=+0.4, roll=+0.3), sleep_node(0.1),
        pose_node('roll right', pitch=+0.4, roll=-0.3), sleep_node(0.1)
        ,pose_node('roll left',  pitch=+0.4, roll=+0.3), sleep_node(0.1)])
    rep = nodes_pb2.Repeat(max_starts=1)          # Repeat.max_starts (int32) + Repeat.child
    rep.child.CopyFrom(wiggle)
    wiggle_x3 = nodes_pb2.Node(name='wiggle x3')
    wiggle_x3.repeat.CopyFrom(rep)
    return sequence_node('Dance A (pitch + roll x3)', [
        pose_node('pitch forward', pitch=+0.3), sleep_node(0.1),
        wiggle_x3,
        pose_node('neutral')])


def build_dance_b():
    return sequence_node('Dance B (feed)', [
        pose_node('pitch forward', pitch=0.5), sleep_node(0.1),
        pose_node('neutral')])

def build_sit():
    return sequence_node('Sit (pitch -0.5)', [
        pose_node('pitch forward', pitch=-0.5), sleep_node(0.1),
        pose_node('neutral')])


# --------------------------------------------------------------------------- #
# Conditional dance: Prompt writes answer_code -> Switch (as the prompt's child)
# --------------------------------------------------------------------------- #

def build_conditional_dance(dance_a, dance_b):
    prompt = nodes_pb2.Prompt(text='Which dance?', source='dance_choice',
                              always_reprompt=True)
    prompt.options_list.options.add(text='shake (A)', answer_code=1)
    prompt.options_list.options.add(text='feed (B)',  answer_code=2)

    switch = nodes_pb2.Switch()
    # pivot_value is a Value; a blackboard lookup is `runtime_var` (name + type).
    # (NOT CopyFrom(prompt.source) -- source is just the string variable name.)
    switch.pivot_value.runtime_var.name = 'dance_choice'
    switch.pivot_value.runtime_var.type = util_pb2.VariableDeclaration.TYPE_INT
    switch.int_children[1].CopyFrom(dance_a)
    switch.int_children[2].CopyFrom(dance_b)
    # default_child must be a real node -- the compiler walks it even when unset,
    # and an empty default Node is the "Unsupported type None" compile error.
    switch.default_child.CopyFrom(pose_node('no dance chosen'))   # just stand
    switch_node = nodes_pb2.Node(name='pick dance')
    switch_node.switch.CopyFrom(switch)

    # KEY: the switch runs as the prompt's CHILD. The answer variable is scoped to
    # the prompt's subtree, so a sibling switch could not read `dance_choice`.
    prompt.child.CopyFrom(switch_node)
    prompt_node = nodes_pb2.Node(name='ask dance')
    prompt_node.prompt.CopyFrom(prompt)
    return prompt_node


# --------------------------------------------------------------------------- #
# Assemble the tree: go to start -> go to dance wp -> conditional dance -> go to end
# --------------------------------------------------------------------------- #

def dest_wp(el):
    """Destination waypoint id from an element's target.

    Recorded elements store a `navigate_route` (a list of waypoints), so the
    destination is the LAST waypoint. Only manually-placed targets use `navigate_to`.
    Using `.navigate_to.destination_waypoint_id` on a route returns '' -> the mission
    fails to compile (empty BosdynNavigateTo destination). This handles both.
    """
    t = el.target
    print(el)
    which = t.WhichOneof('target')
    if which == 'navigate_to':
        return t.navigate_to.destination_waypoint_id
    if which == 'navigate_route':
        wps = list(t.navigate_route.route.waypoint_id)   # Route.waypoint_id (repeated string)
        return wps[-1] if wps else ''
    return ''


def build_tree(elems):
    start_wp = dest_wp(elems['Start'])
    dance_wp = dest_wp(elems['twerk'])
    lower_wp = dest_wp(elems['Pose - 1'])
    normal_wp = dest_wp(elems['Pose - 2'])
    sit_wp = dest_wp(elems['Pose - 3'])
    end_wp   = dest_wp(elems['End Recording'])
    print('waypoints -> start:', repr(start_wp), '| crawl under table:', repr(lower_wp),  '| resume walking:', repr(normal_wp), '| sit:', repr(sit_wp), '| dance:', repr(dance_wp), '| end:', repr(end_wp))
    for name, wp in [('start', start_wp), ('dance', dance_wp), ('end', end_wp)]:
        if not wp:
            raise SystemExit(f'{name}_wp is empty -- print elems[...].target to check the accessor')

    dance = build_conditional_dance(build_dance_a(), build_dance_b())
    sit = build_sit()

    patrol = sequence_node('lt6 patrol mission', [
        navigate_node('go to start', start_wp),
        navigate_node('go to dance', dance_wp),
        dance,
        navigate_node('go to crawl', lower_wp),
        navigate_node('go to walk', normal_wp),
        navigate_node('go to sit', sit_wp),
        sit,
        navigate_node('go to end', end_wp)])

    root = patrol
    if LOOP:
        rep = nodes_pb2.Repeat(max_starts=3)
        rep.child.CopyFrom(root)
        root = nodes_pb2.Node(name='patrol loop')
        root.repeat.CopyFrom(rep)
    # Battery safe-stop Selector omitted: the low-battery Condition needs a verified
    # blackboard path into robot state. Add it once tested.
    return root


# --------------------------------------------------------------------------- #
# GraphNav map upload + fiducial localization
# --------------------------------------------------------------------------- #

def upload_graph_and_snapshots(robot, walk_dir):
    client = robot.ensure_client(GraphNavClient.default_service_name)
    with open(os.path.join(walk_dir, 'graph'), 'rb') as f:
        graph = map_pb2.Graph()
        graph.ParseFromString(f.read())
    client.upload_graph(graph=graph)   # VERIFY: some versions want lease=... here
    for wp in graph.waypoints:
        if not wp.snapshot_id:
            continue
        with open(os.path.join(walk_dir, 'waypoint_snapshots', wp.snapshot_id), 'rb') as f:
            snap = map_pb2.WaypointSnapshot()
            snap.ParseFromString(f.read())
        client.upload_waypoint_snapshot(waypoint_snapshot=snap)
    for edge in graph.edges:
        if not edge.snapshot_id:
            continue
        with open(os.path.join(walk_dir, 'edge_snapshots', edge.snapshot_id), 'rb') as f:
            snap = map_pb2.EdgeSnapshot()
            snap.ParseFromString(f.read())
        client.upload_edge_snapshot(edge_snapshot=snap)
    # Localize to the nearest visible fiducial -- a fiducial MUST be in view at start.
    client.set_localization(
        initial_guess_localization=nav_pb2.Localization(),
        fiducial_init=graph_nav_pb2.SetLocalizationRequest.FIDUCIAL_INIT_NEAREST)
    print(f'uploaded {len(graph.waypoints)} waypoints, {len(graph.edges)} edges; localized')


# --------------------------------------------------------------------------- #
# Console answerer for the mission's Prompt (or answer on the tablet instead)
# --------------------------------------------------------------------------- #

def answer_pending_questions(mission_client):
    for q in mission_client.get_state().questions:
        print(f'\n[mission] {q.text}')
        for opt in q.options:
            print(f'    {opt.answer_code}: {opt.text}')
        code = int(input('answer code> ').strip())
        mission_client.answer_question(q.id, code)   # VERIFY signature: (question_id, answer_code)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    bosdyn.client.util.add_base_arguments(parser)   # adds hostname + verbosity; creds from env
    parser.add_argument('--walk_dir', required=True,
                        help='autowalk directory (contains graph, missions/, *_snapshots/)')
    args = parser.parse_args()

    # Load the Walk proto from the missions/ subfolder of the autowalk directory.
    walk_files = glob.glob(os.path.join(args.walk_dir, 'missions', '*.walk'))
    if not walk_files:
         sys.exit(f'no .walk file found under {os.path.join(args.walk_dir, "missions")}')
    walk = walks_pb2.Walk()
    with open(walk_files[0], 'rb') as f:
        walk.ParseFromString(f.read())

    for i, el in enumerate(walk.elements):
        print(i, el.name, '| skipped:', el.is_skipped)

    # Pruning note: because we HAND-BUILD the nav below (explicit BosdynNavigateTo
    # nodes), is_skipped has no effect on THIS tree -- the route is defined by which
    # nav nodes we add. Skipping only matters if you CompileAutowalk the walk instead.
    drop = {'Localize - 2', 'twerk2', 'twerk3', 'Localize - 4'}   # note: 'Localize' (z)
    for el in walk.elements:
        if el.name in drop:
           el.is_skipped = True
    elems = {el.name: el for el in walk.elements}
    root = build_tree(elems)

    # ---- connect ----
    # MissionClient is NOT a standard client (it lives in bosdyn-mission), so register
    # it explicitly; GraphNav/RobotCommand/Lease/E-Stop are registered by default.
    sdk = bosdyn.client.create_standard_sdk('lt6-mission', [MissionClient])
    robot = sdk.create_robot(args.hostname)
    bosdyn.client.util.authenticate(robot)     # BOSDYN_CLIENT_USERNAME / BOSDYN_CLIENT_PASSWORD
    robot.time_sync.wait_for_sync()

    # ---- E-Stop (own endpoint) ----
    estop_client = robot.ensure_client(bosdyn.client.estop.EstopClient.default_service_name)
    estop_ep = bosdyn.client.estop.EstopEndpoint(estop_client, 'lt6-estop', estop_timeout=9.0)
    estop_ep.force_simple_setup()

    lease_client = robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)

    with bosdyn.client.estop.EstopKeepAlive(estop_ep), \
         bosdyn.client.lease.LeaseKeepAlive(lease_client, must_acquire=True, return_at_exit=True):

        robot.power_on(timeout_sec=20)
        upload_graph_and_snapshots(robot, args.walk_dir)

        mission_client = robot.ensure_client(MissionClient.default_service_name)
        try:
            mission_client.load_mission(root)      # lease supplied from the wallet/keepalive
        except CompilationError as e:
            print('COMPILE ERROR -- failed nodes:')
            for fn in e.response.failed_nodes:     # which node the compiler rejected, and why
                print(f'  node "{fn.name}" ({fn.impl_typename}): {fn.error}')
            raise
        print('mission loaded; playing (answer the dance prompt below or on the tablet)')

        # Play + monitor. play_mission sets a pause time slightly in the future; we
        # re-call it as a keepalive until the mission reaches a terminal status.
        terminal = {mission_pb2.State.STATUS_SUCCESS,
                    mission_pb2.State.STATUS_FAILURE,
                    mission_pb2.State.STATUS_ERROR,
                    mission_pb2.State.STATUS_STOPPED}
        while True:
            mission_client.play_mission(int(time.time()) + 5)   # VERIFY play_mission signature
            time.sleep(0.3)
            answer_pending_questions(mission_client)
            status = mission_client.get_state().status
            if status in terminal:
                print('mission finished with status:', mission_pb2.State.Status.Name(status))
                break

        robot.power_off(cut_immediately=False)


if __name__ == '__main__':
    main()
