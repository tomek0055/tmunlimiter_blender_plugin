from ..object_texture.object_texture_props import (
    TMUnlimiterObjectTextureProps,
    __register__ as object_texture_props_register,
    __unregister__ as object_texture_props_unregister,
)
from ..object_texture.texture_props import TMUnlimiterTextureProps
from ..blender_gbx import GbxArchive
import bpy

class TMUnlimiterObjectSettings( bpy.types.PropertyGroup ) :

    can_export_object_name: bpy.props.BoolProperty(
        name = "Export object name",
        default = False,
        description = "This option controls whenever the object name is saved to the file during export",
    )

    can_export_geometry: bpy.props.BoolProperty(
        name = "Export geometry",
        default = True,
        description = "This option controls export of the geometry data and textures",
    )

    can_export_collision: bpy.props.BoolProperty(
        name = "Export collision",
        default = False,
        description = "This option controls export of the collision data",
    )

    exclude_from_export: bpy.props.BoolProperty(
        name = "Exclude from export",
        default = False,
        description = "This option excludes an object from being saved during export"
    )

    is_visual_mip: bpy.props.BoolProperty(
        name = "Is LOD container",
        default = False,
        description = "This option represents an object as a Level of Detail container during export",
    )

    visual_mip_distance: bpy.props.FloatProperty(
        min = 0,
        name = "LOD distance",
        default = 0,
        description = "This option controls the distance at which an object is displayed",
    )

    texture_props: bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureProps,
    )

    show_full_path: bpy.props.BoolProperty(
        name = "Show full path",
        default = False,
        options = { "SKIP_SAVE" },
        description = "This option toggle visibility of the texture path",
    )

    def archive_material( self, gbx: GbxArchive ) :
        if self.texture_props.texture_type == "Game" :
            self.texture_props.texture_game.archive( gbx )
        elif self.texture_props.texture_type == "Custom" :
            self.texture_props.texture_custom.archive( gbx )
        else :
            gbx.nat32( 0xffffffff )

class TMUnlimiter_ApplyObjectSettingsToSelectedObjects( bpy.types.Operator ) :
    bl_label = ""
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

class TMUnlimiterObjectSettingsPanel( bpy.types.Panel ) :
    bl_idname = "UNLIMITER_PT_object_settings"
    bl_label = "TMUnlimiter - Object settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw_model_ui( self, object_settings: TMUnlimiterObjectSettings ) :
        texture_props = object_settings.texture_props
        self.layout.prop( texture_props, "texture_type" )

        if texture_props.texture_type == "Custom" :
            texture_custom = texture_props.texture_custom

            layout_root = self.layout.box()
            layout_root.prop( texture_custom, "is_double_sided" )

            layout_root.separator()

            def draw_texture_layout( layout, texture: TMUnlimiterTextureProps ) :
                texture_type = texture.get_texture_type()

                layout.prop( texture, "filepath", text = "{0} file path".format( texture_type ) )
                layout.prop( texture, "filtering", text = "{0} filtering".format( texture_type ) )
                layout.prop( texture, "addressing", text = "{0} addressing".format( texture_type ) )

            layout_root.prop( texture_custom, "use_diffuse" )

            if texture_props.texture_custom.use_diffuse:
                draw_texture_layout( layout_root.box(), texture_custom.diffuse )

            layout_root.prop( texture_custom, "use_specular" )

            if texture_props.texture_custom.use_specular:
                draw_texture_layout( layout_root.box(), texture_custom.specular )

            layout_root.prop( texture_custom, "use_normal" )

            if texture_props.texture_custom.use_normal:
                draw_texture_layout( layout_root.box(), texture_custom.normal )

            layout_root.prop( texture_custom, "use_lighting" )

            if texture_props.texture_custom.use_lighting:
                draw_texture_layout( layout_root.box(), texture_custom.lighting )

            layout_root.prop( texture_custom, "use_occlusion" )

            if texture_props.texture_custom.use_occlusion:
                draw_texture_layout( layout_root.box(), texture_custom.occlusion )

            layout_root.prop( texture_custom, "override_cube_ambient" )

            if texture_props.texture_custom.override_cube_ambient:
                draw_texture_layout( layout_root.box(), texture_custom.cube_ambient )

            layout_root.prop( texture_custom, "override_reflect_soft" )

            if texture_props.texture_custom.override_reflect_soft:
                draw_texture_layout( layout_root.box(), texture_custom.reflect_soft )

            layout_root.prop( texture_custom, "override_fresnel" )

            if texture_props.texture_custom.override_fresnel:
                draw_texture_layout( layout_root.box(), texture_custom.fresnel )

            layout_root.prop( texture_custom, "override_clouds" )

            if texture_props.texture_custom.override_clouds:
                draw_texture_layout( layout_root.box(), texture_custom.clouds )

        elif texture_props.texture_type == "Game" :
            layout = self.layout.box()

            layout.prop( texture_props.texture_game, "environment" )
            layout.prop( texture_props.texture_game, "game_material" )

            result, selected_environment_material = texture_props.texture_game.get_selected_environment_material()

            if not result :
                return

            _, material_uv_layers = selected_environment_material

            layout = self.layout.box()

            row = layout.row()
            row.alignment = "CENTER"

            if len( material_uv_layers ) == 0 :
                row.label( text = "This material does not use any UV layer" )
            else :
                row.label( text = f'This material use { len( material_uv_layers ) } UV { "layers" if len( material_uv_layers ) > 1 else "layer" }' )

                row = row.row()
                row.alignment = "CENTER"
                row.prop( object_settings, "show_full_path" )

                for uv_layer_index, uv_layer_textures in enumerate( material_uv_layers ) :
                    row = layout.row()
                    row.scale_y = 0.5

                    if uv_layer_index == 0 :
                        uv_layer_label = "1st"
                    elif uv_layer_index == 1 :
                        uv_layer_label = "2nd"
                    elif uv_layer_index == 2 :
                        uv_layer_label = "3rd"
                    else :
                        uv_layer_label = f"{ 1 + uv_layer_index }th"

                    row.label( text = f'{ uv_layer_label } UV layer:' )

                    for texture_purpose, texture_filepath in uv_layer_textures :
                        if object_settings.show_full_path :
                            texture_filepath = list( texture_filepath )
                            texture_filepath.reverse()
                            texture_filepath = "\\".join( texture_filepath )
                        else :
                            texture_filepath = texture_filepath[ 0 ]

                        row = layout.row()
                        row.scale_y = 0.6
                        row.label( text = f'{ " " * 8 }{ texture_purpose } - { texture_filepath }' )

                    layout.separator()

    @classmethod
    def poll( self, context: bpy.context ) :
        return context.active_object.type in { "MESH", "EMPTY", "LIGHT" }

    def draw( self, context: bpy.context ) :
        object = context.active_object
        object_settings: TMUnlimiterObjectSettings = object.unlimiter_object_settings

        self.layout.prop( object_settings, "exclude_from_export" )

        if object_settings.exclude_from_export :
            return

        if object.type == "EMPTY" :
            self.layout.prop( object_settings, "is_visual_mip" )

        if object.parent and object.parent.unlimiter_object_settings.is_visual_mip :
            self.layout.prop( object_settings, "visual_mip_distance" )

        self.layout.prop( object_settings, "can_export_object_name" )

        if object.type == "MESH" :
            self.layout.prop( object_settings, "can_export_geometry" )
            self.layout.prop( object_settings, "can_export_collision" )

            if object_settings.can_export_geometry :
                self.draw_model_ui( object_settings )

        box = self.layout.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label( text = "Apply object settings to other selected objects" )
        box.operator( TMUnlimiter_ApplyObjectSettingsToSelectedObjects.bl_idname, text = "Apply geometry settings", icon = "COPYDOWN" ).apply_collision = False
        box.operator( TMUnlimiter_ApplyObjectSettingsToSelectedObjects.bl_idname, text = "Apply geometry and collision settings", icon = "COPYDOWN" ).apply_collision = True

def __register__() :
    object_texture_props_register()

    bpy.utils.register_class( TMUnlimiterObjectSettings )
    bpy.utils.register_class( TMUnlimiter_ApplyObjectSettingsToSelectedObjects )
    bpy.utils.register_class( TMUnlimiterObjectSettingsPanel )

    bpy.types.Object.unlimiter_object_settings = bpy.props.PointerProperty(
        type = TMUnlimiterObjectSettings
    )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiterObjectSettingsPanel )
    bpy.utils.unregister_class( TMUnlimiter_ApplyObjectSettingsToSelectedObjects )
    bpy.utils.unregister_class( TMUnlimiterObjectSettings )

    object_texture_props_unregister()