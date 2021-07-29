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


bl_info = {
    "name": "HevMap",
    "author": "David 'Hevedy' Palacios",
    "description": "Export Blender as map to Unreal Engine HevMap. Check for updates @Hevedy",
    "blender": (2, 90, 0),
    "version": (0, 2),
	"wiki_url":    "https://github.com/Hevedy/HevMap",
    "tracker_url": "https://github.com/Hevedy/HevMap/issues",
	"category": "Import-Export"
}

if 'bpy' not in locals():
    import bpy
    from bpy.props import EnumProperty, BoolProperty, FloatProperty, StringProperty
    from . import HevMap_Utils
else:
    from importlib import reload
    reload(HevMap_Utils)


class HevMap_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    UEDir : StringProperty(
        name="UE4 Folder",
        description="Unreal Engine 4 folder",
        default="",
		subtype="DIR_PATH"
    )
    
    TBDir : StringProperty(
        name="TrenchBroom Folder",
        description="TrenchBroom folder name",
        default="",
        subtype="DIR_PATH"
    )
    
    TBFile : StringProperty(
        name="TrenchBroom File",
        description="TrenchBroom file name",
        default="",
        subtype="FILE_PATH"
    )
    
    TBFileAuto : BoolProperty(
        name="TrenchBroom Auto Export",
        description="TrenchBroom file auto export",
        default=False
    )
    
    MapName : StringProperty(
        name="Map Name",
        description="Map Target Name",
        default="CustomMap",
        subtype="FILE_NAME"
    )
    
    MapPath : StringProperty(
        name="Map Path",
        description="Map Target Path",
        default="",
        subtype="DIR_PATH"
    )

    def draw(self, context):
        layout = self.layout
        box=layout.box()
        box.prop(self, 'UEDir')
        box.prop(self, 'TBDir')


class HevMap_Panel(bpy.types.Panel):
    """HevMap Side Panel"""
    bl_idname = "PANEL_PT_HevMap_Side_Panel"
    bl_label = "HevMap"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = 'HevMap'
    bl_context = "output"

    #@classmethod
    #def poll(cls, context):
    #    return (context.scene is not None)

    def draw(self, context):
        addon_prefs = prefs()

        col = self.layout.column(align=True)
        col.label(text="UE Export Settings:")
        
        layout = self.layout
        
        layout.prop(addon_prefs, 'MapName', text="Name")
        layout.prop(addon_prefs, 'MapPath', text="Path")
        row = layout.row()
        row.operator(ExportToUE.bl_idname,text="Export to UE",icon="EXPORT")

        col = self.layout.column(align=True)
        col.label(text="TrenchBroom Settings:")
        
        layout = self.layout
        layout.prop(addon_prefs, 'TBFileAuto', text="Auto Export")
        layout.prop(addon_prefs, 'TBFile', text="File")
        
        row = layout.row()
        row.operator(TBToBlender.bl_idname,text="Import to Blender",icon="IMPORT")

        col = self.layout.column(align=True)
        #row2 = self.layout.column(align=True)
        row2 = layout.row()
        row2.label(text="HevMap by @Hevedy")
        row2.enabled = False
        #row2.label(text="By @Hevedy")


class TBToBlender(bpy.types.Operator):

    bl_idname = "hevmap.tbimport"
    bl_label = "TrenchBroom to Blender"
    bl_description = "Import TrenchBroom to Blender"

    def execute(self, context):
        global _preferences
        
        #bpy.ops.wm.save_mainfile()
        
        valid = HevMap_Utils.TrenchBroomToBlender()
        
        if valid:
            self.report({'INFO'}, "TrenchBroom Import Complete")
        else:
            self.report({'ERROR'}, "TrenchBroom Import Error")
        
        addon_prefs = prefs()
        if addon_prefs.TBFileAuto and valid:
            validExp = HevMap_Utils.ExportFiles()
            if validExp:
                self.report({'INFO'}, "TrenchBroom to UE Export Complete")
            else:
                self.report({'ERROR'}, "TrenchBroom to UE Export Error")
        
        return{'FINISHED'} 

class ExportToUE(bpy.types.Operator):

    bl_idname = "hevmap.exporttoue"
    bl_label = "Export To UE"
    bl_description = "Export to UE"

    def execute(self, context):
        global _preferences
        
        bpy.ops.wm.save_mainfile()
            
        valid = HevMap_Utils.ExportFiles()
            
        if valid:
            self.report({'INFO'}, "Unreal Engine Export Complete")
        else:
            self.report({'ERROR'}, "Unreal Engine Export Error")
            
        return{'FINISHED'} 

class DialogOperator(bpy.types.Operator):
    bl_idname = "object.dialog_operator"
    bl_label = "Simple Dialog Operator"

    my_float: bpy.props.FloatProperty(name="Some Floating Point")
    my_bool: bpy.props.BoolProperty(name="Toggle Option")
    my_string: bpy.props.StringProperty(name="String Value")

    def execute(self, context):
        message = (
            "Popup Values: %f, %d, '%s'" %
            (self.my_float, self.my_bool, self.my_string)
        )
        self.report({'INFO'}, message)
        return {'FINISHED'}

def prefs():
    return bpy.context.preferences.addons[__name__].preferences

classes = (
    HevMap_Preferences,
    DialogOperator,
    TBToBlender,
    ExportToUE,
	HevMap_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
