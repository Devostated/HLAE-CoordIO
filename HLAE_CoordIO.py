bl_info = {
    "name": "HLAE CoordIO",
    "author": "Devostated.",
    "version": (2, 0, 0),
    "blender": (2, 93, 0),
    "operator": "Import-Export",
    "location": "Operator Search",
    "category": "Import-Export",
    "tracker_url": "https://github.com/Devostated/HLAE-CoordIO/issues",
    "description": "Exporting transformation data to After Effects."
}
import bpy
import bmesh
from bpy.types import Panel, Operator, PropertyGroup, Scene
from math import degrees, radians

class COORD_PT_Panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HLAE CoordIO"
    bl_label = "HLAE CoordIO"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        bl2ae_settings = scene.bl2ae_settings

        layout.column(align=True).label(text='Set Coordinate System:')
        layout.prop(bl2ae_settings, 'coord_sys', expand = True)
        layout.operator('bl.plane')
        layout.operator('bl.coords')

class bl2ae_properties(PropertyGroup):
    coord_sys: bpy.props.EnumProperty(
        name = "Set Coordinate System",
        items = (
                ('CSGO','CSGO','Set to CSGOs coordinate system.'),
                ('BLENDER','Blender','Set to Blenders coordinate system.')
        )
    )

class bl2ae_plane(Operator):
    bl_idname = 'bl.plane'
    bl_label = "Create Solid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Decent size for Blender and AE
        scene = context.scene
        width = scene.render.resolution_x
        height = scene.render.resolution_y
        aspect = width / height

        if scene.bl2ae_settings.coord_sys == 'BLENDER':
            Z = 0
            Y = 0.225
            X = Y * aspect
            name = "Blender Solid"
        else:
            Z = 0.225
            Y = Z * aspect
            X = 0
            name = "CSGO Solid"
        verts = [
                (-X,  Y, -Z),
                (-X, -Y, -Z),
                ( X, -Y,  Z),
                ( X,  Y,  Z)
                ]
        mesh = bpy.data.meshes.new(name)
        solid = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(solid)

        bm = bmesh.new()
        for v in reversed(verts):
            bm.verts.new(v)
        bm.faces.new(bm.verts)
        bm.to_mesh(mesh)
        bm.free()

        context.view_layer.objects.active = solid
        if scene.bl2ae_settings.coord_sys == 'BLENDER':
            context.object.rotation_euler[0] = radians(90)
        return {'FINISHED'}

class bl2ae_coords(Operator):
    bl_idname = 'bl.coords'
    bl_label = "Copy to Clipboard"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Transformation Blender to AE
        trans = context.object
        loc = trans.location
        scl = 4.165
        if context.scene.bl2ae_settings.coord_sys == 'BLENDER':
            # Location Blender coords to AE
            LX =  loc.x * 100
            LY = -loc.z * 100
            LZ =  loc.y * 100

            # Rotation Blender coords to AE
            rot = list(trans.matrix_world.to_euler('ZYX'))
            RX =  degrees(rot[0]) - 90
            RY = -degrees(rot[1])
            RZ = -degrees(rot[2])

            # Scale Blender coords to AE
            SX = scl * trans.scale[0]
            SY = scl * trans.scale[1]
            SZ = scl * trans.scale[2]
        else:
            # Location CSGO coords to AE
            LX = -loc.y * 100
            LY = -loc.z * 100
            LZ =  loc.x * 100

            # Rotation CSGO coords to AE
            rot = list(trans.matrix_world.to_euler('XZY'))
            RX = -degrees(rot[1])
            RY = -degrees(rot[2])
            RZ =  degrees(rot[0])

            # Scale CSGO coords to AE
            SX = scl * trans.scale[1]
            SY = scl * trans.scale[2]
            SZ = scl * trans.scale[0]

        # Copy to Clipboard
        context.window_manager.clipboard = (
            "Adobe After Effects 8.0 Keyframe Data\r\n"
            "Transform\tPosition\r"
            "\tFrame\tX pixels\tY pixels\tZ pixels\t\r"
            f"\t\t{LX}\t{LY}\t{LZ}\t\r\n"
            "Transform\tOrientation\r"
            "\tFrame\tX degrees\t\r"
            f"\t\t{RX}\t{RY}\t{RZ}\t\r\n"
            "Transform\tScale\r"
            "\tFrame\tX percent\tY percent\tZ percent\t\r"
            f"\t\t{SX}\t{SY}\t{SZ}\t\r"
            "\r\n"
            "End of Keyframe Data"
        )
        return {'FINISHED'}

addon_keymaps = []
classes = [
    COORD_PT_Panel,
    bl2ae_properties,
    bl2ae_plane,
    bl2ae_coords,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    Scene.bl2ae_settings = bpy.props.PointerProperty(type= bl2ae_properties)

    # Hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new("bl.coords", type= 'F', value= 'PRESS', shift= True)
        addon_keymaps.append((km, kmi))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del Scene.bl2ae_settings

    # Hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
