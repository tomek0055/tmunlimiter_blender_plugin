from bpy_extras.io_utils import ExportHelper
from traceback import print_exception
from ..blender_gbx import GbxArchive

from ..block_definition import TMUnlimiter_BlockDefinition
from ..variants import TMUnlimiter_Variants
from ..variation import TMUnlimiter_Variation
from ..block_unit import TMUnlimiter_BlockUnit

import bpy

def get_selected_block_definition( context: bpy.context ) -> TMUnlimiter_BlockDefinition :
    block_definitions = context.scene.tmunlimiter_block_definitions

    if context.scene.tmunlimiter_selected_block_definition_index < len( block_definitions ) :
        return block_definitions[ context.scene.tmunlimiter_selected_block_definition_index ]

    return None

class TMUnlimiter_VariationItem( bpy.types.UIList ) :
    bl_idname = "TMUNLIMITER_UL_VariationItem"

    def draw_item( self, __context__: bpy.types.Context, layout: bpy.types.UILayout, __data__, variation: TMUnlimiter_Variation, __icon__, __active_data__, __active_propname__, index: int ) :
        layout.label( text = f"Variation #{ 1 + index }: { variation.name }" )

class TMUnlimiter_BlockUnitItem( bpy.types.UIList ) :
    bl_idname = "TMUNLIMITER_UL_BlockUnitItem"
    last_item_failed_validation = False

    def draw_item( self, __context__: bpy.types.Context, layout: bpy.types.UILayout, block_definition: TMUnlimiter_BlockDefinition, block_unit: TMUnlimiter_BlockUnit, __icon__, __active_data__, __active_propname__, index: int ) :
        if not index :
            TMUnlimiter_BlockUnitItem.last_item_failed_validation = False

        validation_result, validation_message = block_unit.validate()

        if validation_result :
            offset = block_unit.calculate_offset()

        if validation_result and index > 0 and not TMUnlimiter_BlockUnitItem.last_item_failed_validation :
            block_units = block_definition.get_selected_block_units()
            back_index = index

            while back_index :
                back_index = back_index - 1
                back_block_unit = block_units[ back_index ]
                back_offset = back_block_unit.calculate_offset()

                if offset == back_offset :
                    validation_result = False
                    validation_message = f"Block Unit #{ 1 + back_index } has the same coordinates"

                    break

        if not validation_result :
            TMUnlimiter_BlockUnitItem.last_item_failed_validation = True

        layout.alert = TMUnlimiter_BlockUnitItem.last_item_failed_validation or not validation_result

        if not validation_result :
            layout.label( text = f"Block Unit #{ 1 + index } ({ validation_message })", icon = "MATCUBE" )
        elif TMUnlimiter_BlockUnitItem.last_item_failed_validation :
            layout.label( text = f"Block Unit #{ 1 + index } (Please solve problem with block unit above)", icon = "MATCUBE" )
        else :
            layout.label( text = f"Block Unit #{ 1 + index } at { '{' } { offset[ 0 ] }, { offset[ 1 ] }, { offset[ 2 ] } { '}' }", icon = "MATCUBE" )

class TMUnlimiter_AddBlockDefinition( bpy.types.Operator ) :
    bl_label = "Add block definition"
    bl_idname = "scene.tmunlimiter_add_block_definition"

    def execute( self, context: bpy.context ) :
        context.scene.tmunlimiter_block_definitions.add()
        context.scene.tmunlimiter_selected_block_definition_index = len( context.scene.tmunlimiter_block_definitions ) - 1

        return { "FINISHED" }

class TMUnlimiter_RemoveBlockDefinition( bpy.types.Operator ) :
    bl_label = "Remove selected block definition"
    bl_idname = "scene.tmunlimiter_remove_block_definition"

    def execute( self, context: bpy.context ) :
        context.scene.tmunlimiter_block_definitions.remove( context.scene.tmunlimiter_selected_block_definition_index )

        if context.scene.tmunlimiter_selected_block_definition_index > 0 :
            context.scene.tmunlimiter_selected_block_definition_index = context.scene.tmunlimiter_selected_block_definition_index - 1

        return { "FINISHED" }

class TMUnlimiter_MoveBlockDefinitionUpwards( bpy.types.Operator ) :
    bl_label = "Move block definition upwards"
    bl_idname = "scene.tmunlimiter_move_block_definition_upwards"

    def execute( self, context: bpy.context ) :
        if context.scene.tmunlimiter_selected_block_definition_index - 1 < 0 :
            return { "CANCELLED" }

        context.scene.tmunlimiter_block_definitions.move \
        (
            context.scene.tmunlimiter_selected_block_definition_index,
            context.scene.tmunlimiter_selected_block_definition_index - 1
        )

        context.scene.tmunlimiter_selected_block_definition_index = context.scene.tmunlimiter_selected_block_definition_index - 1
        return { "FINISHED" }

class TMUnlimiter_MoveBlockDefinitionDownwards( bpy.types.Operator ) :
    bl_label = "Move selected block definition"
    bl_idname = "scene.tmunlimiter_move_block_definition_downwards"

    def execute( self, context: bpy.context ) :
        if context.scene.tmunlimiter_selected_block_definition_index + 1 >= len( context.scene.tmunlimiter_block_definitions ) :
            return { "CANCELLED" }

        context.scene.tmunlimiter_block_definitions.move \
        (
            context.scene.tmunlimiter_selected_block_definition_index,
            context.scene.tmunlimiter_selected_block_definition_index + 1
        )

        context.scene.tmunlimiter_selected_block_definition_index = context.scene.tmunlimiter_selected_block_definition_index + 1
        return { "FINISHED" }

class TMUnlimiter_CopyBlockDefinition( bpy.types.Operator ) :
    bl_label = "Copy selected block definition"
    bl_idname = "scene.tmunlimiter_copy_block_definition"

    def execute( self, context: bpy.context ) :
        if context.scene.tmunlimiter_selected_block_definition_index >= len( context.scene.tmunlimiter_block_definitions ) :
            return { "CANCELLED" }

        old_block_definition = context.scene.tmunlimiter_block_definitions[ context.scene.tmunlimiter_selected_block_definition_index ]
        new_block_definition = context.scene.tmunlimiter_block_definitions.add()

        new_block_definition.identifier = old_block_definition.identifier
        new_block_definition.author = old_block_definition.author
        new_block_definition.block_type = old_block_definition.block_type
        new_block_definition.waypoint_type = old_block_definition.waypoint_type
        new_block_definition.selected_variant = old_block_definition.selected_variant
        new_block_definition.selected_variant_type = old_block_definition.selected_variant_type
        new_block_definition.variants_classic_default.copy_from( old_block_definition.variants_classic_default )
        new_block_definition.variants_road_piece.copy_from( old_block_definition.variants_road_piece )
        new_block_definition.variants_road_deadend.copy_from( old_block_definition.variants_road_deadend )
        new_block_definition.variants_road_turn.copy_from( old_block_definition.variants_road_turn )
        new_block_definition.variants_road_straight.copy_from( old_block_definition.variants_road_straight )
        new_block_definition.variants_road_t_junction.copy_from( old_block_definition.variants_road_t_junction )
        new_block_definition.variants_road_cross_junction.copy_from( old_block_definition.variants_road_cross_junction )
        new_block_definition.ground_spawn_location_object = old_block_definition.ground_spawn_location_object
        new_block_definition.air_spawn_location_object = old_block_definition.air_spawn_location_object
        new_block_definition.backward_compatibility_enabled = old_block_definition.backward_compatibility_enabled
        new_block_definition.backward_compatibility_model = old_block_definition.backward_compatibility_model
        new_block_definition.icon = old_block_definition.icon

        for ground_block_unit in old_block_definition.ground_block_units :
            new_block_definition.ground_block_units.add().copy_from( ground_block_unit )

        for air_block_unit in old_block_definition.air_block_units :
            new_block_definition.air_block_units.add().copy_from( air_block_unit )

        context.scene.tmunlimiter_selected_block_definition_index = len( context.scene.tmunlimiter_block_definitions ) - 1

        return { "FINISHED" }

class TMUnlimiter_AddVariation( bpy.types.Operator ) :
    bl_label = "Add variation"
    bl_idname = "scene.tmunlimiter_add_variation"

    @classmethod
    def poll( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if not block_definition :
            return False

        return len( block_definition.get_selected_variations() ) < 64

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        selected_variants = block_definition.get_selected_variants()
        selected_variations = block_definition.get_selected_variations( selected_variants )

        selected_variations.add()
        selected_variants.selected_variation_index = len( selected_variations ) - 1

        return { "FINISHED" }

class TMUnlimiter_RemoveVariation( bpy.types.Operator ) :
    bl_label = "Remove variation"
    bl_idname = "scene.tmunlimiter_remove_variation"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        selected_variants = block_definition.get_selected_variants()
        selected_variations = block_definition.get_selected_variations( selected_variants )

        selected_variations.remove( selected_variants.selected_variation_index )

        if selected_variants.selected_variation_index > 0 :
            selected_variants.selected_variation_index = selected_variants.selected_variation_index - 1

        return { "FINISHED" }

class TMUnlimiter_MoveVariationUpwards( bpy.types.Operator ) :
    bl_label = "Move variation upwards"
    bl_idname = "scene.tmunlimiter_move_variation_upwards"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        selected_variants = block_definition.get_selected_variants()
        selected_variations = block_definition.get_selected_variations( selected_variants )

        if selected_variants.selected_variation_index - 1 < 0 :
            return { "CANCELLED" }

        selected_variations.move( selected_variants.selected_variation_index, selected_variants.selected_variation_index - 1 )
        selected_variants.selected_variation_index = selected_variants.selected_variation_index - 1
        return { "FINISHED" }

class TMUnlimiter_MoveVariationDownwards( bpy.types.Operator ) :
    bl_label = "Move variation downwards"
    bl_idname = "scene.tmunlimiter_move_variation_downwards"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        selected_variants = block_definition.get_selected_variants()
        selected_variations = block_definition.get_selected_variations( selected_variants )

        if selected_variants.selected_variation_index + 1 >= len( selected_variations ) :
            return { "CANCELLED" }

        selected_variations.move( selected_variants.selected_variation_index, selected_variants.selected_variation_index + 1 )
        selected_variants.selected_variation_index = selected_variants.selected_variation_index + 1
        return { "FINISHED" }

class TMUnlimiter_AddBlockUnit( bpy.types.Operator ) :
    bl_label = "Add block unit"
    bl_idname = "scene.tmunlimiter_add_block_unit"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        block_units = block_definition.get_selected_block_units()
        block_units.add()
        block_definition.selected_block_unit_index = len( block_units ) - 1

        return { "FINISHED" }

class TMUnlimiter_RemoveBlockUnit( bpy.types.Operator ) :
    bl_label = "Remove block unit"
    bl_idname = "scene.tmunlimiter_remove_block_unit"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        block_units = block_definition.get_selected_block_units()
        block_units.remove( block_definition.selected_block_unit_index )

        if block_definition.selected_block_unit_index > 0 :
            block_definition.selected_block_unit_index = block_definition.selected_block_unit_index - 1

        return { "FINISHED" }

class TMUnlimiter_MoveBlockUnitUpwards( bpy.types.Operator ) :
    bl_label = "Move block unit upwards"
    bl_idname = "scene.tmunlimiter_move_block_unit_upwards"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        block_units = block_definition.get_selected_block_units()

        if block_definition.selected_block_unit_index - 1 < 0 :
            return { "CANCELLED" }

        block_units.move( block_definition.selected_block_unit_index, block_definition.selected_block_unit_index - 1 )
        block_definition.selected_block_unit_index = block_definition.selected_block_unit_index - 1
        return { "FINISHED" }

class TMUnlimiter_MoveBlockUnitDownwards( bpy.types.Operator ) :
    bl_label = "Move block unit downwards"
    bl_idname = "scene.tmunlimiter_move_block_unit_downwards"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        block_units = block_definition.get_selected_block_units()

        if block_definition.selected_block_unit_index + 1 >= len( block_units ) :
            return { "CANCELLED" }

        block_units.move( block_definition.selected_block_unit_index, block_definition.selected_block_unit_index + 1 )
        block_definition.selected_block_unit_index = block_definition.selected_block_unit_index + 1
        return { "FINISHED" }

class TMUnlimiter_CopyAllBlockUnitsToSecondType( bpy.types.Operator ) :
    bl_label = "Copy all block units to second type"
    bl_idname = "scene.tmunlimiter_copy_units_to_second_type"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        source_block_units = block_definition.get_selected_block_units()

        if block_definition.selected_block_unit_type == "ground" :
            destination_block_units = block_definition.air_block_units
        else :
            destination_block_units = block_definition.ground_block_units

        for soruce_block_unit in source_block_units :
            destination_block_units.add().copy_from( soruce_block_unit )

        return { "FINISHED" }

class TMUnlimiter_CreateBlockUnitsFromSelection( bpy.types.Operator ) :
    bl_label = "Create block units from selection"
    bl_idname = "scene.tmunlimiter_create_units_from_selection"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        if len( context.selected_objects ) < 1 :
            return { "CANCELLED" }

        block_units = block_definition.get_selected_block_units()

        for selected_object in context.selected_objects :
            validation_result, _ = TMUnlimiter_BlockUnit.static_object_validate( selected_object )

            if not validation_result :
                continue

            back_block_unit_index = len( block_units )

            if back_block_unit_index > 0 :
                block_unit_offset = TMUnlimiter_BlockUnit.static_calculate_offset( selected_object )

                while back_block_unit_index :
                    back_block_unit_index = back_block_unit_index - 1
                    back_block_unit_offset = block_units[ back_block_unit_index ].calculate_offset()

                    if block_unit_offset == back_block_unit_offset :
                        validation_result = False
                        break

                if not validation_result :
                    continue

            block_unit = block_units.add()
            block_unit.object = selected_object

        return { "FINISHED" }

class TMUnlimiter_SelectAllBlockUnits( bpy.types.Operator ) :
    bl_label = "Select all block units"
    bl_idname = "scene.tmunlimiter_select_all_units"

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        if block_definition is None :
            return { "CANCELLED" }

        block_units = block_definition.get_selected_block_units()

        if len( block_units ) < 1 :
            return { "CANCELLED" }

        for block_unit in block_units :
            if block_unit.object :
                block_unit.object.select_set( True )

        return { "FINISHED" }

class TMUnlimiter_ExportBlockDefinition( bpy.types.Operator, ExportHelper ) :
    """Save selected block definition to a *.Block.Gbx file. To enable export, switch to the object mode"""

    bl_label = "Export"
    bl_idname = "scene.export_selected_block_definition"
    check_extension = None

    filter_glob: bpy.props.StringProperty(
        default = "*.Block.Gbx",
        options = { "HIDDEN" },
    )

    @classmethod
    def poll( self, context: bpy.context ) :
        if context.mode != "OBJECT" :
            return False

        block_definition = get_selected_block_definition( context )

        if not block_definition :
            return False

        return \
        (
            block_definition.validate_identifier()[ 0 ]
            and
            block_definition.validate_author()[ 0 ]
            and
            block_definition.validate_variants()[ 0 ]
            and
            block_definition.validate_icon()[ 0 ]
            and
            block_definition.validate_block_units()[ 0 ]
        )

    def invoke( self, context: bpy.context, _ ) :
        if not self.filepath :
            self.filepath = ".Block.Gbx"

        context.window_manager.fileselect_add( self )
        return { "RUNNING_MODAL" }

    def execute( self, context: bpy.context ) :
        block_definition = get_selected_block_definition( context )

        gbx = GbxArchive( 0x3f002000 )
        gbx.context[ "depsgraph" ] = context.evaluated_depsgraph_get()

        try :
            block_definition.archive( gbx )
        except Exception as error :
            self.report( { "ERROR" }, str( error ) )
            print_exception( error )
            return { "CANCELLED" }

        gbx.do_save( self.properties.filepath )
        return { "FINISHED" }

class TMUnlimiter_BlockDefinitionItem( bpy.types.UIList ) :
    bl_idname = "TMUNLIMITER_UL_BlockDefinitionItem"

    def draw_item( self, __context__: bpy.types.Context, layout: bpy.types.UILayout, __data__, block_definition: TMUnlimiter_BlockDefinition, __icon__, __active_data__, __active_propname__, __index__ ) :
        layout.label( text = block_definition.identifier, icon = "MATCUBE" )

class TMUnlimiter_BlockDefinitionsPanel( bpy.types.Panel ) :
    bl_idname = "TMUNLIMITER_PT_BlockDefinitionsPanel"
    bl_label = "TMUnlimiter - Block Definitions"
    bl_category = "TMUnlimiter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw( self, context: bpy.context ) :
        layout = self.layout

        row = layout.row()
        row.template_list \
        (
            TMUnlimiter_BlockDefinitionItem.bl_idname,
            "block_definition",
            context.scene, "tmunlimiter_block_definitions",
            context.scene, "tmunlimiter_selected_block_definition_index"
        )
        col = row.column()
        col.operator( TMUnlimiter_AddBlockDefinition.bl_idname, text = "", icon = "ADD" )
        col.operator( TMUnlimiter_RemoveBlockDefinition.bl_idname, text = "", icon = "REMOVE" )
        col.operator( TMUnlimiter_MoveBlockDefinitionUpwards.bl_idname, text = "", icon = "TRIA_UP" )
        col.operator( TMUnlimiter_MoveBlockDefinitionDownwards.bl_idname, text = "", icon = "TRIA_DOWN" )

        row = layout.row()
        row.operator( TMUnlimiter_CopyBlockDefinition.bl_idname, icon = "COPY_ID" )

        block_definition = get_selected_block_definition( context )

        if block_definition is None:
            row.enabled = False
            return

        validation_result, validation_message = block_definition.validate_identifier()

        layout.alert = not validation_result
        layout.prop( block_definition, "identifier" )

        if layout.alert :
            layout.label( text = validation_message, icon = "ERROR" )

        validation_result, validation_message = block_definition.validate_author()

        layout.alert = not validation_result
        layout.prop( block_definition, "author" )

        if layout.alert :
            layout.label( text = validation_message, icon = "ERROR" )
            layout.alert = False

        layout.prop( block_definition, "block_type" )
        layout.prop( block_definition, "waypoint_type" )

        box = layout.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label( text = "Variants" )

        validation_result, validation_message = block_definition.validate_variants()

        box.alert = not validation_result
        box.prop( block_definition, "selected_variant" )

        if box.alert :
            box.label( text = validation_message, icon = "ERROR" )
            box.alert = False

        row = box.row()
        row.prop( block_definition, "selected_variant_type", expand = True )

        selected_variants = block_definition.get_selected_variants()

        row = box.row()
        row.template_list \
        (
            TMUnlimiter_VariationItem.bl_idname,
            "variation",
            selected_variants, f"{ block_definition.selected_variant_type }_variations",
            selected_variants, "selected_variation_index"
        )
        col = row.column()
        col.operator( TMUnlimiter_AddVariation.bl_idname, text = "", icon = "ADD" )
        col.operator( TMUnlimiter_RemoveVariation.bl_idname, text = "", icon = "REMOVE" )
        col.operator( TMUnlimiter_MoveVariationUpwards.bl_idname, text = "", icon = "TRIA_UP" )
        col.operator( TMUnlimiter_MoveVariationDownwards.bl_idname, text = "", icon = "TRIA_DOWN" )

        selected_variation = block_definition.get_selected_variation( selected_variants )

        if selected_variation :
            box.prop( selected_variation, "name" )

            if block_definition.is_trigger_allowed() :
                validation_result, validation_message = selected_variation.validate_model()
            else :
                validation_result, validation_message = ( True, None )

            box.alert = not validation_result
            box.prop( selected_variation, "model" )

            if box.alert :
                box.label( text = validation_message, icon = "ERROR" )

            if block_definition.is_trigger_allowed() :
                validation_result, validation_message = selected_variation.validate_trigger()

                box.alert = not validation_result
                box.prop( selected_variation, "trigger" )

                if box.alert :
                    box.label( text = validation_message, icon = "ERROR" )

        layout.prop( block_definition, "ground_spawn_location_object" )
        layout.prop( block_definition, "air_spawn_location_object" )

        validation_result, validation_message = block_definition.validate_icon()

        layout.alert = not validation_result
        layout.prop( block_definition, "icon" )

        if layout.alert :
            layout.label( text = validation_message, icon = "ERROR" )
            layout.alert = False

        box = layout.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label( text = "Block Units" )

        row = box.row()
        row.prop( block_definition, "selected_block_unit_type", expand = True )

        block_unit = block_definition.get_selected_block_unit()

        row = box.row()
        row.template_list \
        (
            TMUnlimiter_BlockUnitItem.bl_idname,
            "block_unit",
            block_definition, f"{ block_definition.selected_block_unit_type }_block_units",
            block_definition, "selected_block_unit_index"
        )
        col = row.column()
        col.operator( TMUnlimiter_AddBlockUnit.bl_idname, text = "", icon = "ADD" )
        col.operator( TMUnlimiter_RemoveBlockUnit.bl_idname, text = "", icon = "REMOVE" )
        col.operator( TMUnlimiter_MoveBlockUnitUpwards.bl_idname, text = "", icon = "TRIA_UP" )
        col.operator( TMUnlimiter_MoveBlockUnitDownwards.bl_idname, text = "", icon = "TRIA_DOWN" )

        if block_unit :
            box.prop( block_unit, "object", text = "Object" )

        box.operator( TMUnlimiter_CreateBlockUnitsFromSelection.bl_idname )
        box.operator( TMUnlimiter_SelectAllBlockUnits.bl_idname )
        box.operator( TMUnlimiter_CopyAllBlockUnitsToSecondType.bl_idname )

        layout.separator()
        layout.prop( block_definition, "backward_compatibility_enabled" )

        if block_definition.backward_compatibility_enabled :
            layout.prop( block_definition, "backward_compatibility_model" )

        layout.operator( TMUnlimiter_ExportBlockDefinition.bl_idname, text = "Export block definition", icon = "EXPORT" )

def __register__() :
    bpy.utils.register_class( TMUnlimiter_BlockUnit )
    bpy.utils.register_class( TMUnlimiter_BlockUnitItem )
    bpy.utils.register_class( TMUnlimiter_AddBlockUnit )
    bpy.utils.register_class( TMUnlimiter_RemoveBlockUnit )
    bpy.utils.register_class( TMUnlimiter_MoveBlockUnitUpwards )
    bpy.utils.register_class( TMUnlimiter_MoveBlockUnitDownwards )
    bpy.utils.register_class( TMUnlimiter_CopyAllBlockUnitsToSecondType )
    bpy.utils.register_class( TMUnlimiter_SelectAllBlockUnits )
    bpy.utils.register_class( TMUnlimiter_CreateBlockUnitsFromSelection )
    bpy.utils.register_class( TMUnlimiter_Variation )
    bpy.utils.register_class( TMUnlimiter_Variants )
    bpy.utils.register_class( TMUnlimiter_VariationItem )
    bpy.utils.register_class( TMUnlimiter_BlockDefinition )
    bpy.utils.register_class( TMUnlimiter_BlockDefinitionItem )
    bpy.utils.register_class( TMUnlimiter_AddBlockDefinition )
    bpy.utils.register_class( TMUnlimiter_RemoveBlockDefinition )
    bpy.utils.register_class( TMUnlimiter_MoveBlockDefinitionUpwards )
    bpy.utils.register_class( TMUnlimiter_MoveBlockDefinitionDownwards )
    bpy.utils.register_class( TMUnlimiter_CopyBlockDefinition )
    bpy.utils.register_class( TMUnlimiter_AddVariation )
    bpy.utils.register_class( TMUnlimiter_RemoveVariation )
    bpy.utils.register_class( TMUnlimiter_MoveVariationUpwards )
    bpy.utils.register_class( TMUnlimiter_MoveVariationDownwards )
    bpy.utils.register_class( TMUnlimiter_BlockDefinitionsPanel )
    bpy.utils.register_class( TMUnlimiter_ExportBlockDefinition )

    bpy.types.Scene.tmunlimiter_selected_block_definition_index = bpy.props.IntProperty( options = { "HIDDEN", "SKIP_SAVE" } )
    bpy.types.Scene.tmunlimiter_block_definitions = bpy.props.CollectionProperty( type = TMUnlimiter_BlockDefinition )

def __unregister__() :
    del bpy.types.Scene.tmunlimiter_block_definitions
    del bpy.types.Scene.tmunlimiter_selected_block_definition_index

    bpy.utils.unregister_class( TMUnlimiter_ExportBlockDefinition )
    bpy.utils.unregister_class( TMUnlimiter_BlockDefinitionsPanel )
    bpy.utils.unregister_class( TMUnlimiter_MoveVariationDownwards )
    bpy.utils.unregister_class( TMUnlimiter_MoveVariationUpwards )
    bpy.utils.unregister_class( TMUnlimiter_RemoveVariation )
    bpy.utils.unregister_class( TMUnlimiter_AddVariation )
    bpy.utils.unregister_class( TMUnlimiter_CopyBlockDefinition )
    bpy.utils.unregister_class( TMUnlimiter_MoveBlockDefinitionDownwards )
    bpy.utils.unregister_class( TMUnlimiter_MoveBlockDefinitionUpwards )
    bpy.utils.unregister_class( TMUnlimiter_RemoveBlockDefinition )
    bpy.utils.unregister_class( TMUnlimiter_AddBlockDefinition )
    bpy.utils.unregister_class( TMUnlimiter_BlockDefinitionItem )
    bpy.utils.unregister_class( TMUnlimiter_BlockDefinition )
    bpy.utils.unregister_class( TMUnlimiter_VariationItem )
    bpy.utils.unregister_class( TMUnlimiter_Variants )
    bpy.utils.unregister_class( TMUnlimiter_Variation )
    bpy.utils.unregister_class( TMUnlimiter_CreateBlockUnitsFromSelection )
    bpy.utils.unregister_class( TMUnlimiter_SelectAllBlockUnits )
    bpy.utils.unregister_class( TMUnlimiter_CopyAllBlockUnitsToSecondType )
    bpy.utils.unregister_class( TMUnlimiter_MoveBlockUnitDownwards )
    bpy.utils.unregister_class( TMUnlimiter_MoveBlockUnitUpwards )
    bpy.utils.unregister_class( TMUnlimiter_RemoveBlockUnit )
    bpy.utils.unregister_class( TMUnlimiter_AddBlockUnit )
    bpy.utils.unregister_class( TMUnlimiter_BlockUnitItem )
    bpy.utils.unregister_class( TMUnlimiter_BlockUnit )