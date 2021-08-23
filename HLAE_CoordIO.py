bl_info = {
    "name": "HLAE CoordIO",
    "author": "Devostated.",
    "version": (1, 1, 0),
    "blender": (2, 93, 0),
    "operator": "Import-Export",
    "location": "Operator Search",
    "category": "Import-Export",
    "tracker_url": "https://github.com/Devostated/HLAE-CoordIO/issues",
    "description": "Exporting transformation data to After Effects."
}
import bpy, os

class bl2ae_plane(bpy.types.Operator):
    bl_idname = 'bl.plane'
    bl_label = "Create Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', rotation=(1.5708, 0, 0))
        return {'FINISHED'}

class bl2ae_coords(bpy.types.Operator):
    bl_idname = 'bl.coords'
    bl_label = "Copy to Clipboard"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        X = bpy.context.object.location.y * - 1 * 100
        Y = bpy.context.object.location.z * - 1 * 100
        Z = bpy.context.object.location.x * 100

        copy = bpy.context.window_manager
        copy.clipboard = "Adobe After Effects 8.0 Keyframe Data"
        copy.clipboard = copy.clipboard + "\r\n"
        copy.clipboard = copy.clipboard + "Transform\tPosition\r\n"
        copy.clipboard = copy.clipboard + "\tFrame\tX pixels\tY pixels\tZ pixels\t\r\n"
        copy.clipboard = copy.clipboard + "\t\t{}\t{}\t{}\t".format(X, Y, Z,)
        copy.clipboard = copy.clipboard + "\r\n"
        copy.clipboard = copy.clipboard + "\r\n"
        copy.clipboard = copy.clipboard + "End of Keyframe Data"
        return {'FINISHED'}

class coordPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HLAE CoordIO"
    bl_label = "HLAE CoordIO"

    def draw(self, context):
        self.layout.operator('bl.plane')
        self.layout.operator('bl.coords')

addon_keymaps = []

def register():
    bpy.utils.register_class(bl2ae_plane)
    bpy.utils.register_class(bl2ae_coords)
    bpy.utils.register_class(coordPanel)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new("bl.coords", type= 'F', value= 'PRESS', shift= True)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.register_class(bl2ae_plane)
    bpy.utils.unregister_class(bl2ae_coords)
    bpy.utils.unregister_class(coordPanel)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()