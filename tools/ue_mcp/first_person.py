"""Player = first person (Owen 2026-10-21): BP_ThirdPersonCharacter camera boom length 0 at eye height (+70 cm over the
capsule centre), view follows the mouse, body turns with the view, own mesh hidden from the player's camera."""
from bpkit import compile_save
from ue import call

P = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
print(call("init_unreal.KeeperPyTools", "run_python", code="""
import unreal
C = '/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C'
boom = unreal.find_object(None, C + ':SpringArmComponent_0__A9892D03')
cam = unreal.find_object(None, C + ':CameraComponent_0__CCE3C0B4')
boom.set_editor_property('target_arm_length', 0.0)
boom.set_editor_property('relative_location', unreal.Vector(10, 0, 70))
boom.set_editor_property('socket_offset', unreal.Vector(0, 0, 0))
boom.set_editor_property('target_offset', unreal.Vector(0, 0, 0))
boom.set_editor_property('use_pawn_control_rotation', True)
boom.set_editor_property('do_collision_test', False)
boom.set_editor_property('enable_camera_lag', False)
boom.set_editor_property('enable_camera_rotation_lag', False)
cam.set_editor_property('use_pawn_control_rotation', False)
cdo = unreal.get_default_object(unreal.load_class(None, C))
cdo.set_editor_property('use_controller_rotation_yaw', True)
cdo.character_movement.set_editor_property('orient_rotation_to_movement', False)
cdo.mesh.set_editor_property('owner_no_see', True)
unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset('""" + P + """'))
print('first person set')
"""))
print("saved:", compile_save(P))
