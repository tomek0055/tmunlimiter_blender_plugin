from .prop_object_settings import TMUnlimiterObjectSettings
import bpy

class TMUnlimiter_ApplyObjectSettingsToSelectedObjects( bpy.types.Operator ) :
    bl_label = "Apply object settings to selected objects"
    bl_idname = "scene.tmunlimiter_apply_object_settings_to_selected_objects"
    bl_options = { "REGISTER", "UNDO" }
    bl_description = "Apply object settings from last selected object to other selected objects"

    apply_geometry: bpy.props.BoolProperty(
        name = "Apply geometry settings",
        default = True,
    )

    apply_collision: bpy.props.BoolProperty(
        name = "Apply collision settings",
        default = False,
    )

    @classmethod
    def poll( self, context: bpy.context ) :
        return context.active_object and len( context.selected_objects ) > 1

    def execute( self, context: bpy.context ) :
        if not self.apply_geometry and not self.apply_collision :
            return { "CANCELLED" }

        active_object = context.active_object

        if not active_object :
            return { "CANCELLED" }

        selected_objects = list( filter( lambda object: object.type != "MESH" or object != active_object, context.selected_objects ) )

        if len( selected_objects ) < 1 :
            return { "CANCELLED" }

        active_object_settings: TMUnlimiterObjectSettings = active_object.unlimiter_object_settings

        for selected_object in selected_objects :
            selected_object_settings: TMUnlimiterObjectSettings = selected_object.unlimiter_object_settings

            if self.apply_geometry :
                selected_object_settings.can_export_geometry = active_object_settings.can_export_geometry
                selected_object_settings.texture_props.copy_from( active_object_settings.texture_props )

            if self.apply_collision :
                selected_object_settings.can_export_collision = active_object_settings.can_export_collision

        return { "FINISHED" }

class TMUnlimiter_OperatorsMenu( bpy.types.Menu ) :
    bl_label = "TMUnlimiter"
    bl_idname = "VIEW3D_MT_tmunlimiter_operators"

    def draw( self, context: bpy.context ) :
        self.layout.operator( TMUnlimiter_ApplyObjectSettingsToSelectedObjects.bl_idname )

def _add_operator( self, context: bpy.context ) :
    if context.mode == "OBJECT" :
        self.layout.menu( TMUnlimiter_OperatorsMenu.bl_idname )

def __register__() :
    bpy.utils.register_class( TMUnlimiter_OperatorsMenu )
    bpy.utils.register_class( TMUnlimiter_ApplyObjectSettingsToSelectedObjects )

    bpy.types.VIEW3D_MT_editor_menus.append( _add_operator )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiter_ApplyObjectSettingsToSelectedObjects )
    bpy.utils.unregister_class( TMUnlimiter_OperatorsMenu )

    bpy.types.VIEW3D_MT_editor_menus.remove( _add_operator )