##############################################################
#
#	Blender HevArch, 
#	<HevArch, Blender addon for exporting maps to Unreal Engine.>
#	Copyright (C) <2020-2021> <David Palacios (Hevedy)>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################

import bpy, math
from subprocess import Popen
from os import system, path, makedirs, sep
from distutils import dir_util
from pathlib import Path as pathlib_path

_preferences={}

_enums={}


def GetBlenderFileName():
    return bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend','')

def ValidatePath(_Path):
    if not path.exists(_Path):
        makedirs(_Path)
        
def ResetBlenderScene():
    bpy.ops.wm.read_factory_settings()

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.lamps,
            bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)


def RemoveScene(_NewMethod):
    if _NewMethod:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    else:
        ResetBlenderScene()


def TrenchBroomToBlender():
    module_name = __name__.split('.')[0]
    addon_prefs = bpy.context.preferences.addons[module_name].preferences
    
    iFile = addon_prefs.TBFile
    
    if not path.exists(iFile):
        print('Invalid TrenchBroom File')
        return False
    
    # Reset whole scene
    RemoveScene(True)
    
    #Import the scene
    bpy.ops.import_scene.obj(filepath=iFile, filter_glob='*.obj;*.mtl', use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=False, 
    use_groups_as_vgroups=False, use_image_search=False, split_mode='ON', global_clamp_size=0.0, axis_forward='-Z', axis_up='Y')
    
    # TrenchBroom edit imported scene
    tApplyScale=True #Apply scales
    tScale=0.0125 #Trenchbroom scale 0.0125 # 0.015625

    # Editing
    mDistance=0.001 #Default 0.0001

    # Select all meshes
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')

    if(tApplyScale):
        # Scale meshes
        bpy.ops.transform.resize(value=(tScale, tScale, tScale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', 
        mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        # Apply scale to meshes
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Set objects and then get meshes from them
    objects = bpy.context.selected_objects
    meshes = set(o.data for o in objects)

    # Edit individual meshes using bmesh
    bm = bmesh.new()
    for m in meshes:
        bm.from_mesh(m)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=mDistance)
        bm.to_mesh(m)
        #Todo clear inside faces
        m.update()
        bm.clear()
        
    bm.free()
    
    return True
    

def ExportFiles():
    module_name = __name__.split('.')[0]
    addon_prefs = bpy.context.preferences.addons[module_name].preferences
    
    if addon_prefs.MapName == "":
        addon_prefs.MapName = "MyMap"
        
    if addon_prefs.MapPath == "":
        addon_prefs.MapPath = bpy.path.abspath("//")
    
    customName = addon_prefs.MapName
    filePath = addon_prefs.MapPath
    fileName = filePath + customName + ".hmd"

    ValidatePath(filePath)
    
    # Level Data File
    
    bpy.ops.export_scene.fbx(filepath=fileName, use_selection=False, check_existing=False, axis_forward='Y', axis_up='Z', filter_glob="*.fbx", 
    global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', 
    use_mesh_edges=False, use_tspace=True, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y', secondary_bone_axis='X', 
    use_armature_deform_only=False, bake_anim=False, bake_anim_use_all_bones=False, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, 
    bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
    
    fileName = filePath + customName + ".hmi"
    
    # Level Structure File
    File = open(fileName, "w")
    localLine = "# File HevMapInfo Generated with HevMap by Hevedy" + "\n"
    File.write(localLine)
    localLine = "# Please don't edit" + "\n" + "# " + "\n" + "\n"
    File.write(localLine)

    for coll in bpy.data.collections:
        if not coll.hide_render:
            for obj in coll.all_objects:
                if obj.type == 'MESH':
                    localLine = "Mesh//" + obj.name + "//"
                    localLine += str(int(obj.location.x)) + "," + str(int(obj.location.y)) + "," + str(int(obj.location.z))+"//"
                    matIndex = 0
                    for mat in obj.material_slots:
                        if matIndex == 0:
                            localLine += mat.material.name
                        else:
                            localLine += "," + mat.material.name
                        matIndex += 1
                        
                    if matIndex == 0:
                        localLine += "None"
                        
                    localLine += "\n"
                elif obj.type == 'LIGHT':
                    localLine = "Light//" + obj.name + "//"
                    localLine += str(int(obj.location.x)) + "," + str(int(obj.location.y)) + "," + str(int(obj.location.z))+"//"
                    if obj.data.type == 'SUN':
                        localLine += "DirectionalLight"
                    elif obj.data.type == 'SPOT':
                        localLine += "SpotLight"
                    elif obj.data.type == 'POINT':
                        localLine += "PointLight"
                    elif obj.data.type == 'AREA':
                        localLine += "AreaLight"
                    localLine += "//"
                    localLine += str(float(obj.data.color.r)) + "," + str(float(obj.data.color.g)) + "," + str(float(obj.data.color.b))
                    localLine += "\n"
                else:
                    localLine += ""
                File.write(localLine)
                
    File.close()
    
    return True


classes = (
    TrenchBroomToBlender,
    ExportFiles,
)

def register():

    for cls in classes:
        register_class(cls)

def unregister():

    for cls in reversed(classes):
        unregister_class(cls)

