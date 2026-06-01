# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Edit By Color by KIRI Engine",
    "author" : "Blue Nile 3D", 
    "description" : "Select and edit meshes by colour",
    "blender" : (4, 2, 0),
    "version" : (2, 0, 0),
    "location" : "N-Panel",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Mesh" 
}


import bpy
import bpy.utils.previews
import os
import bmesh
import webbrowser
import mathutils




def string_to_int(value):
    if value.isdigit():
        return int(value)
    return 0


def string_to_icon(value):
    if value in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys():
        return bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items[value].value
    return string_to_int(value)


def string_to_type(value, to_type, default):
    try:
        value = to_type(value)
    except:
        value = default
    return value


addon_keymaps = {}
_icons = None
edit_by_colourfunctionedit_effects = {'sna_tempsubdividemesh': 0, 'sna_templiveeffects': 0, 'sna_tempuvmap': '', 'sna_tempbasetexture': None, 'sna_tempcolourselectionr': 0.0, 'sna_tempcolourselectiong': 0.0, 'sna_tempcolourselectionb': 0.0, 'sna_tempselectiontype': 0, 'sna_tempcolourthreshold': 0.0, 'sna_tempsaturationthreshold': 0.0, 'sna_tempvaluethreshold': 0.0, 'sna_tempgrowshrink': 0, 'sna_tempmasking': 0, 'sna_tempmaskobject': None, 'sna_tempfilterislands': False, 'sna_tempislandthreshold': 0.0, 'sna_tempsetmaterial': None, 'sna_tempsmoothfaces': 0, 'sna_evaluatedfacecount': 0, }
edit_by_colourfunctionretopo_loops = {'sna_ebc_temp_store_active_object': None, 'sna_ebc_temp_store_retopo_object': None, }
edit_by_colourinterfacefunctions = {'sna_kiri_temp_active_object': None, }
edit_by_colourtexture = {'sna_ebc_temp_store_active_object': None, 'sna_ebc_temp_store_set_material': None, 'sna_ebc_active_bake_node': None, 'sna_ebc_bake_count': 0, 'sna_ebc_bake_type_list': [], }
edit_by_colourtexturebake_combined = {'sna_ebc_temp_store_active_object': None, 'sna_ebc_temp_store_base_texture': None, 'sna_ebc_temp_store_set_material': None, 'sna_ebc_active_bake_node': None, 'sna_ebc_bake_count': 0, 'sna_ebc_bake_type_list': [], }
edit_by_colourtexturebake_patch = {'sna_ebc_temp_store_active_object': None, 'sna_ebc_temp_store_set_material': None, 'sna_ebc_active_bake_node': None, 'sna_ebc_bake_count': 0, 'sna_ebc_bake_type_list': [], }


def property_exists(prop_path, glob, loc):
    try:
        eval(prop_path, glob, loc)
        return True
    except:
        return False


def sna_update_sna_ebc_live_effects_proxy_switch_52B23(self, context):
    sna_updated_prop = self.sna_ebc_live_effects_proxy_switch
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = (((((5 if (sna_updated_prop != 'Smooth and Set Material') else 4) if (sna_updated_prop != 'Set Material') else 3) if (sna_updated_prop != 'Smooth') else 2) if (sna_updated_prop != 'Delete Faces') else 1) if (sna_updated_prop != 'None') else 0)
    bpy.context.active_object.update_tag(refresh={'DATA'}, )
    if bpy.context and bpy.context.screen:
        for a in bpy.context.screen.areas:
            a.tag_redraw()
    if ((sna_updated_prop == 'None') or (sna_updated_prop == 'Delete Faces')):
        bpy.context.scene.sna_ebc_active_menu_full = 'Colour Selection'
        bpy.context.scene.sna_ebc_active_menu_retopo_loops = 'Colour Selection'


def load_preview_icon(path):
    global _icons
    if not path in _icons:
        if os.path.exists(path):
            _icons.load(path, path, "IMAGE")
        else:
            return 0
    return _icons[path].icon_id


def sna_active_object_properties_function_interface_3951A(layout_function, ):
    layout_function.label(text='Active Object', icon_value=string_to_icon('RADIOBUT_ON'))
    box_E7F59 = layout_function.box()
    box_E7F59.alert = False
    box_E7F59.enabled = True
    box_E7F59.active = True
    box_E7F59.use_property_split = False
    box_E7F59.use_property_decorate = False
    box_E7F59.alignment = 'Expand'.upper()
    box_E7F59.scale_x = 1.0
    box_E7F59.scale_y = 1.0
    if not True: box_E7F59.operator_context = "EXEC_DEFAULT"
    box_E7F59.prop_search(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], '["Socket_2"]', bpy.context.view_layer.objects.active.data, 'uv_layers', text='UV Map', icon='NONE')
    box_E7F59.prop_search(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], '["Socket_4"]', bpy.data, 'images', text='Base Texture', icon='NONE')
    attr_A311B = '["' + str('Socket_50' + '"]') 
    box_E7F59.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_A311B, text='Subdivide Mesh', icon_value=0, emboss=True)
    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_2'] == ''):
        box_6329F = layout_function.box()
        box_6329F.alert = (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_2'] == '')
        box_6329F.enabled = True
        box_6329F.active = True
        box_6329F.use_property_split = False
        box_6329F.use_property_decorate = False
        box_6329F.alignment = 'Expand'.upper()
        box_6329F.scale_x = 1.0
        box_6329F.scale_y = 1.0
        if not True: box_6329F.operator_context = "EXEC_DEFAULT"
        box_6329F.label(text='UV Map is required', icon_value=0)
    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4'] == None):
        box_3791C = layout_function.box()
        box_3791C.alert = (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4'] == None)
        box_3791C.enabled = True
        box_3791C.active = True
        box_3791C.use_property_split = False
        box_3791C.use_property_decorate = False
        box_3791C.alignment = 'Expand'.upper()
        box_3791C.scale_x = 1.0
        box_3791C.scale_y = 1.0
        if not True: box_3791C.operator_context = "EXEC_DEFAULT"
        box_3791C.label(text='Base Texture is required', icon_value=0)


class SNA_OT_Remove_Edit_By_Colour_Modifier_C523D(bpy.types.Operator):
    bl_idname = "sna.remove_edit_by_colour_modifier_c523d"
    bl_label = "Remove Edit By Colour Modifier"
    bl_description = "Removes the Edit By Colour modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        bpy.context.view_layer.objects.active.modifiers.remove(modifier=bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], )
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Add_Edit_By_Colour_Modifier_381C0(bpy.types.Operator):
    bl_idname = "sna.add_edit_by_colour_modifier_381c0"
    bl_label = "Add Edit By Colour Modifier"
    bl_description = "Adds the Edit By Colour modifier to the active object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_add_edit_by_colour_modifier_function_execute_7A473()
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_add_remove_modifier_function_interface_02DDA(layout_function, ):
    if (bpy.context.mode == 'OBJECT'):
        if (property_exists("bpy.context.view_layer.objects.active.modifiers", globals(), locals()) and 'KIRI_Edit_By_Colour_GN' in bpy.context.view_layer.objects.active.modifiers):
            grid_4A8AA = layout_function.grid_flow(columns=3, row_major=False, even_columns=False, even_rows=False, align=False)
            grid_4A8AA.enabled = True
            grid_4A8AA.active = True
            grid_4A8AA.use_property_split = False
            grid_4A8AA.use_property_decorate = False
            grid_4A8AA.alignment = 'Expand'.upper()
            grid_4A8AA.scale_x = 1.0
            grid_4A8AA.scale_y = 1.0
            if not True: grid_4A8AA.operator_context = "EXEC_DEFAULT"
            grid_4A8AA.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], 'show_viewport', text='', icon_value=0, emboss=True)
            op = grid_4A8AA.operator('sna.remove_edit_by_colour_modifier_c523d', text='', icon_value=string_to_icon('TRASH'), emboss=True, depress=False)
            op = grid_4A8AA.operator('sna.apply_edit_by_colour_modifier_45130', text='', icon_value=string_to_icon('CHECKMARK'), emboss=True, depress=False)
        else:
            op = layout_function.operator('sna.add_edit_by_colour_modifier_381c0', text='Add Edit By Colour Modifier', icon_value=string_to_icon('MODIFIER'), emboss=True, depress=False)
    else:
        layout_function.label(text='Enter Object Mode to add the modifier', icon_value=0)


def sna_add_edit_by_colour_modifier_function_execute_7A473():
    if (property_exists("bpy.data.node_groups", globals(), locals()) and 'KIRI_Edit_By_Colour_GN' in bpy.data.node_groups):
        pass
    else:
        before_data = list(bpy.data.node_groups)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'KIRI_Edit_By_Colour_NODE_APPEND.blend') + r'\NodeTree', filename='KIRI_Edit_By_Colour_GN', link=False)
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.node_groups)))
        appended_EA80E = None if not new_data else new_data[0]
    if (property_exists("bpy.context.view_layer.objects.active.modifiers", globals(), locals()) and 'KIRI_Edit_By_Colour_GN' in bpy.context.view_layer.objects.active.modifiers):
        pass
    else:
        modifier_13AD0 = bpy.context.view_layer.objects.active.modifiers.new(name='KIRI_Edit_By_Colour_GN', type='NODES', )
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'].node_group = bpy.data.node_groups['KIRI_Edit_By_Colour_GN']
    if (property_exists("bpy.data.materials", globals(), locals()) and 'KIRI_LOGO' in bpy.data.materials):
        pass
    else:
        before_data = list(bpy.data.materials)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'KIRI_Edit_By_Colour_NODE_APPEND.blend') + r'\Material', filename='KIRI_LOGO', link=False)
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.materials)))
        appended_6FC99 = None if not new_data else new_data[0]
    bpy.context.view_layer.objects.active.sna_ebc_live_effects_proxy_switch = 'Set Material'
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_26'] = bpy.data.materials['KIRI_LOGO']
    if (property_exists("bpy.data.materials", globals(), locals()) and 'Retopo Material' in bpy.data.materials):
        pass
    else:
        before_data = list(bpy.data.materials)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'KIRI_Edit_By_Colour_NODE_APPEND.blend') + r'\Material', filename='Retopo Material', link=False)
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.materials)))
        appended_F775F = None if not new_data else new_data[0]
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_63'] = bpy.data.materials['Retopo Material']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'].show_in_editmode = False
    bpy.context.active_object.update_tag(refresh={'DATA'}, )
    if bpy.context and bpy.context.screen:
        for a in bpy.context.screen.areas:
            a.tag_redraw()


class SNA_OT_Apply_Edit_By_Colour_Modifier_45130(bpy.types.Operator):
    bl_idname = "sna.apply_edit_by_colour_modifier_45130"
    bl_label = "Apply Edit By Colour Modifier"
    bl_description = "Applies the Edit By Colour modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        modifier_name = 'KIRI_Edit_By_Colour_GN'
        object_name = bpy.context.view_layer.objects.active.name
        obj = bpy.data.objects.get(object_name)
        if obj:
            modifier = obj.modifiers.get(modifier_name)
            if modifier:
                if not modifier.show_viewport:
                    # Simply remove the modifier if it's hidden
                    obj.modifiers.remove(modifier)
                    print(f"Removed hidden modifier '{modifier_name}' from object '{object_name}'.")
                else:
                    # Apply normally if visible
                    bpy.ops.object.modifier_apply(modifier=modifier_name)
                    print(f"Applied visible modifier '{modifier_name}' to object '{object_name}'.")
            else:
                print(f"Modifier '{modifier_name}' not found on object '{object_name}'.")
        else:
            print(f"Object '{object_name}' not found.")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_adjust_selection_function_interface_541E9(layout_function, ):
    layout_function.label(text='Selection', icon_value=string_to_icon('RADIOBUT_ON'))
    box_9F213 = layout_function.box()
    box_9F213.alert = False
    box_9F213.enabled = True
    box_9F213.active = True
    box_9F213.use_property_split = False
    box_9F213.use_property_decorate = False
    box_9F213.alignment = 'Expand'.upper()
    box_9F213.scale_x = 1.0
    box_9F213.scale_y = 1.0
    if not True: box_9F213.operator_context = "EXEC_DEFAULT"
    attr_03B44 = '["' + str('Socket_35' + '"]') 
    box_9F213.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_03B44, text='', icon_value=0, emboss=True)
    attr_52066 = '["' + str('Socket_3' + '"]') 
    box_9F213.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_52066, text='', icon_value=0, emboss=True)
    if ((bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_35'] == 0) or (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_35'] == 1)):
        box_0CA7B = layout_function.box()
        box_0CA7B.alert = False
        box_0CA7B.enabled = True
        box_0CA7B.active = True
        box_0CA7B.use_property_split = False
        box_0CA7B.use_property_decorate = False
        box_0CA7B.alignment = 'Expand'.upper()
        box_0CA7B.scale_x = 1.0
        box_0CA7B.scale_y = 1.0
        if not True: box_0CA7B.operator_context = "EXEC_DEFAULT"
        attr_20E93 = '["' + str('Socket_21' + '"]') 
        box_0CA7B.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_20E93, text='Colour Threshold', icon_value=0, emboss=True)
        attr_E51CE = '["' + str('Socket_33' + '"]') 
        box_0CA7B.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_E51CE, text='Saturation Threshold', icon_value=0, emboss=True)
        attr_574A7 = '["' + str('Socket_34' + '"]') 
        box_0CA7B.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_574A7, text='Value Threshold', icon_value=0, emboss=True)
    box_EC903 = layout_function.box()
    box_EC903.alert = False
    box_EC903.enabled = True
    box_EC903.active = True
    box_EC903.use_property_split = False
    box_EC903.use_property_decorate = False
    box_EC903.alignment = 'Expand'.upper()
    box_EC903.scale_x = 1.0
    box_EC903.scale_y = 1.0
    if not True: box_EC903.operator_context = "EXEC_DEFAULT"
    attr_F9A32 = '["' + str('Socket_44' + '"]') 
    box_EC903.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_F9A32, text='Filter Small Islands', icon_value=0, emboss=True, toggle=True)
    if bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_44']:
        attr_55096 = '["' + str('Socket_45' + '"]') 
        box_EC903.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_55096, text='Island Threshold', icon_value=0, emboss=True, toggle=True)
    box_6CA41 = layout_function.box()
    box_6CA41.alert = False
    box_6CA41.enabled = True
    box_6CA41.active = True
    box_6CA41.use_property_split = False
    box_6CA41.use_property_decorate = False
    box_6CA41.alignment = 'Expand'.upper()
    box_6CA41.scale_x = 1.0
    box_6CA41.scale_y = 1.0
    if not True: box_6CA41.operator_context = "EXEC_DEFAULT"
    attr_2B70C = '["' + str('Socket_5' + '"]') 
    box_6CA41.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_2B70C, text='+ Grow / - Shrink Selection', icon_value=0, emboss=True)
    box_E4145 = layout_function.box()
    box_E4145.alert = False
    box_E4145.enabled = True
    box_E4145.active = True
    box_E4145.use_property_split = False
    box_E4145.use_property_decorate = False
    box_E4145.alignment = 'Expand'.upper()
    box_E4145.scale_x = 1.0
    box_E4145.scale_y = 1.0
    if not True: box_E4145.operator_context = "EXEC_DEFAULT"
    attr_DDF2E = '["' + str('Socket_47' + '"]') 
    box_E4145.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_DDF2E, text='', icon_value=0, emboss=True)
    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_47'] == 0):
        pass
    else:
        col_12627 = box_E4145.column(heading='', align=False)
        col_12627.alert = False
        col_12627.enabled = True
        col_12627.active = True
        col_12627.use_property_split = False
        col_12627.use_property_decorate = False
        col_12627.scale_x = 1.0
        col_12627.scale_y = 1.0
        col_12627.alignment = 'Expand'.upper()
        col_12627.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        box_945FC = col_12627.box()
        box_945FC.alert = False
        box_945FC.enabled = True
        box_945FC.active = True
        box_945FC.use_property_split = False
        box_945FC.use_property_decorate = False
        box_945FC.alignment = 'Expand'.upper()
        box_945FC.scale_x = 1.0
        box_945FC.scale_y = 1.0
        if not True: box_945FC.operator_context = "EXEC_DEFAULT"
        box_945FC.label(text='Mask Object', icon_value=0)
        attr_7E01F = '["' + str('Socket_36' + '"]') 
        box_945FC.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_7E01F, text='', icon_value=0, emboss=True)
        box_1EE16 = col_12627.box()
        box_1EE16.alert = False
        box_1EE16.enabled = True
        box_1EE16.active = True
        box_1EE16.use_property_split = False
        box_1EE16.use_property_decorate = False
        box_1EE16.alignment = 'Expand'.upper()
        box_1EE16.scale_x = 1.0
        box_1EE16.scale_y = 1.0
        if not True: box_1EE16.operator_context = "EXEC_DEFAULT"
        op = box_1EE16.operator('sna.add_wire_cube_24ccd', text='', icon_value=string_to_icon('CUBE'), emboss=True, depress=False)
    box_CC1AA = layout_function.box()
    box_CC1AA.alert = False
    box_CC1AA.enabled = True
    box_CC1AA.active = True
    box_CC1AA.use_property_split = False
    box_CC1AA.use_property_decorate = False
    box_CC1AA.alignment = 'Expand'.upper()
    box_CC1AA.scale_x = 1.0
    box_CC1AA.scale_y = 1.0
    if not True: box_CC1AA.operator_context = "EXEC_DEFAULT"
    attr_C9718 = '["' + str('Socket_55' + '"]') 
    box_CC1AA.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_C9718, text='Smooth Boundary', icon_value=0, emboss=True, toggle=True)
    if bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_55']:
        attr_91361 = '["' + str('Socket_53' + '"]') 
        box_CC1AA.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_91361, text='Smoothing Iterations', icon_value=0, emboss=True, toggle=True)


class SNA_OT_Add_Wire_Cube_24Ccd(bpy.types.Operator):
    bl_idname = "sna.add_wire_cube_24ccd"
    bl_label = "Add wire cube"
    bl_description = "Add a wireframe cube at the 3D cursor location."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        before_data = list(bpy.data.objects)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'KIRI_Edit_By_Colour_OBJECT_APPEND.blend') + r'\Object', filename='Wire Cube', link=False)
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.objects)))
        appended_D8D24 = None if not new_data else new_data[0]
        appended_D8D24.location = bpy.context.scene.cursor.location
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_edit_effects_function_interface_6C02F(layout_function, ):
    layout_function.label(text='Edit Effects', icon_value=string_to_icon('RADIOBUT_ON'))
    box_B7AC1 = layout_function.box()
    box_B7AC1.alert = False
    box_B7AC1.enabled = True
    box_B7AC1.active = True
    box_B7AC1.use_property_split = False
    box_B7AC1.use_property_decorate = False
    box_B7AC1.alignment = 'Expand'.upper()
    box_B7AC1.scale_x = 1.0
    box_B7AC1.scale_y = 1.0
    if not True: box_B7AC1.operator_context = "EXEC_DEFAULT"
    op = box_B7AC1.operator('sna.edit_by_colour__select_77ba8', text='Select', icon_value=string_to_icon('RESTRICT_SELECT_OFF'), emboss=True, depress=False)
    op.sna_apply_subdivision = False
    op.sna_set_live_effects_to = 'None'
    op = box_B7AC1.operator('sna.edit_by_colour__split_819ad', text='Split', icon_value=string_to_icon('MOD_EDGESPLIT'), emboss=True, depress=False)
    op.sna_apply_subdivision = False
    op.sna_set_live_effects_to = 'None'
    op = box_B7AC1.operator('sna.edit_by_colour__duplicate_f7267', text='Duplicate', icon_value=string_to_icon('DUPLICATE'), emboss=True, depress=False)
    op.sna_apply_subdivision = False
    op.sna_set_live_effects_to = 'None'


class SNA_OT_Edit_By_Colour__Select_77Ba8(bpy.types.Operator):
    bl_idname = "sna.edit_by_colour__select_77ba8"
    bl_label = "Edit By Colour - Select"
    bl_description = "Selects faces currently assigned by the Edit By Colour modifier"
    bl_options = {"REGISTER", "UNDO"}
    sna_apply_subdivision: bpy.props.BoolProperty(name='Apply Subdivision?', description='', default=False)

    def sna_set_live_effects_to_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_set_live_effects_to: bpy.props.EnumProperty(name='Set Live Effects to:', description='', items=[('None', 'None', '', 0, 0), ('Set Material', 'Set Material', '', 0, 1), ('No Change', 'No Change', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_ebc_select_function_execute_82A8F(self.sna_apply_subdivision, self.sna_set_live_effects_to)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_8EA7B = layout.box()
        box_8EA7B.alert = False
        box_8EA7B.enabled = True
        box_8EA7B.active = True
        box_8EA7B.use_property_split = False
        box_8EA7B.use_property_decorate = False
        box_8EA7B.alignment = 'Expand'.upper()
        box_8EA7B.scale_x = 1.0
        box_8EA7B.scale_y = 1.0
        if not True: box_8EA7B.operator_context = "EXEC_DEFAULT"
        box_C2E42 = box_8EA7B.box()
        box_C2E42.alert = True
        box_C2E42.enabled = True
        box_C2E42.active = True
        box_C2E42.use_property_split = False
        box_C2E42.use_property_decorate = False
        box_C2E42.alignment = 'Expand'.upper()
        box_C2E42.scale_x = 1.0
        box_C2E42.scale_y = 1.0
        if not True: box_C2E42.operator_context = "EXEC_DEFAULT"
        box_C2E42.label(text='The Edit By Colour modifier will be applied, then re-added', icon_value=string_to_icon('INFO'))
        box_C2E42.label(text='         These effects are destructive', icon_value=0)
        box_8EA7B.label(text='Set Live Effects to:', icon_value=0)
        box_8EA7B.prop(self, 'sna_set_live_effects_to', text='', icon_value=0, emboss=True)
        box_8EA7B.prop(self, 'sna_apply_subdivision', text='Apply Subdivisions', icon_value=0, emboss=True, toggle=False)
        if self.sna_apply_subdivision:
            col_16831 = box_8EA7B.column(heading='', align=False)
            col_16831.alert = False
            col_16831.enabled = True
            col_16831.active = True
            col_16831.use_property_split = False
            col_16831.use_property_decorate = False
            col_16831.scale_x = 1.0
            col_16831.scale_y = 1.0
            col_16831.alignment = 'Expand'.upper()
            col_16831.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_DB4E3 = col_16831.box()
            box_DB4E3.alert = False
            box_DB4E3.enabled = True
            box_DB4E3.active = True
            box_DB4E3.use_property_split = False
            box_DB4E3.use_property_decorate = False
            box_DB4E3.alignment = 'Expand'.upper()
            box_DB4E3.scale_x = 1.0
            box_DB4E3.scale_y = 1.0
            if not True: box_DB4E3.operator_context = "EXEC_DEFAULT"
            box_DB4E3.label(text='This act is destructive', icon_value=string_to_icon('TRIA_RIGHT'))
            box_DB4E3.label(text='Select will take longer with higher face counts', icon_value=string_to_icon('TRIA_RIGHT'))
            box_DB4E3.label(text='Other modifiers will not be applied', icon_value=string_to_icon('TRIA_RIGHT'))
            box_930B3 = col_16831.box()
            box_930B3.alert = False
            box_930B3.enabled = True
            box_930B3.active = True
            box_930B3.use_property_split = False
            box_930B3.use_property_decorate = False
            box_930B3.alignment = 'Expand'.upper()
            box_930B3.scale_x = 1.0
            box_930B3.scale_y = 1.0
            if not True: box_930B3.operator_context = "EXEC_DEFAULT"
            box_930B3.label(text='Base face count =' + ' ' + str(len(bpy.context.view_layer.objects.active.data.polygons)), icon_value=0)
            box_930B3.label(text='Face count with subdivisions + other modifiers =' + ' ' + str(edit_by_colourfunctionedit_effects['sna_evaluatedfacecount']), icon_value=0)

    def invoke(self, context, event):
        bm_D9A23 = bmesh.new()
        if bpy.context.view_layer.objects.active:
            if bpy.context.view_layer.objects.active.mode == 'EDIT' and False:
                bm_D9A23 = bmesh.from_edit_mesh(bpy.context.view_layer.objects.active.data)
            else:
                if True:
                    dg = bpy.context.evaluated_depsgraph_get()
                    bm_D9A23.from_mesh(bpy.context.view_layer.objects.active.evaluated_get(dg).to_mesh())
                else:
                    bm_D9A23.from_mesh(bpy.context.view_layer.objects.active.data)
        if False:
            bm_D9A23.transform(bpy.context.view_layer.objects.active.matrix_world)
        bm_D9A23.verts.ensure_lookup_table()
        bm_D9A23.faces.ensure_lookup_table()
        bm_D9A23.edges.ensure_lookup_table()
        edit_by_colourfunctionedit_effects['sna_evaluatedfacecount'] = len(bm_D9A23.faces)
        return context.window_manager.invoke_props_dialog(self, width=500)


def sna_ebc_select_function_execute_82A8F(Apply_Subdivision, Set_Effects_To):
    if (property_exists("bpy.context.view_layer.objects.active.data.attributes", globals(), locals()) and 'EBC_Selection' in bpy.context.view_layer.objects.active.data.attributes):
        bpy.context.view_layer.objects.active.data.attributes.remove(attribute=bpy.context.view_layer.objects.active.data.attributes['EBC_Selection'], )
    edit_by_colourfunctionedit_effects['sna_templiveeffects'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48']
    edit_by_colourfunctionedit_effects['sna_tempsubdividemesh'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_50']
    edit_by_colourfunctionedit_effects['sna_tempuvmap'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_2']
    edit_by_colourfunctionedit_effects['sna_tempbasetexture'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4']
    bpy.context.scene.sna_ebc_colour_selection = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_3']
    edit_by_colourfunctionedit_effects['sna_tempselectiontype'] = string_to_type(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_35'], int, 0)
    edit_by_colourfunctionedit_effects['sna_tempcolourthreshold'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_21']
    edit_by_colourfunctionedit_effects['sna_tempsaturationthreshold'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_33']
    edit_by_colourfunctionedit_effects['sna_tempvaluethreshold'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_34']
    edit_by_colourfunctionedit_effects['sna_tempgrowshrink'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_5']
    edit_by_colourfunctionedit_effects['sna_tempmasking'] = string_to_type(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_47'], int, 0)
    edit_by_colourfunctionedit_effects['sna_tempmaskobject'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_36']
    edit_by_colourfunctionedit_effects['sna_tempfilterislands'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_44']
    edit_by_colourfunctionedit_effects['sna_tempislandthreshold'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_45']
    edit_by_colourfunctionedit_effects['sna_tempsetmaterial'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_26']
    edit_by_colourfunctionedit_effects['sna_tempsmoothfaces'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_22']
    if Apply_Subdivision:
        pass
    else:
        bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_50'] = 0
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = 0
    bpy.context.active_object.update_tag(refresh={'DATA'}, )
    if bpy.context and bpy.context.screen:
        for a in bpy.context.screen.areas:
            a.tag_redraw()
    modifier_name = 'KIRI_Edit_By_Colour_GN'
    object_name = bpy.context.view_layer.objects.active.name
    obj = bpy.data.objects.get(object_name)
    if obj:
        modifier = obj.modifiers.get(modifier_name)
        if modifier:
            if not modifier.show_viewport:
                # Simply remove the modifier if it's hidden
                obj.modifiers.remove(modifier)
                print(f"Removed hidden modifier '{modifier_name}' from object '{object_name}'.")
            else:
                # Apply normally if visible
                bpy.ops.object.modifier_apply(modifier=modifier_name)
                print(f"Applied visible modifier '{modifier_name}' to object '{object_name}'.")
        else:
            print(f"Modifier '{modifier_name}' not found on object '{object_name}'.")
    else:
        print(f"Object '{object_name}' not found.")
    sna_add_edit_by_colour_modifier_function_execute_7A473()
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_2'] = edit_by_colourfunctionedit_effects['sna_tempuvmap']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4'] = edit_by_colourfunctionedit_effects['sna_tempbasetexture']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_3'] = bpy.context.scene.sna_ebc_colour_selection
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_35'] = edit_by_colourfunctionedit_effects['sna_tempselectiontype']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_21'] = edit_by_colourfunctionedit_effects['sna_tempcolourthreshold']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_33'] = edit_by_colourfunctionedit_effects['sna_tempsaturationthreshold']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_34'] = edit_by_colourfunctionedit_effects['sna_tempvaluethreshold']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_5'] = edit_by_colourfunctionedit_effects['sna_tempgrowshrink']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_47'] = edit_by_colourfunctionedit_effects['sna_tempmasking']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_36'] = edit_by_colourfunctionedit_effects['sna_tempmaskobject']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_44'] = edit_by_colourfunctionedit_effects['sna_tempfilterislands']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_45'] = edit_by_colourfunctionedit_effects['sna_tempislandthreshold']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_26'] = edit_by_colourfunctionedit_effects['sna_tempsetmaterial']
    bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_22'] = edit_by_colourfunctionedit_effects['sna_tempsmoothfaces']
    if Apply_Subdivision:
        bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_50'] = edit_by_colourfunctionedit_effects['sna_tempsubdividemesh']
    if (Set_Effects_To == 'None'):
        bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = 0
        bpy.context.active_object.update_tag(refresh={'DATA'}, )
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        bpy.context.view_layer.objects.active.sna_ebc_live_effects_proxy_switch = Set_Effects_To
    if (Set_Effects_To == 'Set Material'):
        bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = 3
        bpy.context.active_object.update_tag(refresh={'DATA'}, )
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        bpy.context.view_layer.objects.active.sna_ebc_live_effects_proxy_switch = Set_Effects_To
    if (Set_Effects_To == 'No Change'):
        bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = edit_by_colourfunctionedit_effects['sna_templiveeffects']
        bpy.context.view_layer.objects.active.sna_ebc_live_effects_proxy_switch = ((((('Retopo Loops' if (edit_by_colourfunctionedit_effects['sna_templiveeffects'] != 4) else 'Smooth and Set Material') if (edit_by_colourfunctionedit_effects['sna_templiveeffects'] != 3) else 'Set Material') if (edit_by_colourfunctionedit_effects['sna_templiveeffects'] != 2) else 'Smooth') if (edit_by_colourfunctionedit_effects['sna_templiveeffects'] != 1) else 'Delete Faces') if (edit_by_colourfunctionedit_effects['sna_templiveeffects'] != 0) else 'None')
        bpy.context.active_object.update_tag(refresh={'DATA'}, )
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
    bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='EDIT', toggle=False)
    bpy.ops.mesh.select_mode('INVOKE_DEFAULT', type='FACE')
    bpy.ops.mesh.select_all('INVOKE_DEFAULT', action='DESELECT')
    bpy.context.view_layer.objects.active.data.attributes.active = bpy.context.view_layer.objects.active.data.attributes['EBC_Selection']
    bpy.ops.mesh.select_by_attribute('INVOKE_DEFAULT', )


class SNA_OT_Edit_By_Colour__Split_819Ad(bpy.types.Operator):
    bl_idname = "sna.edit_by_colour__split_819ad"
    bl_label = "Edit By Colour - Split"
    bl_description = "Splits faces currently assigned by the Edit By Colour modifier from the current mesh."
    bl_options = {"REGISTER", "UNDO"}
    sna_apply_subdivision: bpy.props.BoolProperty(name='Apply Subdivision?', description='', default=False)

    def sna_set_live_effects_to_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_set_live_effects_to: bpy.props.EnumProperty(name='Set Live Effects to:', description='', items=[('None', 'None', '', 0, 0), ('Set Material', 'Set Material', '', 0, 1), ('No Change', 'No Change', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_ebc_select_function_execute_82A8F(self.sna_apply_subdivision, self.sna_set_live_effects_to)
        bpy.ops.mesh.separate('INVOKE_DEFAULT', type='SELECTED')
        bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='OBJECT', toggle=True)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_7F2D8 = layout.box()
        box_7F2D8.alert = False
        box_7F2D8.enabled = True
        box_7F2D8.active = True
        box_7F2D8.use_property_split = False
        box_7F2D8.use_property_decorate = False
        box_7F2D8.alignment = 'Expand'.upper()
        box_7F2D8.scale_x = 1.0
        box_7F2D8.scale_y = 1.0
        if not True: box_7F2D8.operator_context = "EXEC_DEFAULT"
        box_9AE97 = box_7F2D8.box()
        box_9AE97.alert = True
        box_9AE97.enabled = True
        box_9AE97.active = True
        box_9AE97.use_property_split = False
        box_9AE97.use_property_decorate = False
        box_9AE97.alignment = 'Expand'.upper()
        box_9AE97.scale_x = 1.0
        box_9AE97.scale_y = 1.0
        if not True: box_9AE97.operator_context = "EXEC_DEFAULT"
        box_9AE97.label(text='The Edit By Colour modifier will be applied, then re-added', icon_value=string_to_icon('INFO'))
        box_9AE97.label(text='         These effects are destructive', icon_value=0)
        box_7F2D8.label(text='Set Live Effects to:', icon_value=0)
        box_7F2D8.prop(self, 'sna_set_live_effects_to', text='', icon_value=0, emboss=True)
        box_7F2D8.prop(self, 'sna_apply_subdivision', text='Apply Subdivisions', icon_value=0, emboss=True, toggle=False)
        if self.sna_apply_subdivision:
            col_0AD18 = box_7F2D8.column(heading='', align=False)
            col_0AD18.alert = False
            col_0AD18.enabled = True
            col_0AD18.active = True
            col_0AD18.use_property_split = False
            col_0AD18.use_property_decorate = False
            col_0AD18.scale_x = 1.0
            col_0AD18.scale_y = 1.0
            col_0AD18.alignment = 'Expand'.upper()
            col_0AD18.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_91209 = col_0AD18.box()
            box_91209.alert = False
            box_91209.enabled = True
            box_91209.active = True
            box_91209.use_property_split = False
            box_91209.use_property_decorate = False
            box_91209.alignment = 'Expand'.upper()
            box_91209.scale_x = 1.0
            box_91209.scale_y = 1.0
            if not True: box_91209.operator_context = "EXEC_DEFAULT"
            box_91209.label(text='This act is destructive', icon_value=string_to_icon('TRIA_RIGHT'))
            box_91209.label(text='Select will take longer with higher face counts', icon_value=string_to_icon('TRIA_RIGHT'))
            box_91209.label(text='Other modifiers will not be applied', icon_value=string_to_icon('TRIA_RIGHT'))
            box_AA5B1 = col_0AD18.box()
            box_AA5B1.alert = False
            box_AA5B1.enabled = True
            box_AA5B1.active = True
            box_AA5B1.use_property_split = False
            box_AA5B1.use_property_decorate = False
            box_AA5B1.alignment = 'Expand'.upper()
            box_AA5B1.scale_x = 1.0
            box_AA5B1.scale_y = 1.0
            if not True: box_AA5B1.operator_context = "EXEC_DEFAULT"
            box_AA5B1.label(text='Base face count =' + ' ' + str(len(bpy.context.view_layer.objects.active.data.polygons)), icon_value=0)
            box_AA5B1.label(text='Face count with subdivisions + other modifiers =' + ' ' + str(edit_by_colourfunctionedit_effects['sna_evaluatedfacecount']), icon_value=0)

    def invoke(self, context, event):
        bm_75D99 = bmesh.new()
        if bpy.context.view_layer.objects.active:
            if bpy.context.view_layer.objects.active.mode == 'EDIT' and False:
                bm_75D99 = bmesh.from_edit_mesh(bpy.context.view_layer.objects.active.data)
            else:
                if True:
                    dg = bpy.context.evaluated_depsgraph_get()
                    bm_75D99.from_mesh(bpy.context.view_layer.objects.active.evaluated_get(dg).to_mesh())
                else:
                    bm_75D99.from_mesh(bpy.context.view_layer.objects.active.data)
        if False:
            bm_75D99.transform(bpy.context.view_layer.objects.active.matrix_world)
        bm_75D99.verts.ensure_lookup_table()
        bm_75D99.faces.ensure_lookup_table()
        bm_75D99.edges.ensure_lookup_table()
        edit_by_colourfunctionedit_effects['sna_evaluatedfacecount'] = len(bm_75D99.faces)
        return context.window_manager.invoke_props_dialog(self, width=500)


class SNA_OT_Edit_By_Colour__Duplicate_F7267(bpy.types.Operator):
    bl_idname = "sna.edit_by_colour__duplicate_f7267"
    bl_label = "Edit By Colour - Duplicate"
    bl_description = "Dupliates faces currently assigned by the Edit By Colour modifier and leaves the original mesh intact."
    bl_options = {"REGISTER", "UNDO"}
    sna_apply_subdivision: bpy.props.BoolProperty(name='Apply Subdivision?', description='', default=False)

    def sna_set_live_effects_to_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_set_live_effects_to: bpy.props.EnumProperty(name='Set Live Effects to:', description='', items=[('None', 'None', '', 0, 0), ('Set Material', 'Set Material', '', 0, 1), ('No Change', 'No Change', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        sna_ebc_select_function_execute_82A8F(self.sna_apply_subdivision, self.sna_set_live_effects_to)
        # Get the active object
        obj = bpy.context.active_object
        # Store the selected faces' indices
        selected_faces = [f.index for f in obj.data.polygons if f.select]
        # Duplicate the selected faces
        bpy.ops.mesh.duplicate()
        # Separate the duplicated faces
        bpy.ops.mesh.separate(type='SELECTED')
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_10D06 = layout.box()
        box_10D06.alert = False
        box_10D06.enabled = True
        box_10D06.active = True
        box_10D06.use_property_split = False
        box_10D06.use_property_decorate = False
        box_10D06.alignment = 'Expand'.upper()
        box_10D06.scale_x = 1.0
        box_10D06.scale_y = 1.0
        if not True: box_10D06.operator_context = "EXEC_DEFAULT"
        box_77480 = box_10D06.box()
        box_77480.alert = True
        box_77480.enabled = True
        box_77480.active = True
        box_77480.use_property_split = False
        box_77480.use_property_decorate = False
        box_77480.alignment = 'Expand'.upper()
        box_77480.scale_x = 1.0
        box_77480.scale_y = 1.0
        if not True: box_77480.operator_context = "EXEC_DEFAULT"
        box_77480.label(text='The Edit By Colour modifier will be applied, then re-added', icon_value=string_to_icon('INFO'))
        box_77480.label(text='         These effects are destructive', icon_value=0)
        box_10D06.label(text='Set Live Effects to:', icon_value=0)
        box_10D06.prop(self, 'sna_set_live_effects_to', text='', icon_value=0, emboss=True)
        box_10D06.prop(self, 'sna_apply_subdivision', text='Apply Subdivisions', icon_value=0, emboss=True, toggle=False)
        if self.sna_apply_subdivision:
            col_A5DE0 = box_10D06.column(heading='', align=False)
            col_A5DE0.alert = False
            col_A5DE0.enabled = True
            col_A5DE0.active = True
            col_A5DE0.use_property_split = False
            col_A5DE0.use_property_decorate = False
            col_A5DE0.scale_x = 1.0
            col_A5DE0.scale_y = 1.0
            col_A5DE0.alignment = 'Expand'.upper()
            col_A5DE0.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_7FC90 = col_A5DE0.box()
            box_7FC90.alert = False
            box_7FC90.enabled = True
            box_7FC90.active = True
            box_7FC90.use_property_split = False
            box_7FC90.use_property_decorate = False
            box_7FC90.alignment = 'Expand'.upper()
            box_7FC90.scale_x = 1.0
            box_7FC90.scale_y = 1.0
            if not True: box_7FC90.operator_context = "EXEC_DEFAULT"
            box_7FC90.label(text='This act is destructive', icon_value=string_to_icon('TRIA_RIGHT'))
            box_7FC90.label(text='Select will take longer with higher face counts', icon_value=string_to_icon('TRIA_RIGHT'))
            box_7FC90.label(text='Other modifiers will not be applied', icon_value=string_to_icon('TRIA_RIGHT'))
            box_ABABF = col_A5DE0.box()
            box_ABABF.alert = False
            box_ABABF.enabled = True
            box_ABABF.active = True
            box_ABABF.use_property_split = False
            box_ABABF.use_property_decorate = False
            box_ABABF.alignment = 'Expand'.upper()
            box_ABABF.scale_x = 1.0
            box_ABABF.scale_y = 1.0
            if not True: box_ABABF.operator_context = "EXEC_DEFAULT"
            box_ABABF.label(text='Base face count =' + ' ' + str(len(bpy.context.view_layer.objects.active.data.polygons)), icon_value=0)
            box_ABABF.label(text='Face count with subdivisions + other modifiers =' + ' ' + str(edit_by_colourfunctionedit_effects['sna_evaluatedfacecount']), icon_value=0)

    def invoke(self, context, event):
        bm_A0AA9 = bmesh.new()
        if bpy.context.view_layer.objects.active:
            if bpy.context.view_layer.objects.active.mode == 'EDIT' and False:
                bm_A0AA9 = bmesh.from_edit_mesh(bpy.context.view_layer.objects.active.data)
            else:
                if True:
                    dg = bpy.context.evaluated_depsgraph_get()
                    bm_A0AA9.from_mesh(bpy.context.view_layer.objects.active.evaluated_get(dg).to_mesh())
                else:
                    bm_A0AA9.from_mesh(bpy.context.view_layer.objects.active.data)
        if False:
            bm_A0AA9.transform(bpy.context.view_layer.objects.active.matrix_world)
        bm_A0AA9.verts.ensure_lookup_table()
        bm_A0AA9.faces.ensure_lookup_table()
        bm_A0AA9.edges.ensure_lookup_table()
        edit_by_colourfunctionedit_effects['sna_evaluatedfacecount'] = len(bm_A0AA9.faces)
        return context.window_manager.invoke_props_dialog(self, width=500)


def sna_live_effects_function_interface_5A08A(layout_function, ):
    layout_function.label(text='Live Effects', icon_value=string_to_icon('RADIOBUT_ON'))
    box_F7F47 = layout_function.box()
    box_F7F47.alert = True
    box_F7F47.enabled = True
    box_F7F47.active = True
    box_F7F47.use_property_split = False
    box_F7F47.use_property_decorate = False
    box_F7F47.alignment = 'Expand'.upper()
    box_F7F47.scale_x = 1.0
    box_F7F47.scale_y = 1.0
    if not True: box_F7F47.operator_context = "EXEC_DEFAULT"
    box_F7F47.prop(bpy.context.view_layer.objects.active, 'sna_ebc_live_effects_proxy_switch', text='', icon_value=0, emboss=True)
    if ((bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 0) or (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 1)):
        pass
    else:
        col_6723E = box_F7F47.column(heading='', align=False)
        col_6723E.alert = False
        col_6723E.enabled = True
        col_6723E.active = True
        col_6723E.use_property_split = False
        col_6723E.use_property_decorate = False
        col_6723E.scale_x = 1.0
        col_6723E.scale_y = 1.0
        col_6723E.alignment = 'Expand'.upper()
        col_6723E.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        if ((bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 2) or (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 4)):
            attr_DAD0F = '["' + str('Socket_22' + '"]') 
            col_6723E.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_DAD0F, text='Smooth Iterations', icon_value=0, emboss=True)
        if ((bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 3) or (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 4)):
            col_A135B = col_6723E.column(heading='', align=False)
            col_A135B.alert = False
            col_A135B.enabled = True
            col_A135B.active = True
            col_A135B.use_property_split = False
            col_A135B.use_property_decorate = False
            col_A135B.scale_x = 1.0
            col_A135B.scale_y = 1.0
            col_A135B.alignment = 'Expand'.upper()
            col_A135B.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            col_A135B.prop_search(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], '["Socket_26"]', bpy.data, 'materials', text='Material', icon='NONE')


def sna_retopo_loops_function_interface_61CF5(layout_function, ):
    layout_function.label(text='Retopo Loops', icon_value=string_to_icon('RADIOBUT_ON'))
    box_BA276 = layout_function.box()
    box_BA276.alert = False
    box_BA276.enabled = True
    box_BA276.active = True
    box_BA276.use_property_split = False
    box_BA276.use_property_decorate = False
    box_BA276.alignment = 'Expand'.upper()
    box_BA276.scale_x = 1.0
    box_BA276.scale_y = 1.0
    if not True: box_BA276.operator_context = "EXEC_DEFAULT"
    box_BA276.label(text='Adjust', icon_value=0)
    box_BA276.prop_search(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], '["Socket_63"]', bpy.data, 'materials', text='Material', icon='NONE')
    attr_A89E4 = '["' + str('Socket_62' + '"]') 
    box_BA276.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_A89E4, text='Preview With Base', icon_value=0, emboss=True, toggle=True)
    attr_0282E = '["' + str('Socket_57' + '"]') 
    box_BA276.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_0282E, text='Loop Resolution', icon_value=0, emboss=True, toggle=True)
    attr_14B05 = '["' + str('Socket_66' + '"]') 
    box_BA276.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_14B05, text='Smooth Loops', icon_value=0, emboss=True)
    attr_277B1 = '["' + str('Socket_58' + '"]') 
    box_BA276.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_277B1, text='Loop Width', icon_value=0, emboss=True)
    attr_AAB84 = '["' + str('Socket_61' + '"]') 
    box_BA276.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_AAB84, text='Surface Offset', icon_value=0, emboss=True)
    attr_A49F0 = '["' + str('Socket_60' + '"]') 
    box_BA276.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_A49F0, text='Shrinkwrap', icon_value=0, emboss=True, toggle=True)
    box_8D5ED = box_BA276.box()
    box_8D5ED.alert = False
    box_8D5ED.enabled = True
    box_8D5ED.active = True
    box_8D5ED.use_property_split = False
    box_8D5ED.use_property_decorate = False
    box_8D5ED.alignment = 'Expand'.upper()
    box_8D5ED.scale_x = 1.0
    box_8D5ED.scale_y = 1.0
    if not True: box_8D5ED.operator_context = "EXEC_DEFAULT"
    box_8D5ED.label(text='Clean Up', icon_value=0)
    attr_942EF = '["' + str('Socket_64' + '"]') 
    box_8D5ED.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_942EF, text='Preview Curve', icon_value=0, emboss=True, toggle=True)
    attr_E6119 = '["' + str('Socket_65' + '"]') 
    box_8D5ED.prop(bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN'], attr_E6119, text='Remove Shorter Than:', icon_value=0, emboss=True)
    box_408A8 = box_BA276.box()
    box_408A8.alert = False
    box_408A8.enabled = True
    box_408A8.active = True
    box_408A8.use_property_split = False
    box_408A8.use_property_decorate = False
    box_408A8.alignment = 'Expand'.upper()
    box_408A8.scale_x = 1.0
    box_408A8.scale_y = 1.0
    if not True: box_408A8.operator_context = "EXEC_DEFAULT"
    op = box_408A8.operator('sna.apply_retopo_loops_7ea68', text='Apply Loops', icon_value=0, emboss=True, depress=False)
    op.sna_set_originals_effects = 'Set Material'
    op.sna_add_shrinkwrap_and_subdiv = True


class SNA_OT_Apply_Retopo_Loops_7Ea68(bpy.types.Operator):
    bl_idname = "sna.apply_retopo_loops_7ea68"
    bl_label = "Apply Retopo Loops"
    bl_description = "Applies the retopology loops as a new object."
    bl_options = {"REGISTER", "UNDO"}

    def sna_set_originals_effects_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_set_originals_effects: bpy.props.EnumProperty(name='Set Originals Effects', description='', items=[('Set Material', 'Set Material', '', 0, 0), ('Retopo Loops', 'Retopo Loops', '', 0, 1), ('None', 'None', '', 0, 2)])
    sna_add_shrinkwrap_and_subdiv: bpy.props.BoolProperty(name='Add Shrinkwrap and Subdiv', description='', default=True)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_active_object'] = bpy.context.view_layer.objects.active
        source_obj_name = bpy.context.view_layer.objects.active.name
        offset_x = 0.0
        new_object_name = None
        # Input variables
        #source_obj_name = "Cube"  # Change this to your object's name
        #offset_x = 0.0  # Input float variable for X offset
        # Get the source object
        source_obj = bpy.data.objects.get(source_obj_name)
        # Check if the object exists
        if source_obj:
            # Create a copy of the object
            new_obj = source_obj.copy()
            new_obj.data = source_obj.data.copy()
            # Link the new object to the scene
            bpy.context.scene.collection.objects.link(new_obj)
            # Apply the offset if any
            new_obj.location.x += offset_x
            # Store the new object's name in a variable
            new_object_name = new_obj.name
        else:
            new_object_name = "ERROR: Source object not found"
        # Output the new object's name (this will be captured by Serpens)
        print(new_object_name)
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_retopo_object'] = bpy.data.objects[new_object_name]
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_retopo_object'].modifiers['KIRI_Edit_By_Colour_GN']['Socket_62'] = False
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_retopo_object'].modifiers['KIRI_Edit_By_Colour_GN']['Socket_64'] = False
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_active_object'].modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = ((5 if (self.sna_set_originals_effects != 'None') else 0) if (self.sna_set_originals_effects != 'Set Material') else 3)
        bpy.context.view_layer.objects.active.sna_ebc_live_effects_proxy_switch = self.sna_set_originals_effects
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_active_object'].update_tag(refresh={'DATA'}, )
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_retopo_object'].update_tag(refresh={'DATA'}, )
        if bpy.context and bpy.context.screen:
            for a in bpy.context.screen.areas:
                a.tag_redraw()
        for i_CD250 in range(len(bpy.context.scene.objects)):
            bpy.context.scene.objects[i_CD250].select_set(state=False, view_layer=bpy.context.view_layer, )
        edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_retopo_object'].select_set(state=True, view_layer=bpy.context.view_layer, )
        bpy.context.view_layer.objects.active = edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_retopo_object']
        bpy.ops.object.modifier_apply('INVOKE_DEFAULT', modifier='KIRI_Edit_By_Colour_GN')
        if self.sna_add_shrinkwrap_and_subdiv:
            modifier_8FCC1 = bpy.context.view_layer.objects.active.modifiers.new(name='EBC Subdiv', type='SUBSURF', )
            modifier_63518 = bpy.context.view_layer.objects.active.modifiers.new(name='EBC Shrinkwrap', type='SHRINKWRAP', )
            modifier_63518.target = edit_by_colourfunctionretopo_loops['sna_ebc_temp_store_active_object']
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_F96AC = layout.box()
        box_F96AC.alert = False
        box_F96AC.enabled = True
        box_F96AC.active = True
        box_F96AC.use_property_split = False
        box_F96AC.use_property_decorate = False
        box_F96AC.alignment = 'Expand'.upper()
        box_F96AC.scale_x = 1.0
        box_F96AC.scale_y = 1.0
        if not True: box_F96AC.operator_context = "EXEC_DEFAULT"
        box_F96AC.label(text='Apply Loops Settings', icon_value=0)
        box_F96AC.label(text="Set Original's Effects To:", icon_value=0)
        box_F96AC.prop(self, 'sna_set_originals_effects', text='', icon_value=0, emboss=True)
        box_F96AC.prop(self, 'sna_add_shrinkwrap_and_subdiv', text='Add Shrinkwrap and Subdiv', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)


def sna_sculpt_function_interface_92592(layout_function, ):
    layout_function.label(text='Sculpt', icon_value=string_to_icon('RADIOBUT_ON'))
    box_21A98 = layout_function.box()
    box_21A98.alert = False
    box_21A98.enabled = True
    box_21A98.active = True
    box_21A98.use_property_split = False
    box_21A98.use_property_decorate = False
    box_21A98.alignment = 'Expand'.upper()
    box_21A98.scale_x = 1.0
    box_21A98.scale_y = 1.0
    if not True: box_21A98.operator_context = "EXEC_DEFAULT"
    if 'OBJECT'==bpy.context.mode:
        op = box_21A98.operator('sna.selection_to_face_sets_69a50', text='Selection to Face Sets', icon_value=0, emboss=True, depress=False)
        op.sna_apply_subdivision = False
        op.sna_set_live_effects_to = 'None'
    if (bpy.context.mode == 'SCULPT'):
        col_CC812 = box_21A98.column(heading='', align=False)
        col_CC812.alert = False
        col_CC812.enabled = True
        col_CC812.active = True
        col_CC812.use_property_split = False
        col_CC812.use_property_decorate = False
        col_CC812.scale_x = 1.0
        col_CC812.scale_y = 1.0
        col_CC812.alignment = 'Expand'.upper()
        col_CC812.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        col_CC812.prop(bpy.context.scene.tool_settings.sculpt, 'use_automasking_face_sets', text='Auto Mask By Face Sets', icon_value=0, emboss=True, toggle=True)
        op = col_CC812.operator('sculpt.face_sets_create', text='Face Set From Visible (Clear)', icon_value=0, emboss=True, depress=False)
        op.mode = 'VISIBLE'
        box_98238 = col_CC812.box()
        box_98238.alert = False
        box_98238.enabled = True
        box_98238.active = True
        box_98238.use_property_split = False
        box_98238.use_property_decorate = False
        box_98238.alignment = 'Expand'.upper()
        box_98238.scale_x = 1.0
        box_98238.scale_y = 1.0
        if not True: box_98238.operator_context = "EXEC_DEFAULT"
        box_98238.label(text='Grow Face Set = Ctrl + W', icon_value=0)
        box_98238.label(text='Shrink Face Set = Ctrl + Alt + W', icon_value=0)


class SNA_OT_Selection_To_Face_Sets_69A50(bpy.types.Operator):
    bl_idname = "sna.selection_to_face_sets_69a50"
    bl_label = "Selection to Face Sets"
    bl_description = "Enters sculpting mode and creates Face Sets based on the Edit By Colour selection."
    bl_options = {"REGISTER", "UNDO"}
    sna_apply_subdivision: bpy.props.BoolProperty(name='Apply Subdivision?', description='', default=False)

    def sna_set_live_effects_to_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_set_live_effects_to: bpy.props.EnumProperty(name='Set Live Effects to', description='', items=[('None', 'None', '', 0, 0), ('Set Material', 'Set Material', '', 0, 1), ('No Change', 'No Change', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        shade_mode = 'SOLID'  # Options: 'SOLID', 'RENDERED', 'MATERIAL', 'WIREFRAME'
        # Loop through all screens
        for screen in bpy.data.screens:
            # Loop through all areas in each screen
            for area in screen.areas:
                # Check if the area is a 3D View
                if area.type == 'VIEW_3D':
                    # Get the 3D viewport's shading settings
                    space = area.spaces[0]
                    # Set the shading type
                    space.shading.type = shade_mode
        sna_ebc_select_function_execute_82A8F(self.sna_apply_subdivision, self.sna_set_live_effects_to)
        bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='SCULPT')
        bpy.ops.sculpt.face_sets_create('INVOKE_DEFAULT', mode='SELECTION')
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_C5083 = layout.box()
        box_C5083.alert = False
        box_C5083.enabled = True
        box_C5083.active = True
        box_C5083.use_property_split = False
        box_C5083.use_property_decorate = False
        box_C5083.alignment = 'Expand'.upper()
        box_C5083.scale_x = 1.0
        box_C5083.scale_y = 1.0
        if not True: box_C5083.operator_context = "EXEC_DEFAULT"
        box_78E53 = box_C5083.box()
        box_78E53.alert = True
        box_78E53.enabled = True
        box_78E53.active = True
        box_78E53.use_property_split = False
        box_78E53.use_property_decorate = False
        box_78E53.alignment = 'Expand'.upper()
        box_78E53.scale_x = 1.0
        box_78E53.scale_y = 1.0
        if not True: box_78E53.operator_context = "EXEC_DEFAULT"
        box_78E53.label(text='The Edit By Colour modifier will be applied, then re-added', icon_value=string_to_icon('INFO'))
        box_78E53.label(text='         These effects are destructive', icon_value=0)
        box_C5083.label(text='Set Live Effects to:', icon_value=0)
        box_C5083.prop(self, 'sna_set_live_effects_to', text='', icon_value=0, emboss=True)
        box_C5083.prop(self, 'sna_apply_subdivision', text='Apply Subdivisions', icon_value=0, emboss=True, toggle=False)
        if self.sna_apply_subdivision:
            col_68F58 = box_C5083.column(heading='', align=False)
            col_68F58.alert = False
            col_68F58.enabled = True
            col_68F58.active = True
            col_68F58.use_property_split = False
            col_68F58.use_property_decorate = False
            col_68F58.scale_x = 1.0
            col_68F58.scale_y = 1.0
            col_68F58.alignment = 'Expand'.upper()
            col_68F58.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_8B5B8 = col_68F58.box()
            box_8B5B8.alert = False
            box_8B5B8.enabled = True
            box_8B5B8.active = True
            box_8B5B8.use_property_split = False
            box_8B5B8.use_property_decorate = False
            box_8B5B8.alignment = 'Expand'.upper()
            box_8B5B8.scale_x = 1.0
            box_8B5B8.scale_y = 1.0
            if not True: box_8B5B8.operator_context = "EXEC_DEFAULT"
            box_8B5B8.label(text='This act is destructive', icon_value=string_to_icon('TRIA_RIGHT'))
            box_8B5B8.label(text='Select will take longer with higher face counts', icon_value=string_to_icon('TRIA_RIGHT'))
            box_8B5B8.label(text='Other modifiers will not be applied', icon_value=string_to_icon('TRIA_RIGHT'))
            box_7A6F5 = col_68F58.box()
            box_7A6F5.alert = False
            box_7A6F5.enabled = True
            box_7A6F5.active = True
            box_7A6F5.use_property_split = False
            box_7A6F5.use_property_decorate = False
            box_7A6F5.alignment = 'Expand'.upper()
            box_7A6F5.scale_x = 1.0
            box_7A6F5.scale_y = 1.0
            if not True: box_7A6F5.operator_context = "EXEC_DEFAULT"
            box_7A6F5.label(text='Base face count =' + ' ' + str(len(bpy.context.view_layer.objects.active.data.polygons)), icon_value=0)
            box_7A6F5.label(text='Face count with subdivisions + other modifiers =' + ' ' + str(edit_by_colourfunctionedit_effects['sna_evaluatedfacecount']), icon_value=0)

    def invoke(self, context, event):
        bm_3B63D = bmesh.new()
        if bpy.context.view_layer.objects.active:
            if bpy.context.view_layer.objects.active.mode == 'EDIT' and False:
                bm_3B63D = bmesh.from_edit_mesh(bpy.context.view_layer.objects.active.data)
            else:
                if True:
                    dg = bpy.context.evaluated_depsgraph_get()
                    bm_3B63D.from_mesh(bpy.context.view_layer.objects.active.evaluated_get(dg).to_mesh())
                else:
                    bm_3B63D.from_mesh(bpy.context.view_layer.objects.active.data)
        if False:
            bm_3B63D.transform(bpy.context.view_layer.objects.active.matrix_world)
        bm_3B63D.verts.ensure_lookup_table()
        bm_3B63D.faces.ensure_lookup_table()
        bm_3B63D.edges.ensure_lookup_table()
        edit_by_colourfunctionedit_effects['sna_evaluatedfacecount'] = len(bm_3B63D.faces)
        return context.window_manager.invoke_props_dialog(self, width=500)


class SNA_PT_EDIT_BY_COLOUR_BY_KIRI_ENGINE_955BF(bpy.types.Panel):
    bl_label = 'Edit By Colour by KIRI Engine'
    bl_idname = 'SNA_PT_EDIT_BY_COLOUR_BY_KIRI_ENGINE_955BF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_category = 'Edit By Colour'
    bl_order = 0
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout
        layout.template_icon(icon_value=load_preview_icon(os.path.join(os.path.dirname(__file__), 'assets', 'kiriengine icon.png')), scale=0.0)

    def draw(self, context):
        layout = self.layout
        layout_function = layout
        sna_edit_by_colour_functions_function_interface_7277A(layout_function, )
        layout.separator(factor=1.0)
        layout_function = layout
        sna_documentation_interface_function_A1B59(layout_function, )
        layout.separator(factor=1.0)
        layout_function = layout
        sna_about_and_external_links_interface_function_8E1B8(layout_function, )
        layout.separator(factor=1.0)
        sna_palette_split_interface(layout)
        layout.separator(factor=1.0)
        sna_auto_palette_interface(layout)
        layout.separator(factor=1.0)
        sna_voxel_block_remesh_interface(layout)


class SNA_OT_Open_Edit_By_Colour_Documentation_1Eac5(bpy.types.Operator):
    bl_idname = "sna.open_edit_by_colour_documentation_1eac5"
    bl_label = "Open Edit By Colour Documentation"
    bl_description = "Opens a web browser"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = 'https://www.kiriengine.app/blender-addon/edit-by-colour'
        # Open the web browser and go to the specified URL
        webbrowser.open(url)
        print(f"Opening web browser to {url}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_documentation_interface_function_A1B59(layout_function, ):
    box_74304 = layout_function.box()
    box_74304.alert = False
    box_74304.enabled = True
    box_74304.active = True
    box_74304.use_property_split = False
    box_74304.use_property_decorate = False
    box_74304.alignment = 'Expand'.upper()
    box_74304.scale_x = 1.0
    box_74304.scale_y = 1.0
    if not True: box_74304.operator_context = "EXEC_DEFAULT"
    op = box_74304.operator('sna.open_edit_by_colour_documentation_1eac5', text='Documentation', icon_value=0, emboss=True, depress=False)
    op = box_74304.operator('sna.open_edit_by_colour_tutorial_video_a4fe6', text='Tutorial Video', icon_value=0, emboss=True, depress=False)


class SNA_OT_Open_Edit_By_Colour_Tutorial_Video_A4Fe6(bpy.types.Operator):
    bl_idname = "sna.open_edit_by_colour_tutorial_video_a4fe6"
    bl_label = "Open Edit By Colour Tutorial Video"
    bl_description = "Opens a web browser"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = 'https://youtu.be/RRAivqua1rc'
        # Open the web browser and go to the specified URL
        webbrowser.open(url)
        print(f"Opening web browser to {url}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_edit_by_colour_functions_function_interface_7277A(layout_function, ):
    if (bpy.context.view_layer.objects.active == None):
        pass
    else:
        box_5BFA9 = layout_function.box()
        box_5BFA9.alert = False
        box_5BFA9.enabled = True
        box_5BFA9.active = True
        box_5BFA9.use_property_split = False
        box_5BFA9.use_property_decorate = False
        box_5BFA9.alignment = 'Expand'.upper()
        box_5BFA9.scale_x = 1.0
        box_5BFA9.scale_y = 1.0
        if not True: box_5BFA9.operator_context = "EXEC_DEFAULT"
        box_DC03C = box_5BFA9.box()
        box_DC03C.alert = False
        box_DC03C.enabled = True
        box_DC03C.active = True
        box_DC03C.use_property_split = False
        box_DC03C.use_property_decorate = False
        box_DC03C.alignment = 'Expand'.upper()
        box_DC03C.scale_x = 1.0
        box_DC03C.scale_y = 1.0
        if not True: box_DC03C.operator_context = "EXEC_DEFAULT"
        layout_function = box_DC03C
        sna_add_remove_modifier_function_interface_02DDA(layout_function, )
        if (property_exists("bpy.context.view_layer.objects.active.modifiers", globals(), locals()) and 'KIRI_Edit_By_Colour_GN' in bpy.context.view_layer.objects.active.modifiers):
            box_49EC8 = box_5BFA9.box()
            box_49EC8.alert = False
            box_49EC8.enabled = True
            box_49EC8.active = True
            box_49EC8.use_property_split = False
            box_49EC8.use_property_decorate = False
            box_49EC8.alignment = 'Expand'.upper()
            box_49EC8.scale_x = 1.0
            box_49EC8.scale_y = 1.0
            if not True: box_49EC8.operator_context = "EXEC_DEFAULT"
            layout_function = box_49EC8
            sna_active_object_properties_function_interface_3951A(layout_function, )
        if (property_exists("bpy.context.view_layer.objects.active.modifiers", globals(), locals()) and 'KIRI_Edit_By_Colour_GN' in bpy.context.view_layer.objects.active.modifiers):
            if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4'] == None):
                pass
            else:
                col_2BD89 = box_5BFA9.column(heading='', align=False)
                col_2BD89.alert = False
                col_2BD89.enabled = True
                col_2BD89.active = True
                col_2BD89.use_property_split = False
                col_2BD89.use_property_decorate = False
                col_2BD89.scale_x = 1.0
                col_2BD89.scale_y = 1.0
                col_2BD89.alignment = 'Expand'.upper()
                col_2BD89.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                box_3C86E = col_2BD89.box()
                box_3C86E.alert = False
                box_3C86E.enabled = True
                box_3C86E.active = True
                box_3C86E.use_property_split = False
                box_3C86E.use_property_decorate = False
                box_3C86E.alignment = 'Expand'.upper()
                box_3C86E.scale_x = 1.0
                box_3C86E.scale_y = 1.0
                if not True: box_3C86E.operator_context = "EXEC_DEFAULT"
                layout_function = box_3C86E
                sna_live_effects_function_interface_5A08A(layout_function, )
                if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 5):
                    box_4AEEA = col_2BD89.box()
                    box_4AEEA.alert = False
                    box_4AEEA.enabled = True
                    box_4AEEA.active = True
                    box_4AEEA.use_property_split = False
                    box_4AEEA.use_property_decorate = False
                    box_4AEEA.alignment = 'Expand'.upper()
                    box_4AEEA.scale_x = 1.0
                    box_4AEEA.scale_y = 1.0
                    if not True: box_4AEEA.operator_context = "EXEC_DEFAULT"
                    grid_31ECB = box_4AEEA.grid_flow(columns=2, row_major=False, even_columns=False, even_rows=False, align=False)
                    grid_31ECB.enabled = True
                    grid_31ECB.active = True
                    grid_31ECB.use_property_split = False
                    grid_31ECB.use_property_decorate = False
                    grid_31ECB.alignment = 'Expand'.upper()
                    grid_31ECB.scale_x = 1.0
                    grid_31ECB.scale_y = 1.0
                    if not True: grid_31ECB.operator_context = "EXEC_DEFAULT"
                    grid_31ECB.prop(bpy.context.scene, 'sna_ebc_active_menu_retopo_loops', text=bpy.context.scene.sna_ebc_active_menu_retopo_loops, icon_value=0, emboss=True, expand=True)
                else:
                    box_594E9 = col_2BD89.box()
                    box_594E9.alert = False
                    box_594E9.enabled = True
                    box_594E9.active = True
                    box_594E9.use_property_split = False
                    box_594E9.use_property_decorate = False
                    box_594E9.alignment = 'Expand'.upper()
                    box_594E9.scale_x = 1.0
                    box_594E9.scale_y = 1.0
                    if not True: box_594E9.operator_context = "EXEC_DEFAULT"
                    grid_40E66 = box_594E9.grid_flow(columns=2, row_major=False, even_columns=False, even_rows=False, align=False)
                    grid_40E66.enabled = True
                    grid_40E66.active = True
                    grid_40E66.use_property_split = False
                    grid_40E66.use_property_decorate = False
                    grid_40E66.alignment = 'Expand'.upper()
                    grid_40E66.scale_x = 1.0
                    grid_40E66.scale_y = 1.0
                    if not True: grid_40E66.operator_context = "EXEC_DEFAULT"
                    grid_40E66.prop(bpy.context.scene, 'sna_ebc_active_menu_full', text=bpy.context.scene.sna_ebc_active_menu_full, icon_value=0, emboss=True, expand=True)
                if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 5):
                    if (bpy.context.scene.sna_ebc_active_menu_retopo_loops == 'Colour Selection'):
                        box_06706 = col_2BD89.box()
                        box_06706.alert = False
                        box_06706.enabled = True
                        box_06706.active = True
                        box_06706.use_property_split = False
                        box_06706.use_property_decorate = False
                        box_06706.alignment = 'Expand'.upper()
                        box_06706.scale_x = 1.0
                        box_06706.scale_y = 1.0
                        if not True: box_06706.operator_context = "EXEC_DEFAULT"
                        layout_function = box_06706
                        sna_adjust_selection_function_interface_541E9(layout_function, )
                else:
                    if (bpy.context.scene.sna_ebc_active_menu_full == 'Colour Selection'):
                        box_3F66F = col_2BD89.box()
                        box_3F66F.alert = False
                        box_3F66F.enabled = True
                        box_3F66F.active = True
                        box_3F66F.use_property_split = False
                        box_3F66F.use_property_decorate = False
                        box_3F66F.alignment = 'Expand'.upper()
                        box_3F66F.scale_x = 1.0
                        box_3F66F.scale_y = 1.0
                        if not True: box_3F66F.operator_context = "EXEC_DEFAULT"
                        layout_function = box_3F66F
                        sna_adjust_selection_function_interface_541E9(layout_function, )
                if 'OBJECT'==bpy.context.mode:
                    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 5):
                        pass
                    else:
                        if (bpy.context.scene.sna_ebc_active_menu_full == 'Edit Mesh'):
                            box_84303 = col_2BD89.box()
                            box_84303.alert = False
                            box_84303.enabled = True
                            box_84303.active = True
                            box_84303.use_property_split = False
                            box_84303.use_property_decorate = False
                            box_84303.alignment = 'Expand'.upper()
                            box_84303.scale_x = 1.0
                            box_84303.scale_y = 1.0
                            if not True: box_84303.operator_context = "EXEC_DEFAULT"
                            layout_function = box_84303
                            sna_edit_effects_function_interface_6C02F(layout_function, )
                if 'OBJECT'==bpy.context.mode:
                    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 5):
                        pass
                    else:
                        if (bpy.context.scene.sna_ebc_active_menu_full == 'Texture'):
                            box_16002 = col_2BD89.box()
                            box_16002.alert = False
                            box_16002.enabled = True
                            box_16002.active = True
                            box_16002.use_property_split = False
                            box_16002.use_property_decorate = False
                            box_16002.alignment = 'Expand'.upper()
                            box_16002.scale_x = 1.0
                            box_16002.scale_y = 1.0
                            if not True: box_16002.operator_context = "EXEC_DEFAULT"
                            layout_function = box_16002
                            sna_texture_function_interface_D6644(layout_function, )
                if ('SCULPT'==bpy.context.mode or 'OBJECT'==bpy.context.mode):
                    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 5):
                        pass
                    else:
                        if (bpy.context.scene.sna_ebc_active_menu_full == 'Sculpt'):
                            box_26DF2 = col_2BD89.box()
                            box_26DF2.alert = False
                            box_26DF2.enabled = True
                            box_26DF2.active = True
                            box_26DF2.use_property_split = False
                            box_26DF2.use_property_decorate = False
                            box_26DF2.alignment = 'Expand'.upper()
                            box_26DF2.scale_x = 1.0
                            box_26DF2.scale_y = 1.0
                            if not True: box_26DF2.operator_context = "EXEC_DEFAULT"
                            layout_function = box_26DF2
                            sna_sculpt_function_interface_92592(layout_function, )
                if 'OBJECT'==bpy.context.mode:
                    if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] == 5):
                        if (bpy.context.scene.sna_ebc_active_menu_retopo_loops == 'Retopo Loops'):
                            box_83655 = col_2BD89.box()
                            box_83655.alert = False
                            box_83655.enabled = True
                            box_83655.active = True
                            box_83655.use_property_split = False
                            box_83655.use_property_decorate = False
                            box_83655.alignment = 'Expand'.upper()
                            box_83655.scale_x = 1.0
                            box_83655.scale_y = 1.0
                            if not True: box_83655.operator_context = "EXEC_DEFAULT"
                            layout_function = box_83655
                            sna_retopo_loops_function_interface_61CF5(layout_function, )


class SNA_OT_Ebclaunch_Kiri_Site_D26Bf(bpy.types.Operator):
    bl_idname = "sna.ebclaunch_kiri_site_d26bf"
    bl_label = "EBC-Launch Kiri Site"
    bl_description = "Opens a web browser"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = 'https://www.kiriengine.com/'
        # Open the web browser and go to the specified URL
        webbrowser.open(url)
        print(f"Opening web browser to {url}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_about_and_external_links_interface_function_8E1B8(layout_function, ):
    box_0CFD3 = layout_function.box()
    box_0CFD3.alert = False
    box_0CFD3.enabled = True
    box_0CFD3.active = True
    box_0CFD3.use_property_split = False
    box_0CFD3.use_property_decorate = False
    box_0CFD3.alignment = 'Expand'.upper()
    box_0CFD3.scale_x = 1.0
    box_0CFD3.scale_y = 1.0
    if not True: box_0CFD3.operator_context = "EXEC_DEFAULT"
    op = box_0CFD3.operator('sna.ebclaunch_blender_market_77f72', text='See All Add-ons on Blender Market', icon_value=0, emboss=True, depress=False)
    op = box_0CFD3.operator('sna.ebclaunch_kiri_site_d26bf', text='Learn More About KIRI Engine', icon_value=0, emboss=True, depress=False)


class SNA_OT_Ebclaunch_Blender_Market_77F72(bpy.types.Operator):
    bl_idname = "sna.ebclaunch_blender_market_77f72"
    bl_label = "EBC-Launch Blender Market"
    bl_description = "Opens a web browser"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        url = 'https://blendermarket.com/creators/blender-addon-from-kiri-engine'
        # Open the web browser and go to the specified URL
        webbrowser.open(url)
        print(f"Opening web browser to {url}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


def sna_texture_function_interface_D6644(layout_function, ):
    layout_function.label(text='Texture', icon_value=string_to_icon('RADIOBUT_ON'))
    layout_function = layout_function
    sna_shader_attributes_function_interface_0EC7B(layout_function, )
    layout_function = layout_function
    sna_bake_patch_function_interface_834B3(layout_function, )
    layout_function = layout_function
    sna_bake_combined_function_interface_4566F(layout_function, )


class SNA_OT_Add_Ebc_Attribute_To_Selected_Material_3F5C9(bpy.types.Operator):
    bl_idname = "sna.add_ebc_attribute_to_selected_material_3f5c9"
    bl_label = "Add EBC attribute to selected material"
    bl_description = "Applies the EBC selection as an attribute and adds an attribute node to the selected material."
    bl_options = {"REGISTER", "UNDO"}
    sna_apply_subdivision: bpy.props.BoolProperty(name='Apply Subdivision?', description='', default=False)

    def sna_set_live_effects_to_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_set_live_effects_to: bpy.props.EnumProperty(name='Set Live Effects to:', description='', items=[('None', 'None', '', 0, 0), ('Set Material', 'Set Material', '', 0, 1), ('No Change', 'No Change', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if (bpy.context.scene.sna_ebc_base_material == None):
            self.report({'ERROR'}, message='No material assigned')
        else:
            sna_ebc_select_function_execute_82A8F(self.sna_apply_subdivision, self.sna_set_live_effects_to)
            bpy.ops.object.mode_set('INVOKE_DEFAULT', mode='OBJECT')
            node_281D0 = bpy.context.scene.sna_ebc_base_material.node_tree.nodes.new(type='ShaderNodeAttribute', )
            node_281D0.attribute_name = 'EBC_Selection'
            if (property_exists("bpy.context.view_layer.objects.active.active_material.node_tree.nodes", globals(), locals()) and 'Material Output' in bpy.context.view_layer.objects.active.active_material.node_tree.nodes):
                node_281D0.location = (bpy.context.scene.sna_ebc_base_material.node_tree.nodes['Material Output'].location[0], float(bpy.context.scene.sna_ebc_base_material.node_tree.nodes['Material Output'].location[1] + 200.0))
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_85BF0 = layout.box()
        box_85BF0.alert = False
        box_85BF0.enabled = True
        box_85BF0.active = True
        box_85BF0.use_property_split = False
        box_85BF0.use_property_decorate = False
        box_85BF0.alignment = 'Expand'.upper()
        box_85BF0.scale_x = 1.0
        box_85BF0.scale_y = 1.0
        if not True: box_85BF0.operator_context = "EXEC_DEFAULT"
        box_7232E = box_85BF0.box()
        box_7232E.alert = False
        box_7232E.enabled = True
        box_7232E.active = True
        box_7232E.use_property_split = False
        box_7232E.use_property_decorate = False
        box_7232E.alignment = 'Expand'.upper()
        box_7232E.scale_x = 1.0
        box_7232E.scale_y = 1.0
        if not True: box_7232E.operator_context = "EXEC_DEFAULT"
        box_971AA = box_7232E.box()
        box_971AA.alert = True
        box_971AA.enabled = True
        box_971AA.active = True
        box_971AA.use_property_split = False
        box_971AA.use_property_decorate = False
        box_971AA.alignment = 'Expand'.upper()
        box_971AA.scale_x = 1.0
        box_971AA.scale_y = 1.0
        if not True: box_971AA.operator_context = "EXEC_DEFAULT"
        box_971AA.label(text='The Edit By Colour modifier will be applied, then re-added', icon_value=string_to_icon('INFO'))
        box_971AA.label(text='         These effects are destructive', icon_value=0)
        box_7232E.label(text='Set Live Effects to:', icon_value=0)
        box_7232E.prop(self, 'sna_set_live_effects_to', text='', icon_value=0, emboss=True)
        box_7232E.prop(self, 'sna_apply_subdivision', text='Apply Subdivisions', icon_value=0, emboss=True, toggle=False)
        if self.sna_apply_subdivision:
            col_BBE4C = box_7232E.column(heading='', align=False)
            col_BBE4C.alert = False
            col_BBE4C.enabled = True
            col_BBE4C.active = True
            col_BBE4C.use_property_split = False
            col_BBE4C.use_property_decorate = False
            col_BBE4C.scale_x = 1.0
            col_BBE4C.scale_y = 1.0
            col_BBE4C.alignment = 'Expand'.upper()
            col_BBE4C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            box_CDF6B = col_BBE4C.box()
            box_CDF6B.alert = False
            box_CDF6B.enabled = True
            box_CDF6B.active = True
            box_CDF6B.use_property_split = False
            box_CDF6B.use_property_decorate = False
            box_CDF6B.alignment = 'Expand'.upper()
            box_CDF6B.scale_x = 1.0
            box_CDF6B.scale_y = 1.0
            if not True: box_CDF6B.operator_context = "EXEC_DEFAULT"
            box_CDF6B.label(text='This act is destructive', icon_value=string_to_icon('TRIA_RIGHT'))
            box_CDF6B.label(text='Select will take longer with higher face counts', icon_value=string_to_icon('TRIA_RIGHT'))
            box_CDF6B.label(text='Other modifiers will not be applied', icon_value=string_to_icon('TRIA_RIGHT'))
            box_F46BD = col_BBE4C.box()
            box_F46BD.alert = False
            box_F46BD.enabled = True
            box_F46BD.active = True
            box_F46BD.use_property_split = False
            box_F46BD.use_property_decorate = False
            box_F46BD.alignment = 'Expand'.upper()
            box_F46BD.scale_x = 1.0
            box_F46BD.scale_y = 1.0
            if not True: box_F46BD.operator_context = "EXEC_DEFAULT"
            box_F46BD.label(text='Base face count =' + ' ' + str(len(bpy.context.view_layer.objects.active.data.polygons)), icon_value=0)
            box_F46BD.label(text='Face count with subdivisions + other modifiers =' + ' ' + str(edit_by_colourfunctionedit_effects['sna_evaluatedfacecount']), icon_value=0)
        box_85BF0.label(text='Shader Attribute Settings', icon_value=0)
        box_29F78 = box_85BF0.box()
        box_29F78.alert = False
        box_29F78.enabled = True
        box_29F78.active = True
        box_29F78.use_property_split = False
        box_29F78.use_property_decorate = False
        box_29F78.alignment = 'Expand'.upper()
        box_29F78.scale_x = 1.0
        box_29F78.scale_y = 1.0
        if not True: box_29F78.operator_context = "EXEC_DEFAULT"
        box_29F78.prop_search(bpy.context.scene, 'sna_ebc_base_material', bpy.data, 'materials', text='Material', icon='NONE')

    def invoke(self, context, event):
        bpy.context.scene.sna_ebc_base_material = bpy.context.view_layer.objects.active.material_slots[0].material
        bm_0D07F = bmesh.new()
        if bpy.context.view_layer.objects.active:
            if bpy.context.view_layer.objects.active.mode == 'EDIT' and False:
                bm_0D07F = bmesh.from_edit_mesh(bpy.context.view_layer.objects.active.data)
            else:
                if True:
                    dg = bpy.context.evaluated_depsgraph_get()
                    bm_0D07F.from_mesh(bpy.context.view_layer.objects.active.evaluated_get(dg).to_mesh())
                else:
                    bm_0D07F.from_mesh(bpy.context.view_layer.objects.active.data)
        if False:
            bm_0D07F.transform(bpy.context.view_layer.objects.active.matrix_world)
        bm_0D07F.verts.ensure_lookup_table()
        bm_0D07F.faces.ensure_lookup_table()
        bm_0D07F.edges.ensure_lookup_table()
        edit_by_colourfunctionedit_effects['sna_evaluatedfacecount'] = len(bm_0D07F.faces)
        return context.window_manager.invoke_props_dialog(self, width=500)


def sna_shader_attributes_function_interface_0EC7B(layout_function, ):
    box_F143E = layout_function.box()
    box_F143E.alert = False
    box_F143E.enabled = True
    box_F143E.active = True
    box_F143E.use_property_split = False
    box_F143E.use_property_decorate = False
    box_F143E.alignment = 'Expand'.upper()
    box_F143E.scale_x = 1.0
    box_F143E.scale_y = 1.0
    if not True: box_F143E.operator_context = "EXEC_DEFAULT"
    box_F143E.label(text='Shader Attributes', icon_value=0)
    if (bpy.context.mode == 'OBJECT'):
        op = box_F143E.operator('sna.add_ebc_attribute_to_selected_material_3f5c9', text='Create Material Attributes', icon_value=0, emboss=True, depress=False)
        op.sna_apply_subdivision = False
        op.sna_set_live_effects_to = 'None'


class SNA_OT_Bake_Set_Material__Original_Dafdb(bpy.types.Operator):
    bl_idname = "sna.bake_set_material__original_dafdb"
    bl_label = "Bake Set Material + Original"
    bl_description = "Bakes all materials currently assigned to the active object."
    bl_options = {"REGISTER", "UNDO"}
    sna_bake_samples: bpy.props.IntProperty(name='Bake Samples', description='', default=10, subtype='NONE', min=1)
    sna_bake_diffuse: bpy.props.BoolProperty(name='Bake Diffuse', description='', default=False)
    sna_bake_roughness: bpy.props.BoolProperty(name='Bake Roughness', description='', default=False)
    sna_bake_normal: bpy.props.BoolProperty(name='Bake Normal', description='', default=False)

    def sna_bake_resolution_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_bake_resolution: bpy.props.EnumProperty(name='Bake Resolution', description='', items=[('1K', '1K', '', 0, 0), ('2K', '2K', '', 0, 1), ('4K', '4K', '', 0, 2), ('8K', '8K', '', 0, 3)])
    sna_apply_subdivision: bpy.props.BoolProperty(name='Apply Subdivision?', description='', default=False)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if ((not self.sna_bake_diffuse) and (not self.sna_bake_roughness) and (not self.sna_bake_normal)):
            self.report({'INFO'}, message='No bake passes selected - no changes made')
        else:
            target_object = bpy.context.view_layer.objects.active
            remove_empty = True
            remove_unused = True
            # REMOVE UNUSED MATERIALS
            # Removes unused material slots from an object (empty slots and slots not used by any polygons)
            #target_object: Object to clean materials from
            #Type: Pointer
            #Pointer: bpy.types.Object
            #Description: Target object to remove unused materials from
            #remove_empty: Remove slots with no material assigned
            #Values: True, False
            #Default: True
            #Description: Whether to remove slots that have no material assigned
            #remove_unused: Remove slots not used by any polygons
            #Values: True, False
            #Default: True
            #Description: Whether to remove slots that aren't used by any faces
            # Input variables
            #target_object = None
            #remove_empty = True
            #remove_unused = True
            # Output variables
            success = False
            error_message = ""
            removed_count = 0
            try:
                print(f"Cleaning materials for object: {target_object.name}")
                initial_slot_count = len(target_object.material_slots)
                print(f"Initial material slots: {initial_slot_count}")
                # First pass: Remove empty slots
                if remove_empty:
                    print("Checking for empty slots...")
                    for i in range(len(target_object.material_slots) - 1, -1, -1):
                        if target_object.material_slots[i].material is None:
                            target_object.data.materials.pop(index=i)
                            print(f"Removed empty slot at index {i}")
                            removed_count += 1
                # Second pass: Remove unused slots
                if remove_unused and hasattr(target_object.data, "polygons"):
                    print("Checking for unused slots...")
                    used_indices = {p.material_index for p in target_object.data.polygons}
                    print(f"Found used material indices: {used_indices}")
                    for i in range(len(target_object.material_slots) - 1, -1, -1):
                        if i not in used_indices:
                            target_object.data.materials.pop(index=i)
                            print(f"Removed unused slot at index {i}")
                            removed_count += 1
                final_slot_count = len(target_object.material_slots)
                print(f"Removed {removed_count} slots total")
                print(f"Final material slot count: {final_slot_count}")
                success = True
            except Exception as e:
                error_message = str(e)
                print(f"Error cleaning materials: {error_message}")
                removed_count = 0
            if self.sna_apply_subdivision:
                pass
            else:
                bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_50'] = 0
            if (bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_26'] == None):
                pass
            else:
                edit_by_colourtexturebake_combined['sna_ebc_temp_store_set_material'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_26']
            edit_by_colourtexturebake_combined['sna_ebc_temp_store_base_texture'] = bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4']
            modifier_name = 'KIRI_Edit_By_Colour_GN'
            object_name = bpy.context.view_layer.objects.active.name
            obj = bpy.data.objects.get(object_name)
            if obj:
                modifier = obj.modifiers.get(modifier_name)
                if modifier:
                    if not modifier.show_viewport:
                        # Simply remove the modifier if it's hidden
                        obj.modifiers.remove(modifier)
                        print(f"Removed hidden modifier '{modifier_name}' from object '{object_name}'.")
                    else:
                        # Apply normally if visible
                        bpy.ops.object.modifier_apply(modifier=modifier_name)
                        print(f"Applied visible modifier '{modifier_name}' to object '{object_name}'.")
                else:
                    print(f"Modifier '{modifier_name}' not found on object '{object_name}'.")
            else:
                print(f"Object '{object_name}' not found.")
            sna_add_edit_by_colour_modifier_function_execute_7A473()
            bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_4'] = edit_by_colourtexturebake_combined['sna_ebc_temp_store_base_texture']
            bpy.context.view_layer.objects.active.modifiers['KIRI_Edit_By_Colour_GN']['Socket_48'] = 0
            bpy.context.active_object.update_tag(refresh={'DATA'}, )
            if bpy.context and bpy.context.screen:
                for a in bpy.context.screen.areas:
                    a.tag_redraw()
            bpy.context.view_layer.objects.active.sna_ebc_live_effects_proxy_switch = 'None'
            bpy.context.scene.sna_ebc_active_menu_full = 'Texture'
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.samples = self.sna_bake_samples
            edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'] = []
            if self.sna_bake_diffuse:
                edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'].append('DIFFUSE')
            if self.sna_bake_roughness:
                edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'].append('ROUGHNESS')
            if self.sna_bake_normal:
                edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'].append('NORMAL')
            for i_0660C in range(len(bpy.context.view_layer.objects.active.material_slots)):
                for i_57D31 in range(len(bpy.context.view_layer.objects.active.material_slots[i_0660C].material.node_tree.nodes)):
                    bpy.context.view_layer.objects.active.material_slots[i_0660C].material.node_tree.nodes[i_57D31].select = False
            if (property_exists("bpy.data.materials", globals(), locals()) and 'Combined_Bake_Material' in bpy.data.materials):
                pass
            else:
                before_data = list(bpy.data.materials)
                bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'KIRI_Edit_By_Colour_OBJECT_APPEND.blend') + r'\Material', filename='EBC_Combined_Bake_Material', link=False)
                new_data = list(filter(lambda d: not d in before_data, list(bpy.data.materials)))
                appended_41152 = None if not new_data else new_data[0]
            edit_by_colourtexturebake_combined['sna_ebc_bake_count'] = 0

            def delayed_0E63E():
                is_baking = None
                is_baking = bpy.app.is_job_running("OBJECT_BAKE")
                if is_baking:
                    pass
                else:
                    image_294E9 = bpy.data.images.new(name='Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Texture', width=(((8192 if (self.sna_bake_resolution != '4K') else 4096) if (self.sna_bake_resolution != '2K') else 2048) if (self.sna_bake_resolution != '1K') else 1080), height=(((8192 if (self.sna_bake_resolution != '4K') else 4096) if (self.sna_bake_resolution != '2K') else 2048) if (self.sna_bake_resolution != '1K') else 1080), is_data=(edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] != 'DIFFUSE'), )
                    if (edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] == 'DIFFUSE'):
                        bpy.context.scene.sna_ebc_baked_diffuse_image = image_294E9
                    if (edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] == 'ROUGHNESS'):
                        bpy.context.scene.sna_ebc_baked_roughness_image = image_294E9
                    if (edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] == 'NORMAL'):
                        bpy.context.scene.sna_ebc_baked_normal_image = image_294E9
                    for i_1AD62 in range(len(bpy.context.view_layer.objects.active.material_slots)):
                        if (property_exists("bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes", globals(), locals()) and 'Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Node' in bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes):
                            pass
                        else:
                            node_ECC29 = bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes.new(type='ShaderNodeTexImage', )
                            node_ECC29.name = 'Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Node'
                            node_ECC29.label = 'Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Node'
                            node_ECC29.use_custom_color = True
                            node_ECC29.color = (0.09107446670532227, 0.274009108543396, 1.0)
                            node_ECC29.location = (400.0, float(edit_by_colourtexturebake_combined['sna_ebc_bake_count'] * -250.0))
                            node_ECC29.image = image_294E9
                            bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes.active = node_ECC29
                            node_ECC29.select = True
                        bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes['Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Node'].image = image_294E9
                        bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes.active = bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes['Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Node']
                        bpy.context.view_layer.objects.active.material_slots[i_1AD62].material.node_tree.nodes['Combined_Bake_' + edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] + '_Node'].select = True
                    bpy.context.view_layer.objects.active.select_set(state=True, view_layer=bpy.context.view_layer, )
                    bpy.ops.object.bake('INVOKE_DEFAULT', type=edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']], pass_filter=set([('COLOR' if (edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'][edit_by_colourtexturebake_combined['sna_ebc_bake_count']] == 'DIFFUSE') else 'NONE')]), margin=16, use_selected_to_active=False, max_ray_distance=0.0, cage_extrusion=1.0, normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z', target='IMAGE_TEXTURES', save_mode='INTERNAL', use_clear=True)
                    edit_by_colourtexturebake_combined['sna_ebc_bake_count'] += 1
                if (edit_by_colourtexturebake_combined['sna_ebc_bake_count'] == len(edit_by_colourtexturebake_combined['sna_ebc_bake_type_list'])):
                    return None
                return 0.10000000149011612
            bpy.app.timers.register(delayed_0E63E, first_interval=0.0)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_45332 = layout.box()
        box_45332.alert = False
        box_45332.enabled = True
        box_45332.active = True
        box_45332.use_property_split = False
        box_45332.use_property_decorate = False
        box_45332.alignment = 'Expand'.upper()
        box_45332.scale_x = 1.0
        box_45332.scale_y = 1.0
        if not True: box_45332.operator_context = "EXEC_DEFAULT"
        box_5D865 = box_45332.box()
        box_5D865.alert = False
        box_5D865.enabled = True
        box_5D865.active = True
        box_5D865.use_property_split = False
        box_5D865.use_property_decorate = False
        box_5D865.alignment = 'Expand'.upper()
        box_5D865.scale_x = 1.0
        box_5D865.scale_y = 1.0
        if not True: box_5D865.operator_context = "EXEC_DEFAULT"
        box_A2874 = box_5D865.box()
        box_A2874.alert = True
        box_A2874.enabled = True
        box_A2874.active = True
        box_A2874.use_property_split = False
        box_A2874.use_property_decorate = False
        box_A2874.alignment = 'Expand'.upper()
        box_A2874.scale_x = 1.0
        box_A2874.scale_y = 1.0
        if not True: box_A2874.operator_context = "EXEC_DEFAULT"
        box_A2874.label(text='The Edit By Colour modifier will be applied, then re-added', icon_value=string_to_icon('INFO'))
        box_A2874.label(text='         These effects are destructive', icon_value=0)
        box_5D865.prop(self, 'sna_apply_subdivision', text='Apply Subdivisions', icon_value=0, emboss=True)
        box_45332.label(text='Bake Settings', icon_value=0)
        box_67968 = box_45332.box()
        box_67968.alert = False
        box_67968.enabled = True
        box_67968.active = True
        box_67968.use_property_split = False
        box_67968.use_property_decorate = False
        box_67968.alignment = 'Expand'.upper()
        box_67968.scale_x = 1.0
        box_67968.scale_y = 1.0
        if not True: box_67968.operator_context = "EXEC_DEFAULT"
        box_67968.prop(bpy.context.scene.cycles, 'device', text='Bake Device', icon_value=0, emboss=True)
        box_67968.prop(self, 'sna_bake_samples', text='Bake Samples', icon_value=0, emboss=True)
        box_C3C21 = box_45332.box()
        box_C3C21.alert = False
        box_C3C21.enabled = True
        box_C3C21.active = True
        box_C3C21.use_property_split = False
        box_C3C21.use_property_decorate = False
        box_C3C21.alignment = 'Expand'.upper()
        box_C3C21.scale_x = 1.0
        box_C3C21.scale_y = 1.0
        if not True: box_C3C21.operator_context = "EXEC_DEFAULT"
        box_C3C21.prop_search(bpy.context.scene, 'sna_ebc_base_material', bpy.data, 'objects', text='Base Material', icon='NONE')
        box_1531A = box_45332.box()
        box_1531A.alert = False
        box_1531A.enabled = True
        box_1531A.active = True
        box_1531A.use_property_split = False
        box_1531A.use_property_decorate = False
        box_1531A.alignment = 'Expand'.upper()
        box_1531A.scale_x = 1.0
        box_1531A.scale_y = 1.0
        if not True: box_1531A.operator_context = "EXEC_DEFAULT"
        box_1531A.prop(self, 'sna_bake_resolution', text='Bake Resolution', icon_value=0, emboss=True)
        box_BA395 = box_45332.box()
        box_BA395.alert = False
        box_BA395.enabled = True
        box_BA395.active = True
        box_BA395.use_property_split = False
        box_BA395.use_property_decorate = False
        box_BA395.alignment = 'Expand'.upper()
        box_BA395.scale_x = 1.0
        box_BA395.scale_y = 1.0
        if not True: box_BA395.operator_context = "EXEC_DEFAULT"
        box_BA395.prop(self, 'sna_bake_diffuse', text='Bake Diffuse', icon_value=0, emboss=True)
        box_BA395.prop(self, 'sna_bake_roughness', text='Bake Roughness', icon_value=0, emboss=True)
        box_BA395.prop(self, 'sna_bake_normal', text='Bake Normal', icon_value=0, emboss=True)

    def invoke(self, context, event):
        bpy.context.scene.sna_ebc_base_material = bpy.context.view_layer.objects.active.material_slots[0].material
        return context.window_manager.invoke_props_dialog(self, width=500)


def sna_bake_combined_function_interface_4566F(layout_function, ):
    box_97CC3 = layout_function.box()
    box_97CC3.alert = False
    box_97CC3.enabled = True
    box_97CC3.active = True
    box_97CC3.use_property_split = False
    box_97CC3.use_property_decorate = False
    box_97CC3.alignment = 'Expand'.upper()
    box_97CC3.scale_x = 1.0
    box_97CC3.scale_y = 1.0
    if not True: box_97CC3.operator_context = "EXEC_DEFAULT"
    box_97CC3.label(text='Unify Textures', icon_value=0)
    op = box_97CC3.operator('sna.bake_set_material__original_dafdb', text='Bake Combined Material', icon_value=string_to_icon('IMAGE_RGB'), emboss=True, depress=False)
    op.sna_bake_diffuse = False
    op.sna_bake_roughness = False
    op.sna_bake_normal = False
    op.sna_bake_resolution = '1K'
    op.sna_apply_subdivision = False
    op = box_97CC3.operator('sna.switch_to_combined_bake_material_a7d5f', text='Switch To Baked Material', icon_value=string_to_icon('FILE_REFRESH'), emboss=True, depress=False)


class SNA_OT_Switch_To_Combined_Bake_Material_A7D5F(bpy.types.Operator):
    bl_idname = "sna.switch_to_combined_bake_material_a7d5f"
    bl_label = "Switch To Combined Bake Material"
    bl_description = "Removes all materials assigned to the active object and replaces them with the combined bake material."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        target_object = bpy.context.view_layer.objects.active
        material_to_assign = bpy.context.scene.sna_ebc_combined_bake_material
        clear_unused = True
        make_active = True
        assign_all_faces = True
        # ASSIGN NEW MATERIAL SLOT
        # Adds a new material slot to an object and assigns the specified material to it with optional face assignment
        #target_object: Object to add material slot to
        #Type: Pointer
        #Pointer: bpy.types.Object
        #Description: Target object that will receive the new material slot
        #material_to_assign: Material to assign to new slot
        #Type: Pointer
        #Pointer: bpy.types.Material
        #Description: Material that will be assigned to the new slot
        #clear_unused: Clear unused materials first
        #Values: True, False
        #Default: False
        #Description: Whether to remove unused material slots before adding new one
        #make_active: Make new slot the active slot
        #Values: True, False
        #Default: True
        #Description: Whether to make the new slot the active material slot
        #assign_all_faces: Assign material to all faces
        #Values: True, False
        #Default: False
        #Description: Whether to assign this material to all faces of the object
        # Input variables
        #target_object = None
        #material_to_assign = None
        #clear_unused = False
        #make_active = True
        #assign_all_faces = False
        # Output variables
        success = False
        error_message = ""
        slot_index = -1
        try:
           print(f"Processing material slots for object: {target_object.name}")
           # Clear unused materials if requested
           if clear_unused:
               print("Clearing unused materials...")
               # Get initial slot count
               initial_slot_count = len(target_object.material_slots)
               print(f"Initial material slots: {initial_slot_count}")
               # Remove slots that have no material assigned
               for i in range(len(target_object.material_slots) - 1, -1, -1):
                   if target_object.material_slots[i].material is None:
                       target_object.data.materials.pop(index=i)
                       print(f"Removed empty slot at index {i}")
               # Check remaining slots for usage
               if hasattr(target_object.data, "polygons"):
                   used_indices = {p.material_index for p in target_object.data.polygons}
                   print(f"Found used material indices: {used_indices}")
                   # Remove unused slots from highest index to lowest
                   for i in range(len(target_object.material_slots) - 1, -1, -1):
                       if i not in used_indices:
                           target_object.data.materials.pop(index=i)
                           print(f"Removed unused slot at index {i}")
               # Report cleanup results
               final_slot_count = len(target_object.material_slots)
               removed_count = initial_slot_count - final_slot_count
               print(f"Removed {removed_count} unused slots. Remaining slots: {final_slot_count}")
           # Add new material slot
           target_object.data.materials.append(None)
           slot_index = len(target_object.data.materials) - 1
           print(f"Created new slot at index: {slot_index}")
           # Assign material to the new slot
           target_object.data.materials[slot_index] = material_to_assign
           print(f"Assigned material: {material_to_assign.name}")
           # Assign this material slot to all polygons if requested
           if assign_all_faces and hasattr(target_object.data, "polygons"):
               print("Assigning material to all faces...")
               for polygon in target_object.data.polygons:
                   polygon.material_index = slot_index
               print(f"Assigned material index {slot_index} to {len(target_object.data.polygons)} faces")
           # Make slot active if requested
           if make_active:
               target_object.active_material_index = slot_index
               print("Set as active material slot")
           success = True
           print("Material slot assignment completed successfully")
        except Exception as e:
           error_message = str(e)
           print(f"Error assigning material slot: {error_message}")
           slot_index = -1
        if (property_exists("bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes", globals(), locals()) and 'Principled BSDF' in bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes):
            if (property_exists("bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes", globals(), locals()) and 'Normal Map' in bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes):
                for i_927EE in range(len(bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes)):
                    if 'Combined_Bake_DIFFUSE' in bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes[i_927EE].name:
                        if (bpy.context.scene.sna_ebc_baked_diffuse_image == None):
                            pass
                        else:
                            bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes[i_927EE].image = bpy.context.scene.sna_ebc_baked_diffuse_image
                    if 'Combined_Bake_ROUGHNESS' in bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes[i_927EE].name:
                        if (bpy.context.scene.sna_ebc_baked_roughness_image == None):
                            pass
                        else:
                            bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes[i_927EE].image = bpy.context.scene.sna_ebc_baked_roughness_image
                    if 'Combined_Bake_NORMAL' in bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes[i_927EE].name:
                        if (bpy.context.scene.sna_ebc_baked_normal_image == None):
                            pass
                        else:
                            bpy.context.scene.sna_ebc_combined_bake_material.node_tree.nodes[i_927EE].image = bpy.context.scene.sna_ebc_baked_normal_image
                    target_object = bpy.context.view_layer.objects.active
                    remove_empty = True
                    remove_unused = True
                    # REMOVE UNUSED MATERIALS
                    # Removes unused material slots from an object (empty slots and slots not used by any polygons)
                    #target_object: Object to clean materials from
                    #Type: Pointer
                    #Pointer: bpy.types.Object
                    #Description: Target object to remove unused materials from
                    #remove_empty: Remove slots with no material assigned
                    #Values: True, False
                    #Default: True
                    #Description: Whether to remove slots that have no material assigned
                    #remove_unused: Remove slots not used by any polygons
                    #Values: True, False
                    #Default: True
                    #Description: Whether to remove slots that aren't used by any faces
                    # Input variables
                    #target_object = None
                    #remove_empty = True
                    #remove_unused = True
                    # Output variables
                    success = False
                    error_message = ""
                    removed_count = 0
                    try:
                        print(f"Cleaning materials for object: {target_object.name}")
                        initial_slot_count = len(target_object.material_slots)
                        print(f"Initial material slots: {initial_slot_count}")
                        # First pass: Remove empty slots
                        if remove_empty:
                            print("Checking for empty slots...")
                            for i in range(len(target_object.material_slots) - 1, -1, -1):
                                if target_object.material_slots[i].material is None:
                                    target_object.data.materials.pop(index=i)
                                    print(f"Removed empty slot at index {i}")
                                    removed_count += 1
                        # Second pass: Remove unused slots
                        if remove_unused and hasattr(target_object.data, "polygons"):
                            print("Checking for unused slots...")
                            used_indices = {p.material_index for p in target_object.data.polygons}
                            print(f"Found used material indices: {used_indices}")
                            for i in range(len(target_object.material_slots) - 1, -1, -1):
                                if i not in used_indices:
                                    target_object.data.materials.pop(index=i)
                                    print(f"Removed unused slot at index {i}")
                                    removed_count += 1
                        final_slot_count = len(target_object.material_slots)
                        print(f"Removed {removed_count} slots total")
                        print(f"Final material slot count: {final_slot_count}")
                        success = True
                    except Exception as e:
                        error_message = str(e)
                        print(f"Error cleaning materials: {error_message}")
                        removed_count = 0
            else:
                self.report({'ERROR'}, message='Normal Map node not found in Combined Bake material')
        else:
            self.report({'ERROR'}, message='Principled BSDF not found in Combined Bake material')
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_488F8 = layout.box()
        box_488F8.alert = False
        box_488F8.enabled = True
        box_488F8.active = True
        box_488F8.use_property_split = False
        box_488F8.use_property_decorate = False
        box_488F8.alignment = 'Expand'.upper()
        box_488F8.scale_x = 1.0
        box_488F8.scale_y = 1.0
        if not True: box_488F8.operator_context = "EXEC_DEFAULT"
        box_ABB21 = box_488F8.box()
        box_ABB21.alert = True
        box_ABB21.enabled = True
        box_ABB21.active = True
        box_ABB21.use_property_split = False
        box_ABB21.use_property_decorate = False
        box_ABB21.alignment = 'Expand'.upper()
        box_ABB21.scale_x = 1.0
        box_ABB21.scale_y = 1.0
        if not True: box_ABB21.operator_context = "EXEC_DEFAULT"
        box_ABB21.label(text='All faces on the active object will be set to', icon_value=0)
        box_ABB21.label(text="use the 'Combined_Bake' material", icon_value=0)
        box_F2AC4 = box_488F8.box()
        box_F2AC4.alert = False
        box_F2AC4.enabled = True
        box_F2AC4.active = True
        box_F2AC4.use_property_split = False
        box_F2AC4.use_property_decorate = False
        box_F2AC4.alignment = 'Expand'.upper()
        box_F2AC4.scale_x = 1.0
        box_F2AC4.scale_y = 1.0
        if not True: box_F2AC4.operator_context = "EXEC_DEFAULT"
        box_F2AC4.label(text='Combined Bake Material', icon_value=0)
        box_F2AC4.prop_search(bpy.context.scene, 'sna_ebc_combined_bake_material', bpy.data, 'materials', text='', icon='NONE')
        box_9D0E3 = box_488F8.box()
        box_9D0E3.alert = False
        box_9D0E3.enabled = True
        box_9D0E3.active = True
        box_9D0E3.use_property_split = False
        box_9D0E3.use_property_decorate = False
        box_9D0E3.alignment = 'Expand'.upper()
        box_9D0E3.scale_x = 1.0
        box_9D0E3.scale_y = 1.0
        if not True: box_9D0E3.operator_context = "EXEC_DEFAULT"
        box_9D0E3.label(text='Baked Diffuse Texture', icon_value=0)
        box_9D0E3.prop(bpy.context.scene, 'sna_ebc_baked_diffuse_image', text='', icon_value=0, emboss=True)
        box_9D0E3.label(text='Baked Roughness Texture', icon_value=0)
        box_9D0E3.prop(bpy.context.scene, 'sna_ebc_baked_roughness_image', text='', icon_value=0, emboss=True)
        box_9D0E3.label(text='Baked Normal Texture', icon_value=0)
        box_9D0E3.prop(bpy.context.scene, 'sna_ebc_baked_normal_image', text='', icon_value=0, emboss=True)

    def invoke(self, context, event):
        if (property_exists("bpy.data.materials", globals(), locals()) and 'EBC_Combined_Bake_Material' in bpy.data.materials):
            bpy.context.scene.sna_ebc_combined_bake_material = bpy.data.materials['EBC_Combined_Bake_Material']
        return context.window_manager.invoke_props_dialog(self, width=400)


class SNA_OT_Bake_To_Patch_Fa828(bpy.types.Operator):
    bl_idname = "sna.bake_to_patch_fa828"
    bl_label = "Bake To Patch"
    bl_description = "Bakes from the active object to the assigned bake patch material."
    bl_options = {"REGISTER", "UNDO"}
    sna_bake_samples: bpy.props.IntProperty(name='Bake Samples', description='', default=10, subtype='NONE', min=1)
    sna_bake_diffuse: bpy.props.BoolProperty(name='Bake Diffuse', description='', default=False)
    sna_bake_roughness: bpy.props.BoolProperty(name='Bake Roughness', description='', default=False)
    sna_bake_normal: bpy.props.BoolProperty(name='Bake Normal', description='', default=False)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if ((not self.sna_bake_diffuse) and (not self.sna_bake_roughness) and (not self.sna_bake_normal)):
            self.report({'INFO'}, message='No bake passes selected - no changes made')
        else:
            target_object = bpy.context.scene.sna_ebc_bake_base_object
            material_to_assign = bpy.context.scene.sna_ebc_bake_patch_material
            make_active = True
            clear_unused = True
            assign_all_faces = False
            # ASSIGN NEW MATERIAL SLOT
            # Adds a new material slot to an object and assigns the specified material to it with optional face assignment
            #target_object: Object to add material slot to
            #Type: Pointer
            #Pointer: bpy.types.Object
            #Description: Target object that will receive the new material slot
            #material_to_assign: Material to assign to new slot
            #Type: Pointer
            #Pointer: bpy.types.Material
            #Description: Material that will be assigned to the new slot
            #clear_unused: Clear unused materials first
            #Values: True, False
            #Default: False
            #Description: Whether to remove unused material slots before adding new one
            #make_active: Make new slot the active slot
            #Values: True, False
            #Default: True
            #Description: Whether to make the new slot the active material slot
            #assign_all_faces: Assign material to all faces
            #Values: True, False
            #Default: False
            #Description: Whether to assign this material to all faces of the object
            # Input variables
            #target_object = None
            #material_to_assign = None
            #clear_unused = False
            #make_active = True
            #assign_all_faces = False
            # Output variables
            success = False
            error_message = ""
            slot_index = -1
            try:
               print(f"Processing material slots for object: {target_object.name}")
               # Clear unused materials if requested
               if clear_unused:
                   print("Clearing unused materials...")
                   # Get initial slot count
                   initial_slot_count = len(target_object.material_slots)
                   print(f"Initial material slots: {initial_slot_count}")
                   # Remove slots that have no material assigned
                   for i in range(len(target_object.material_slots) - 1, -1, -1):
                       if target_object.material_slots[i].material is None:
                           target_object.data.materials.pop(index=i)
                           print(f"Removed empty slot at index {i}")
                   # Check remaining slots for usage
                   if hasattr(target_object.data, "polygons"):
                       used_indices = {p.material_index for p in target_object.data.polygons}
                       print(f"Found used material indices: {used_indices}")
                       # Remove unused slots from highest index to lowest
                       for i in range(len(target_object.material_slots) - 1, -1, -1):
                           if i not in used_indices:
                               target_object.data.materials.pop(index=i)
                               print(f"Removed unused slot at index {i}")
                   # Report cleanup results
                   final_slot_count = len(target_object.material_slots)
                   removed_count = initial_slot_count - final_slot_count
                   print(f"Removed {removed_count} unused slots. Remaining slots: {final_slot_count}")
               # Add new material slot
               target_object.data.materials.append(None)
               slot_index = len(target_object.data.materials) - 1
               print(f"Created new slot at index: {slot_index}")
               # Assign material to the new slot
               target_object.data.materials[slot_index] = material_to_assign
               print(f"Assigned material: {material_to_assign.name}")
               # Assign this material slot to all polygons if requested
               if assign_all_faces and hasattr(target_object.data, "polygons"):
                   print("Assigning material to all faces...")
                   for polygon in target_object.data.polygons:
                       polygon.material_index = slot_index
                   print(f"Assigned material index {slot_index} to {len(target_object.data.polygons)} faces")
               # Make slot active if requested
               if make_active:
                   target_object.active_material_index = slot_index
                   print("Set as active material slot")
               success = True
               print("Material slot assignment completed successfully")
            except Exception as e:
               error_message = str(e)
               print(f"Error assigning material slot: {error_message}")
               slot_index = -1
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.samples = self.sna_bake_samples
            for i_99343 in range(len(bpy.context.scene.objects)):
                bpy.context.scene.objects[i_99343].select_set(state=False, view_layer=bpy.context.view_layer, )
            bpy.context.scene.sna_ebc_bake_base_object.select_set(state=True, view_layer=bpy.context.view_layer, )
            bpy.context.scene.sna_ebc_bake_patch_object.select_set(state=True, view_layer=bpy.context.view_layer, )
            bpy.context.view_layer.objects.active = bpy.context.scene.sna_ebc_bake_patch_object
            edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'] = []
            if self.sna_bake_diffuse:
                edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'].append('DIFFUSE')
            if self.sna_bake_roughness:
                edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'].append('ROUGHNESS')
            if self.sna_bake_normal:
                edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'].append('NORMAL')
            edit_by_colourtexturebake_patch['sna_ebc_bake_count'] = 0

            def delayed_F7E06():
                is_baking = None
                is_baking = bpy.app.is_job_running("OBJECT_BAKE")
                if is_baking:
                    pass
                else:
                    for i_D2F31 in range(len(bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes)):
                        if edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'][edit_by_colourtexturebake_patch['sna_ebc_bake_count']] + '_Image_Node' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31].name:
                            bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes.active = bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31]
                            bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31].select = True
                            edit_by_colourtexturebake_patch['sna_ebc_active_bake_node'] = bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31]
                            for i_6728E in range(len(bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31].outputs[0].links)-1,-1,-1):
                                bpy.context.scene.sna_ebc_bake_patch_material.node_tree.links.remove(link=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31].outputs[0].links[i_6728E], )
                        else:
                            bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_D2F31].select = False
                    print(str(len(edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'])))
                    print('Bake Count = ' + str(edit_by_colourtexturebake_patch['sna_ebc_bake_count']))
                    print('Current Passs = ', edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'][edit_by_colourtexturebake_patch['sna_ebc_bake_count']])
                    print('Active Node = ', bpy.context.view_layer.objects.active.active_material.node_tree.nodes.active.name)
                    bpy.ops.object.bake('INVOKE_DEFAULT', type=edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'][edit_by_colourtexturebake_patch['sna_ebc_bake_count']], pass_filter=set([('COLOR' if (edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'][edit_by_colourtexturebake_patch['sna_ebc_bake_count']] == 'DIFFUSE') else 'NONE')]), margin=16, use_selected_to_active=True, max_ray_distance=0.0, cage_extrusion=1.0, normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z', target='IMAGE_TEXTURES', save_mode='INTERNAL', use_clear=True)
                    edit_by_colourtexturebake_patch['sna_ebc_bake_count'] += 1
                if (edit_by_colourtexturebake_patch['sna_ebc_bake_count'] == len(edit_by_colourtexturebake_patch['sna_ebc_bake_type_list'])):
                    return None
                return 0.10000000149011612
            bpy.app.timers.register(delayed_F7E06, first_interval=0.0)
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_1DD24 = layout.box()
        box_1DD24.alert = False
        box_1DD24.enabled = True
        box_1DD24.active = True
        box_1DD24.use_property_split = False
        box_1DD24.use_property_decorate = False
        box_1DD24.alignment = 'Expand'.upper()
        box_1DD24.scale_x = 1.0
        box_1DD24.scale_y = 1.0
        if not True: box_1DD24.operator_context = "EXEC_DEFAULT"
        box_1DD24.label(text='Bake Settings', icon_value=0)
        box_DE272 = box_1DD24.box()
        box_DE272.alert = False
        box_DE272.enabled = True
        box_DE272.active = True
        box_DE272.use_property_split = False
        box_DE272.use_property_decorate = False
        box_DE272.alignment = 'Expand'.upper()
        box_DE272.scale_x = 1.0
        box_DE272.scale_y = 1.0
        if not True: box_DE272.operator_context = "EXEC_DEFAULT"
        box_DE272.prop_search(bpy.context.scene, 'sna_ebc_bake_base_object', bpy.data, 'objects', text='Base Object', icon='NONE')
        box_DE272.prop_search(bpy.context.scene, 'sna_ebc_bake_patch_object', bpy.data, 'objects', text='Bake Patch', icon='NONE')
        box_DE272.prop_search(bpy.context.scene, 'sna_ebc_bake_patch_material', bpy.data, 'objects', text='Bake Patch Material', icon='NONE')
        box_19C7C = box_1DD24.box()
        box_19C7C.alert = False
        box_19C7C.enabled = True
        box_19C7C.active = True
        box_19C7C.use_property_split = False
        box_19C7C.use_property_decorate = False
        box_19C7C.alignment = 'Expand'.upper()
        box_19C7C.scale_x = 1.0
        box_19C7C.scale_y = 1.0
        if not True: box_19C7C.operator_context = "EXEC_DEFAULT"
        box_19C7C.prop(bpy.context.scene.cycles, 'device', text='Bake Device', icon_value=0, emboss=True)
        box_19C7C.prop(self, 'sna_bake_samples', text='Bake Samples', icon_value=0, emboss=True)
        box_C4A56 = box_1DD24.box()
        box_C4A56.alert = False
        box_C4A56.enabled = True
        box_C4A56.active = True
        box_C4A56.use_property_split = False
        box_C4A56.use_property_decorate = False
        box_C4A56.alignment = 'Expand'.upper()
        box_C4A56.scale_x = 1.0
        box_C4A56.scale_y = 1.0
        if not True: box_C4A56.operator_context = "EXEC_DEFAULT"
        box_C4A56.prop(self, 'sna_bake_diffuse', text='Bake Diffuse', icon_value=0, emboss=True)
        box_C4A56.prop(self, 'sna_bake_roughness', text='Bake Roughness', icon_value=0, emboss=True)
        box_C4A56.prop(self, 'sna_bake_normal', text='Bake Normal', icon_value=0, emboss=True)

    def invoke(self, context, event):
        bpy.context.scene.sna_ebc_bake_base_object = bpy.context.view_layer.objects.active
        return context.window_manager.invoke_props_dialog(self, width=500)


class SNA_OT_Add_Bake_Patch_68526(bpy.types.Operator):
    bl_idname = "sna.add_bake_patch_68526"
    bl_label = "Add Bake Patch"
    bl_description = "Adds a mesh plane meant for baking."
    bl_options = {"REGISTER", "UNDO"}

    def sna_bake_patch_resolution_enum_items(self, context):
        return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
    sna_bake_patch_resolution: bpy.props.EnumProperty(name='Bake Patch Resolution', description='', items=[('1K', '1K', '', 0, 0), ('2K', '2K', '', 0, 1), ('4K', '4K', '', 0, 2)])

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        edit_by_colourtexturebake_patch['sna_ebc_temp_store_active_object'] = bpy.context.view_layer.objects.active
        before_data = list(bpy.data.objects)
        bpy.ops.wm.append(directory=os.path.join(os.path.dirname(__file__), 'assets', 'KIRI_Edit_By_Colour_OBJECT_APPEND.blend') + r'\Object', filename=self.sna_bake_patch_resolution + '_Bake_Patch', link=False)
        new_data = list(filter(lambda d: not d in before_data, list(bpy.data.objects)))
        appended_42718 = None if not new_data else new_data[0]
        appended_42718.location = bpy.context.scene.cursor.location
        appended_42718.rotation_mode = 'QUATERNION'
        bpy.context.scene.cursor.rotation_mode = 'QUATERNION'
        appended_42718.rotation_quaternion = bpy.context.scene.cursor.rotation_quaternion
        modifier_49CBF = appended_42718.modifiers.new(name='Bake Patch Shrinkwrap', type='SHRINKWRAP', )
        modifier_49CBF.target = edit_by_colourtexturebake_patch['sna_ebc_temp_store_active_object']
        modifier_49CBF.wrap_method = 'PROJECT'
        modifier_49CBF.use_negative_direction = True
        bpy.context.view_layer.objects.active = appended_42718
        bpy.context.scene.sna_ebc_bake_patch_material = appended_42718.material_slots[0].material
        bpy.context.scene.sna_ebc_bake_patch_object = appended_42718
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_02260 = layout.box()
        box_02260.alert = False
        box_02260.enabled = True
        box_02260.active = True
        box_02260.use_property_split = False
        box_02260.use_property_decorate = False
        box_02260.alignment = 'Expand'.upper()
        box_02260.scale_x = 1.0
        box_02260.scale_y = 1.0
        if not True: box_02260.operator_context = "EXEC_DEFAULT"
        box_523A4 = box_02260.box()
        box_523A4.alert = True
        box_523A4.enabled = True
        box_523A4.active = True
        box_523A4.use_property_split = False
        box_523A4.use_property_decorate = False
        box_523A4.alignment = 'Expand'.upper()
        box_523A4.scale_x = 1.0
        box_523A4.scale_y = 1.0
        if not True: box_523A4.operator_context = "EXEC_DEFAULT"
        box_523A4.label(text='The active object will be set as the target', icon_value=0)
        box_523A4.label(text='Place 3D cursor first for best results', icon_value=0)
        box_02260.label(text='Bake Patch settings', icon_value=0)
        box_02260.prop(self, 'sna_bake_patch_resolution', text='Bake Patch resolution', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)


def sna_bake_patch_function_interface_834B3(layout_function, ):
    box_2279C = layout_function.box()
    box_2279C.alert = False
    box_2279C.enabled = True
    box_2279C.active = True
    box_2279C.use_property_split = False
    box_2279C.use_property_decorate = False
    box_2279C.alignment = 'Expand'.upper()
    box_2279C.scale_x = 1.0
    box_2279C.scale_y = 1.0
    if not True: box_2279C.operator_context = "EXEC_DEFAULT"
    box_2279C.label(text='Patch Baking', icon_value=0)
    op = box_2279C.operator('sna.add_bake_patch_68526', text='Add Bake Patch', icon_value=316, emboss=True, depress=False)
    op.sna_bake_patch_resolution = '1K'
    op = box_2279C.operator('sna.bake_to_patch_fa828', text='Bake To Patch', icon_value=string_to_icon('FORCE_TEXTURE'), emboss=True, depress=False)
    op.sna_bake_samples = 10
    op.sna_bake_diffuse = False
    op.sna_bake_roughness = False
    op.sna_bake_normal = False
    op = box_2279C.operator('sna.link_baked_textures_patch_067f8', text='Link Baked Textures', icon_value=string_to_icon('FILE_REFRESH'), emboss=True, depress=False)
    op.sna_link_diffuse = True
    op.sna_link_roughness = False
    op.sna_link_normal = False


class SNA_OT_Link_Baked_Textures_Patch_067F8(bpy.types.Operator):
    bl_idname = "sna.link_baked_textures_patch_067f8"
    bl_label = "Link Baked Textures (Patch)"
    bl_description = "Re-links all newly baked and selected bake patch textures"
    bl_options = {"REGISTER", "UNDO"}
    sna_link_diffuse: bpy.props.BoolProperty(name='Link Diffuse', description='', default=False)
    sna_link_roughness: bpy.props.BoolProperty(name='Link Roughness', description='', default=False)
    sna_link_normal: bpy.props.BoolProperty(name='Link Normal', description='', default=False)

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        if (property_exists("bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes", globals(), locals()) and 'Principled BSDF' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes):
            if (property_exists("bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes", globals(), locals()) and 'Normal Map' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes):
                for i_9DB58 in range(len(bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes)):
                    if ('Patch_DIFFUSE' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].name or 'Patch_ROUGHNESS' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].name or 'Patch_NORMAL' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].name):
                        if ('Patch_DIFFUSE' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].name and self.sna_link_diffuse):
                            link_D38BE = bpy.context.scene.sna_ebc_bake_patch_material.node_tree.links.new(input=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes['Principled BSDF'].inputs[0], output=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].outputs[0], )
                        if ('Patch_ROUGHNESS' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].name and self.sna_link_roughness):
                            link_9765A = bpy.context.scene.sna_ebc_bake_patch_material.node_tree.links.new(input=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes['Principled BSDF'].inputs[2], output=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].outputs[0], )
                        if ('Patch_NORMAL' in bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].name and self.sna_link_normal):
                            link_6D43C = bpy.context.scene.sna_ebc_bake_patch_material.node_tree.links.new(input=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes['Normal Map'].inputs[1], output=bpy.context.scene.sna_ebc_bake_patch_material.node_tree.nodes[i_9DB58].outputs[0], )
            else:
                self.report({'ERROR'}, message='Normal Map node not found in Bake Patch Material')
        else:
            self.report({'ERROR'}, message='Principled BSDF not found in Bake Patch Material')
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box_343B1 = layout.box()
        box_343B1.alert = False
        box_343B1.enabled = True
        box_343B1.active = True
        box_343B1.use_property_split = False
        box_343B1.use_property_decorate = False
        box_343B1.alignment = 'Expand'.upper()
        box_343B1.scale_x = 1.0
        box_343B1.scale_y = 1.0
        if not True: box_343B1.operator_context = "EXEC_DEFAULT"
        box_CDF97 = box_343B1.box()
        box_CDF97.alert = False
        box_CDF97.enabled = True
        box_CDF97.active = True
        box_CDF97.use_property_split = False
        box_CDF97.use_property_decorate = False
        box_CDF97.alignment = 'Expand'.upper()
        box_CDF97.scale_x = 1.0
        box_CDF97.scale_y = 1.0
        if not True: box_CDF97.operator_context = "EXEC_DEFAULT"
        box_CDF97.prop_search(bpy.context.scene, 'sna_ebc_bake_patch_object', bpy.data, 'objects', text='Bake Patch', icon='NONE')
        box_CDF97.prop_search(bpy.context.scene, 'sna_ebc_bake_patch_material', bpy.data, 'objects', text='Bake Patch Material', icon='NONE')
        box_F4CB0 = box_343B1.box()
        box_F4CB0.alert = False
        box_F4CB0.enabled = True
        box_F4CB0.active = True
        box_F4CB0.use_property_split = False
        box_F4CB0.use_property_decorate = False
        box_F4CB0.alignment = 'Expand'.upper()
        box_F4CB0.scale_x = 1.0
        box_F4CB0.scale_y = 1.0
        if not True: box_F4CB0.operator_context = "EXEC_DEFAULT"
        box_F4CB0.prop(self, 'sna_link_diffuse', text='Link Diffuse', icon_value=0, emboss=True)
        box_F4CB0.prop(self, 'sna_link_roughness', text='Link Roughness', icon_value=0, emboss=True)
        box_F4CB0.prop(self, 'sna_link_normal', text='Link Normal', icon_value=0, emboss=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)


# ============================================================
# Palette Split — quantize texture to manual palette + gradients
# ============================================================

class SNA_PaletteColorItem(bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(
        name='Color', subtype='COLOR', size=3,
        min=0.0, max=1.0, default=(0.5, 0.5, 0.5),
    )
    steps: bpy.props.IntProperty(
        name='Gradient Steps', default=4, min=1, max=16,
        description='How many tones to split this base color into',
    )


class SNA_UL_palette_colors(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, 'color', text='')
        row.prop(item, 'steps', text='Steps')


class SNA_OT_palette_add(bpy.types.Operator):
    bl_idname = 'sna.palette_add'
    bl_label = 'Add Palette Color'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.sna_palette_colors.add()
        context.scene.sna_palette_active_index = len(context.scene.sna_palette_colors) - 1
        return {'FINISHED'}


class SNA_OT_palette_remove(bpy.types.Operator):
    bl_idname = 'sna.palette_remove'
    bl_label = 'Remove Palette Color'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        coll = context.scene.sna_palette_colors
        idx = context.scene.sna_palette_active_index
        if 0 <= idx < len(coll):
            coll.remove(idx)
            context.scene.sna_palette_active_index = max(0, idx - 1)
        return {'FINISHED'}


def _sna_hsv_dist(a, b):
    import math
    dh = min(abs(a[0] - b[0]), 1.0 - abs(a[0] - b[0])) * 2.0
    ds = a[1] - b[1]
    dv = a[2] - b[2]
    return math.sqrt(dh * dh + ds * ds + dv * dv)


def _sna_make_bary_pts(n):
    """Return list of (u, v, w) barycentric coords, sqrt-spaced inside triangle."""
    import math
    pts = []
    k = int(math.ceil(math.sqrt(n)))
    for i in range(1, k + 2):
        for j in range(1, k - i + 3):
            a = i / (k + 2); b = j / (k + 2); c = 1.0 - a - b
            if c > 0:
                pts.append((a, b, c))
    if not pts:
        pts = [(1/3, 1/3, 1/3)]
    if len(pts) > n:
        pts = pts[:n]
    return pts


def _sna_rgb_to_hsv_np(arr):
    """arr: (N,3) float32 RGB → (N,3) float32 HSV."""
    import numpy as np
    r, g, b = arr[:, 0], arr[:, 1], arr[:, 2]
    mx = np.max(arr, axis=1); mn = np.min(arr, axis=1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-8), 0.0)
    rc = np.where(d > 0, (mx - r) / np.maximum(d, 1e-8), 0.0)
    gc = np.where(d > 0, (mx - g) / np.maximum(d, 1e-8), 0.0)
    bc = np.where(d > 0, (mx - b) / np.maximum(d, 1e-8), 0.0)
    h_ = np.where(r == mx, bc - gc,
          np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h_ = (h_ / 6.0) % 1.0
    return np.stack([h_, s, mx], axis=1)


class SNA_OT_palette_split_and_colorize(bpy.types.Operator):
    bl_idname = 'sna.palette_split_and_colorize'
    bl_label = 'Split & Colorize by Palette'
    bl_description = 'Sample texture per face, bin to nearest palette color + luminance bin, assign materials and separate by material'
    bl_options = {'REGISTER', 'UNDO'}

    samples_per_face: bpy.props.IntProperty(
        name='Samples per Face', default=7, min=1, max=64,
        description='Barycentric samples averaged per face for accuracy',
    )
    do_separate: bpy.props.BoolProperty(
        name='Separate by Material', default=True,
        description='Split into individual mesh objects (one per color bucket) after assigning materials',
    )

    def execute(self, context):
        import math, colorsys
        obj = context.view_layer.objects.active
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, 'No active mesh')
            return {'CANCELLED'}

        mod = obj.modifiers.get('KIRI_Edit_By_Colour_GN')
        if mod is None:
            self.report({'ERROR'}, 'Add Edit By Colour modifier first')
            return {'CANCELLED'}

        try:
            uv_name = mod['Socket_2']
        except Exception:
            uv_name = ''
        try:
            image = mod['Socket_4']
        except Exception:
            image = None

        if not uv_name or uv_name not in obj.data.uv_layers:
            self.report({'ERROR'}, 'UV Map not set in modifier')
            return {'CANCELLED'}
        if image is None:
            self.report({'ERROR'}, 'Base Texture not set in modifier')
            return {'CANCELLED'}

        palette = list(context.scene.sna_palette_colors)
        if not palette:
            self.report({'ERROR'}, 'Palette empty — add colors first')
            return {'CANCELLED'}

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        w, h = image.size[0], image.size[1]
        if w == 0 or h == 0:
            self.report({'ERROR'}, 'Image has zero size')
            return {'CANCELLED'}
        px = list(image.pixels)

        def sample(u, v):
            u = u - math.floor(u)
            v = v - math.floor(v)
            x = min(w - 1, int(u * w))
            y = min(h - 1, int(v * h))
            i = (y * w + x) * 4
            return px[i], px[i+1], px[i+2]

        bary_pts = _sna_make_bary_pts(max(1, self.samples_per_face))

        pal_hsv = [colorsys.rgb_to_hsv(c.color[0], c.color[1], c.color[2]) for c in palette]

        mat_index_map = {}
        def get_mat_slot(base_idx, bin_idx):
            key = (base_idx, bin_idx)
            if key in mat_index_map:
                return mat_index_map[key]
            base = palette[base_idx]
            steps = max(1, base.steps)
            if steps == 1:
                v_mul = 1.0
            else:
                v_mul = 0.3 + 0.7 * (bin_idx / (steps - 1))
            br = base.color[0] * v_mul
            bg = base.color[1] * v_mul
            bb = base.color[2] * v_mul
            mat_name = f'EBC_Pal_{base_idx}_{bin_idx}'
            mat = bpy.data.materials.get(mat_name)
            if mat is None:
                mat = bpy.data.materials.new(mat_name)
                mat.use_nodes = True
            if mat.use_nodes and mat.node_tree:
                for nd in mat.node_tree.nodes:
                    if nd.type == 'BSDF_PRINCIPLED':
                        nd.inputs['Base Color'].default_value = (br, bg, bb, 1.0)
                        break
            mat.diffuse_color = (br, bg, bb, 1.0)
            slot_idx = -1
            for si, s in enumerate(obj.material_slots):
                if s.material and s.material.name == mat.name:
                    slot_idx = si
                    break
            if slot_idx < 0:
                obj.data.materials.append(mat)
                slot_idx = len(obj.material_slots) - 1
            mat_index_map[key] = slot_idx
            return slot_idx

        me = obj.data
        uv_layer = me.uv_layers[uv_name].data
        for poly in me.polygons:
            loop_indices = list(poly.loop_indices)
            if len(loop_indices) < 3:
                continue
            avg_r = avg_g = avg_b = 0.0
            cnt = 0
            uv0 = uv_layer[loop_indices[0]].uv
            for ti in range(1, len(loop_indices) - 1):
                uv1 = uv_layer[loop_indices[ti]].uv
                uv2 = uv_layer[loop_indices[ti + 1]].uv
                for (a, b, c) in bary_pts:
                    u = a * uv0[0] + b * uv1[0] + c * uv2[0]
                    v = a * uv0[1] + b * uv1[1] + c * uv2[1]
                    r, g, bl = sample(u, v)
                    avg_r += r; avg_g += g; avg_b += bl
                    cnt += 1
            if cnt == 0:
                continue
            avg_r /= cnt; avg_g /= cnt; avg_b /= cnt

            shv = colorsys.rgb_to_hsv(avg_r, avg_g, avg_b)
            best_i = 0
            best_d = float('inf')
            for i, ph in enumerate(pal_hsv):
                d = _sna_hsv_dist(shv, ph)
                if shv[1] < 0.1 and ph[1] > 0.3:
                    d += 0.5
                if d < best_d:
                    best_d = d
                    best_i = i

            steps = max(1, palette[best_i].steps)
            lum = 0.2126 * avg_r + 0.7152 * avg_g + 0.0722 * avg_b
            bin_idx = min(steps - 1, max(0, int(lum * steps)))
            poly.material_index = get_mat_slot(best_i, bin_idx)

        me.update()

        if self.do_separate:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            try:
                bpy.ops.mesh.separate(type='MATERIAL')
            except RuntimeError as e:
                self.report({'WARNING'}, f'Separate failed: {e}')
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, f'Done: {len(mat_index_map)} color buckets')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'samples_per_face')
        layout.prop(self, 'do_separate')


class SNA_OT_auto_palette_split(bpy.types.Operator):
    bl_idname = 'sna.auto_palette_split'
    bl_label = 'Auto Palette Split'
    bl_description = 'Automatically detect dominant colors in the texture via k-means and split mesh into N material buckets'
    bl_options = {'REGISTER', 'UNDO'}

    num_clusters: bpy.props.IntProperty(
        name='Total Colors', default=16, min=2, max=256,
        description='How many color buckets to produce (each becomes one material / mesh)',
    )
    samples_per_face: bpy.props.IntProperty(
        name='Samples per Face', default=4, min=1, max=64,
        description='Barycentric samples averaged per face',
    )
    kmeans_iters: bpy.props.IntProperty(
        name='K-means Iterations', default=20, min=2, max=100,
    )
    kmeans_subsample: bpy.props.IntProperty(
        name='Cluster Sample Cap', default=20000, min=500, max=200000,
        description='Cap number of faces used to compute clusters (random subsample). Speeds up large meshes',
    )
    use_hsv: bpy.props.BoolProperty(
        name='Cluster in HSV', default=True,
        description='K-means in HSV space (better perceptual grouping). Off = RGB',
    )
    do_separate: bpy.props.BoolProperty(
        name='Separate by Material', default=True,
    )
    remove_modifier: bpy.props.BoolProperty(
        name='Remove EBC Modifier after Split', default=True,
        description='Removes the KIRI_Edit_By_Colour_GN modifier from the result objects so their EBC_Auto materials show correctly',
    )
    progressive_separate: bpy.props.BoolProperty(
        name='Progressive Separate (logged)', default=False,
        description='Separate materials one by one with a console log per cluster. Slower but shows progress. Off = single fast bpy.ops.mesh.separate(MATERIAL) with no progress',
    )
    solidify_thickness: bpy.props.FloatProperty(
        name='Solidify Thickness', default=0.0, min=0.0, max=100.0,
        description='If > 0, add a Solidify modifier to the source object before separation so each result piece becomes a closed volume for 3D printing. Recommend 0.4mm (nozzle width) to 1mm. Disabled when 0',
        unit='LENGTH', precision=3, step=10,
    )
    merge_small_islands: bpy.props.BoolProperty(
        name='Merge Small Islands', default=False,
        description='Find connected face regions per cluster; islands smaller than the threshold get merged into their majority neighbor cluster before separation. Reduces tiny print artifacts',
    )
    min_island_size_x: bpy.props.FloatProperty(
        name='Min X', default=0.003, min=0.0, max=10.0,
        description='Minimum bbox extent along X for an island, in scene units. 0 disables the X check',
        unit='LENGTH', precision=4,
    )
    min_island_size_y: bpy.props.FloatProperty(
        name='Min Y', default=0.003, min=0.0, max=10.0,
        description='Minimum bbox extent along Y for an island, in scene units. 0 disables the Y check',
        unit='LENGTH', precision=4,
    )
    min_island_size_z: bpy.props.FloatProperty(
        name='Min Z', default=0.0, min=0.0, max=10.0,
        description='Minimum bbox extent along Z for an island, in scene units. 0 disables the Z check',
        unit='LENGTH', precision=4,
    )
    min_island_face_count: bpy.props.IntProperty(
        name='Min Island Faces', default=20, min=0, max=100000,
        description='Islands with fewer than this many faces are merged regardless of size. Safeguard against degenerate slivers',
    )
    min_island_feature_width: bpy.props.FloatProperty(
        name='Min Feature Width (OBB)', default=0.0, min=0.0, max=10.0,
        description='Minimum width along the smallest principal axis (oriented bounding box). Catches thin features regardless of orientation. 0 = disabled. Recommended 3mm for 0.4mm nozzle prints',
        unit='LENGTH', precision=4,
    )
    merge_max_iters: bpy.props.IntProperty(
        name='Merge Iterations', default=8, min=1, max=30,
        description='Repeat the small-island merge pass up to N times. Each iteration recomputes connected components on the updated labels — small clusters cascade-absorb into larger neighbors. Stops early on convergence. 1 = legacy single-pass behavior',
    )
    erosion_passes: bpy.props.IntProperty(
        name='Erosion Passes', default=0, min=0, max=20,
        description='After bbox-based merging, run N morphological erosion passes. Each pass flips faces whose same-cluster neighbor fraction is below the strength threshold. 1-3 passes typical, 5+ for aggressive smoothing',
    )
    erosion_strength: bpy.props.FloatProperty(
        name='Erosion Strength', default=0.7, min=0.5, max=0.99, precision=2,
        description='Flip face if (same-cluster neighbors / total neighbors) < this value. 0.5 = strict minority only (cant erode 1-face wide strips on triangulated meshes since they have 2/3 same neighbors). 0.7 = catches 1-face strips on triangles. 0.8+ erodes wider features faster',
    )

    _SPIN = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=380)

    def execute(self, context):
        try:
            import numpy as np
        except Exception:
            self.report({'ERROR'}, 'numpy not available in this Blender build')
            return {'CANCELLED'}

        obj = context.view_layer.objects.active
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, 'No active mesh'); return {'CANCELLED'}
        mod = obj.modifiers.get('KIRI_Edit_By_Colour_GN')
        if mod is None:
            self.report({'ERROR'}, 'Add Edit By Colour modifier first'); return {'CANCELLED'}
        try: uv_name = mod['Socket_2']
        except Exception: uv_name = ''
        try: image = mod['Socket_4']
        except Exception: image = None
        if not uv_name or uv_name not in obj.data.uv_layers:
            self.report({'ERROR'}, 'UV Map not set in modifier'); return {'CANCELLED'}
        if image is None:
            self.report({'ERROR'}, 'Base Texture not set in modifier'); return {'CANCELLED'}
        if image.size[0] == 0 or image.size[1] == 0:
            self.report({'ERROR'}, 'Image has zero size'); return {'CANCELLED'}

        self._gen = self._work(context, obj, image, uv_name)
        self._spin_idx = 0
        self._last_text = ''
        # advance once so the first status is visible immediately
        try:
            first = next(self._gen)
            self._apply_status(context, first)
        except StopIteration:
            self._cleanup(context)
            return {'FINISHED'}
        except Exception as e:
            self._cleanup(context)
            self.report({'ERROR'}, f'{type(e).__name__}: {e}')
            return {'CANCELLED'}
        wm = context.window_manager
        wm.progress_begin(0, 100)
        self._timer = wm.event_timer_add(0.08, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            print('[AutoPalette] cancelled by ESC', flush=True)
            self._cleanup(context)
            self.report({'WARNING'}, 'Auto Palette Split cancelled')
            return {'CANCELLED'}
        if event.type == 'TIMER':
            try:
                status = next(self._gen)
                self._apply_status(context, status)
            except StopIteration:
                self._cleanup(context)
                return {'FINISHED'}
            except Exception as e:
                print(f'[AutoPalette] FAILED: {type(e).__name__}: {e}', flush=True)
                self._cleanup(context)
                self.report({'ERROR'}, f'{type(e).__name__}: {e}')
                return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def _apply_status(self, context, status):
        if isinstance(status, tuple):
            if len(status) >= 2:
                text, pct = status[0], status[1]
            elif len(status) == 1:
                text, pct = status[0], None
            else:
                text, pct = str(status), None
        else:
            text, pct = status, None
        self._spin_idx = (self._spin_idx + 1) % len(self._SPIN)
        spin = self._SPIN[self._spin_idx]
        full = f'{spin}  EBC Auto Palette: {text}   (ESC to cancel)'
        try:
            if context.workspace:
                context.workspace.status_text_set(full)
        except Exception:
            pass
        if pct is not None:
            try: context.window_manager.progress_update(max(0, min(100, int(pct))))
            except Exception: pass
        self._last_text = text

    def _cleanup(self, context):
        wm = context.window_manager
        if getattr(self, '_timer', None) is not None:
            try: wm.event_timer_remove(self._timer)
            except Exception: pass
            self._timer = None
        try: wm.progress_end()
        except Exception: pass
        try:
            if context.workspace:
                context.workspace.status_text_set(None)
        except Exception:
            pass

    def _work(self, context, obj, image, uv_name):
        """Generator: yields ('text', pct 0..100) or just 'text'. Each yield = UI tick."""
        import math, colorsys, time
        import numpy as np

        def log(msg):
            print(f'[AutoPalette] {msg}', flush=True)

        t_start = time.time()
        log(f'=== Auto Palette Split started: K={self.num_clusters}, samples={self.samples_per_face}, HSV={self.use_hsv} ===')

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        w, h = image.size[0], image.size[1]
        yield (f'Reading image {w}x{h}...', 0)
        npx = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(npx)
        img = npx.reshape(h, w, 4)[:, :, :3]
        log(f'Image read in {time.time() - t_start:.1f}s')

        bary = np.array(_sna_make_bary_pts(max(1, self.samples_per_face)), dtype=np.float32)

        me = obj.data
        uv_layer = me.uv_layers[uv_name].data
        n_polys = len(me.polygons)
        if n_polys == 0:
            raise RuntimeError('Mesh has no polygons')

        face_colors = np.zeros((n_polys, 3), dtype=np.float32)
        log(f'Sampling {n_polys} polygons...')
        t_sample = time.time()
        # Chunk size for UI yield frequency
        sample_chunk = max(20000, n_polys // 40)
        for chunk_start in range(0, n_polys, sample_chunk):
            chunk_end = min(chunk_start + sample_chunk, n_polys)
            for pi in range(chunk_start, chunk_end):
                poly = me.polygons[pi]
                li = poly.loop_indices
                ln = poly.loop_total
                if ln < 3:
                    continue
                uv0 = uv_layer[li[0]].uv
                acc_r = acc_g = acc_b = 0.0
                cnt = 0
                for ti in range(1, ln - 1):
                    uv1 = uv_layer[li[ti]].uv
                    uv2 = uv_layer[li[ti + 1]].uv
                    us = bary[:, 0] * uv0[0] + bary[:, 1] * uv1[0] + bary[:, 2] * uv2[0]
                    vs = bary[:, 0] * uv0[1] + bary[:, 1] * uv1[1] + bary[:, 2] * uv2[1]
                    us = us - np.floor(us)
                    vs = vs - np.floor(vs)
                    xs = np.minimum((us * w).astype(np.int32), w - 1)
                    ys = np.minimum((vs * h).astype(np.int32), h - 1)
                    cols = img[ys, xs]
                    acc_r += float(cols[:, 0].sum())
                    acc_g += float(cols[:, 1].sum())
                    acc_b += float(cols[:, 2].sum())
                    cnt += len(bary)
                if cnt > 0:
                    face_colors[pi, 0] = acc_r / cnt
                    face_colors[pi, 1] = acc_g / cnt
                    face_colors[pi, 2] = acc_b / cnt
            pct = chunk_end * 100 // n_polys
            elapsed = time.time() - t_sample
            eta = elapsed * (n_polys - chunk_end) / max(chunk_end, 1)
            log(f'  sampling {pct}% ({chunk_end}/{n_polys}) elapsed {elapsed:.1f}s ETA {eta:.1f}s')
            # Pct range for this stage: 0..40
            yield (f'Sampling polygons {pct}% (ETA {eta:.0f}s)', int(pct * 0.4))
        log(f'Sampling done in {time.time() - t_sample:.1f}s')

        yield ('Preparing cluster space...', 42)
        if self.use_hsv:
            cluster_data = _sna_rgb_to_hsv_np(face_colors)
            hx = np.cos(cluster_data[:, 0] * 2.0 * math.pi) * cluster_data[:, 1]
            hy = np.sin(cluster_data[:, 0] * 2.0 * math.pi) * cluster_data[:, 1]
            cluster_data = np.stack([hx, hy, cluster_data[:, 2]], axis=1)
        else:
            cluster_data = face_colors

        N = cluster_data.shape[0]
        cap = min(N, max(self.num_clusters * 50, self.kmeans_subsample))
        if N > cap:
            idx = np.random.choice(N, cap, replace=False)
            sample = cluster_data[idx]
        else:
            sample = cluster_data

        K = self.num_clusters
        log(f'K-means++ init for K={K} on {sample.shape[0]} samples...')
        yield (f'K-means init K={K}...', 44)
        t_km = time.time()
        rng = np.random.default_rng(42)
        first = rng.integers(0, sample.shape[0])
        centers = [sample[first]]
        dist_sq = np.full(sample.shape[0], np.inf)
        for _ in range(K - 1):
            diff = sample - centers[-1]
            d2 = np.sum(diff * diff, axis=1)
            dist_sq = np.minimum(dist_sq, d2)
            probs = dist_sq / max(dist_sq.sum(), 1e-12)
            nxt = rng.choice(sample.shape[0], p=probs)
            centers.append(sample[nxt])
        centers = np.stack(centers, axis=0)

        for it in range(self.kmeans_iters):
            d2 = np.sum((sample[:, None, :] - centers[None, :, :]) ** 2, axis=2)
            labels = np.argmin(d2, axis=1)
            new_centers = np.zeros_like(centers)
            for c in range(K):
                mask = labels == c
                if mask.any():
                    new_centers[c] = sample[mask].mean(axis=0)
                else:
                    new_centers[c] = centers[c]
            shift = float(np.linalg.norm(new_centers - centers))
            centers = new_centers
            log(f'  iter {it+1}/{self.kmeans_iters}: shift={shift:.5f}')
            pct = 44 + int(6 * (it + 1) / self.kmeans_iters)
            yield (f'K-means iter {it+1}/{self.kmeans_iters} (shift={shift:.4f})', pct)
            if shift < 1e-5:
                log(f'  converged early at iter {it+1}')
                break
        log(f'K-means done in {time.time() - t_km:.1f}s')

        log(f'Assigning {cluster_data.shape[0]} faces to nearest cluster...')
        t_assign = time.time()
        face_labels = np.empty(cluster_data.shape[0], dtype=np.int32)
        chunk = 50000
        total_chunks = (cluster_data.shape[0] + chunk - 1) // chunk
        for ci, start in enumerate(range(0, cluster_data.shape[0], chunk)):
            end = min(start + chunk, cluster_data.shape[0])
            seg = cluster_data[start:end]
            d2_seg = np.sum((seg[:, None, :] - centers[None, :, :]) ** 2, axis=2)
            face_labels[start:end] = np.argmin(d2_seg, axis=1)
            pct = 50 + int(10 * (ci + 1) / total_chunks)
            yield (f'Assigning faces {ci+1}/{total_chunks}', pct)
        log(f'Assignment done in {time.time() - t_assign:.1f}s')

        if self.merge_small_islands:
            yield ('Merging small islands: adjacency...', 60)
            reassigned = 0
            try:
                reassigned = yield from self._merge_islands_gen(obj, face_labels, log)
            except Exception as e:
                log(f'Island merge failed: {type(e).__name__}: {e} (continuing without merge)')
            log(f'Island merging reassigned {reassigned} faces')

        cluster_rgb = np.zeros((K, 3), dtype=np.float32)
        for c in range(K):
            mask = face_labels == c
            if mask.any():
                cluster_rgb[c] = face_colors[mask].mean(axis=0)

        yield ('Creating materials...', 62)
        slot_map = {}
        for c in range(K):
            if not (face_labels == c).any():
                continue
            r, g, b = float(cluster_rgb[c, 0]), float(cluster_rgb[c, 1]), float(cluster_rgb[c, 2])
            mat_name = f'EBC_Auto_{c:03d}'
            mat = bpy.data.materials.get(mat_name)
            if mat is None:
                mat = bpy.data.materials.new(mat_name)
                mat.use_nodes = True
            # always (re)write Base Color + diffuse — reused materials may carry
            # stale colour from a previous run
            if mat.use_nodes and mat.node_tree:
                for nd in mat.node_tree.nodes:
                    if nd.type == 'BSDF_PRINCIPLED':
                        nd.inputs['Base Color'].default_value = (r, g, b, 1.0); break
            mat.diffuse_color = (r, g, b, 1.0)
            slot_idx = -1
            for si, s in enumerate(obj.material_slots):
                if s.material and s.material.name == mat.name:
                    slot_idx = si; break
            if slot_idx < 0:
                obj.data.materials.append(mat)
                slot_idx = len(obj.material_slots) - 1
            slot_map[c] = slot_idx
        log(f'Materials: {len(slot_map)} non-empty buckets')

        log('Writing material_index per polygon...')
        t_w = time.time()
        # foreach_set is much faster than Python loop
        slot_arr = np.zeros(n_polys, dtype=np.int32)
        slot_lookup = np.full(K, -1, dtype=np.int32)
        for c, si in slot_map.items():
            slot_lookup[c] = si
        slot_arr = slot_lookup[face_labels]
        # any -1 entries (shouldn't happen) → 0
        slot_arr[slot_arr < 0] = 0
        obj.data.polygons.foreach_set('material_index', slot_arr)
        obj.data.update()
        log(f'Material indices written in {time.time() - t_w:.1f}s')
        yield ('Material indices written', 70)

        if self.remove_modifier:
            try:
                obj.modifiers.remove(obj.modifiers['KIRI_Edit_By_Colour_GN'])
                log('Removed KIRI_Edit_By_Colour_GN modifier')
            except Exception as e:
                log(f'Could not remove modifier: {e}')
            yield ('Modifier removed', 72)

        # Add Solidify modifier before separation so each separated object
        # inherits a copy — open surfaces become closed volumes for slicers.
        solidify_mm = float(getattr(self, 'solidify_thickness', 0.0))
        if solidify_mm > 0.0:
            mod = obj.modifiers.new('EBC_Solidify', 'SOLIDIFY')
            mod.thickness = solidify_mm
            mod.offset = 0.0        # even thickness
            mod.use_even_offset = True
            mod.use_quality_normals = True
            log(f'Added Solidify modifier (thickness={solidify_mm*1000:.1f}mm)')

        if self.do_separate and self.progressive_separate:
            log('Progressive separate via material_slot_select...')
            t_sep = time.time()
            unique_labels = sorted(set(int(x) for x in face_labels) & set(slot_map.keys()))
            to_split = unique_labels[:-1]
            total = len(to_split)
            log(f'  {total} separate calls planned')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='FACE')
            for ki, c in enumerate(to_split):
                try:
                    active = context.view_layer.objects.active
                    if active is None:
                        log('  no active object — stopping'); break
                    target_mi = slot_map[c]
                    active.active_material_index = target_mi
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.material_slot_select()
                    objs_before = set(bpy.data.objects)
                    bpy.ops.mesh.separate(type='SELECTED')
                    new_objs = set(bpy.data.objects) - objs_before
                    n_new = sum(len(o.data.polygons) for o in new_objs)
                    elapsed = time.time() - t_sep
                    eta = elapsed * (total - (ki + 1)) / max(ki + 1, 1)
                    log(f'  separated {ki+1}/{total} (cluster {c}, {n_new} faces) elapsed {elapsed:.1f}s ETA {eta:.1f}s')
                    pct = 72 + int(26 * (ki + 1) / total)
                    yield (f'Separating {ki+1}/{total} (ETA {eta:.0f}s)', pct)
                except Exception as e:
                    log(f'  ERROR iter {ki+1}: {type(e).__name__}: {e}')
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except Exception: pass
            log(f'Progressive separation done in {time.time() - t_sep:.1f}s')
        elif self.do_separate:
            log('Separating by material (atomic)...')
            yield ('Separating by material (atomic, no progress)', 75)
            t_sep = time.time()
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            try:
                bpy.ops.mesh.separate(type='MATERIAL')
            except RuntimeError as e:
                log(f'Separate failed: {e}')
            bpy.ops.object.mode_set(mode='OBJECT')
            log(f'Separation done in {time.time() - t_sep:.1f}s')

        log(f'=== DONE in {time.time() - t_start:.1f}s — {len(slot_map)} non-empty clusters of {K} ===')
        yield (f'Done — {len(slot_map)} clusters', 100)
        self.report({'INFO'}, f'Auto split: {len(slot_map)} non-empty clusters of {K}')

    def _merge_islands_gen(self, obj, face_labels, log):
        """Generator that finds connected islands per cluster and merges small
        ones into their majority neighbor cluster. Mutates face_labels in place.
        Yields status strings (no pct — caller wraps in its own range).
        Returns number of reassigned faces via final yield value (StopIteration.value).
        """
        import numpy as np, time
        from collections import defaultdict
        mesh = obj.data
        n_polys = len(mesh.polygons)
        n_loops = len(mesh.loops)
        n_verts = len(mesh.vertices)
        if n_polys == 0 or n_loops == 0:
            return 0

        t0 = time.time()
        loop_edge = np.empty(n_loops, dtype=np.int32)
        mesh.loops.foreach_get('edge_index', loop_edge)
        loop_verts = np.empty(n_loops, dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', loop_verts)
        poly_loop_start = np.empty(n_polys, dtype=np.int32)
        mesh.polygons.foreach_get('loop_start', poly_loop_start)
        poly_loop_total = np.empty(n_polys, dtype=np.int32)
        mesh.polygons.foreach_get('loop_total', poly_loop_total)
        poly_of_loop = np.empty(n_loops, dtype=np.int32)
        for pi in range(n_polys):
            s = int(poly_loop_start[pi]); t = int(poly_loop_total[pi])
            poly_of_loop[s:s + t] = pi
        log(f'  adjacency arrays built in {time.time() - t0:.1f}s')
        yield ('Merging islands: sorting edges...', 61)

        # Pair faces sharing the same edge
        sort_idx = np.argsort(loop_edge, kind='stable')
        sorted_edges = loop_edge[sort_idx]
        sorted_polys = poly_of_loop[sort_idx]
        same_edge = sorted_edges[1:] == sorted_edges[:-1]
        pair_a = sorted_polys[:-1][same_edge]
        pair_b = sorted_polys[1:][same_edge]
        log(f'  {len(pair_a)} adjacent face pairs')
        # world vertex coords — built ONCE, reused each iter
        v_co = np.empty(n_verts * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', v_co)
        v_co = v_co.reshape(n_verts, 3)
        M = np.array(obj.matrix_world, dtype=np.float32)
        R = M[:3, :3]; T = M[:3, 3]
        v_world = v_co @ R.T + T

        min_x = float(self.min_island_size_x)
        min_y = float(self.min_island_size_y)
        min_z = float(self.min_island_size_z)
        min_w = float(self.min_island_feature_width)
        min_faces = int(self.min_island_face_count)
        max_iters = int(getattr(self, 'merge_max_iters', 8))

        reassigned = 0
        for it in range(max_iters):
            yield (f'Merging islands iter {it+1}/{max_iters}: union-find...', 62)

            # Union-find within same cluster label (fresh each iter)
            parent = np.arange(n_polys, dtype=np.int32)

            def find(x, parent=parent):
                r = x
                while parent[r] != r:
                    r = parent[r]
                while parent[x] != r:
                    parent[x], x = r, parent[x]
                return r

            same_label_mask = face_labels[pair_a] == face_labels[pair_b]
            pa = pair_a[same_label_mask].tolist()
            pb = pair_b[same_label_mask].tolist()
            for a, b in zip(pa, pb):
                ra = find(a); rb = find(b)
                if ra != rb:
                    if ra < rb:
                        parent[rb] = ra
                    else:
                        parent[ra] = rb
            for i in range(n_polys):
                find(i)

            comp_faces = defaultdict(list)
            for pi in range(n_polys):
                comp_faces[int(parent[pi])].append(pi)

            # bbox + OBB per component
            comp_bbox = {}
            comp_obb_min = {}
            for root, faces in comp_faces.items():
                vis = []
                for fi in faces:
                    s = int(poly_loop_start[fi]); t = int(poly_loop_total[fi])
                    vis.append(loop_verts[s:s + t])
                vi = np.concatenate(vis) if vis else np.empty(0, dtype=np.int32)
                if vi.size == 0:
                    comp_bbox[root] = (np.zeros(3), np.zeros(3))
                    comp_obb_min[root] = 0.0
                    continue
                uniq = np.unique(vi)
                vs = v_world[uniq]
                comp_bbox[root] = (vs.min(axis=0), vs.max(axis=0))
                if vs.shape[0] >= 3:
                    mean = vs.mean(axis=0)
                    centered = vs - mean
                    try:
                        cov = centered.T @ centered / max(1, vs.shape[0] - 1)
                        _ev, evecs = np.linalg.eigh(cov.astype(np.float64))
                        projected = centered.astype(np.float64) @ evecs
                        obb_ext = projected.max(axis=0) - projected.min(axis=0)
                        comp_obb_min[root] = float(obb_ext.min())
                    except np.linalg.LinAlgError:
                        extent = comp_bbox[root][1] - comp_bbox[root][0]
                        comp_obb_min[root] = float(extent.min())
                else:
                    extent = comp_bbox[root][1] - comp_bbox[root][0]
                    comp_obb_min[root] = float(extent.min())

            small_roots = set()
            hist_faces = {'<5': 0, '5-20': 0, '20-100': 0, '100-1000': 0, '1000+': 0}
            hist_obb = {'<1mm': 0, '1-3mm': 0, '3-10mm': 0, '10-50mm': 0, '50mm+': 0}
            for root, faces in comp_faces.items():
                n_f = len(faces)
                bmin, bmax = comp_bbox[root]
                extent = bmax - bmin
                dx, dy, dz = float(extent[0]), float(extent[1]), float(extent[2])
                obb_w = comp_obb_min.get(root, 0.0)
                if n_f < 5: hist_faces['<5'] += 1
                elif n_f < 20: hist_faces['5-20'] += 1
                elif n_f < 100: hist_faces['20-100'] += 1
                elif n_f < 1000: hist_faces['100-1000'] += 1
                else: hist_faces['1000+'] += 1
                if obb_w < 0.001: hist_obb['<1mm'] += 1
                elif obb_w < 0.003: hist_obb['1-3mm'] += 1
                elif obb_w < 0.010: hist_obb['3-10mm'] += 1
                elif obb_w < 0.050: hist_obb['10-50mm'] += 1
                else: hist_obb['50mm+'] += 1
                too_small = False
                if min_faces > 0 and n_f < min_faces: too_small = True
                if min_x > 0.0 and dx < min_x: too_small = True
                if min_y > 0.0 and dy < min_y: too_small = True
                if min_z > 0.0 and dz < min_z: too_small = True
                if min_w > 0.0 and obb_w < min_w: too_small = True
                if too_small:
                    small_roots.add(root)
            log(f'  iter {it+1}: {len(comp_faces)} components, {len(small_roots)} small')
            log(f'    faces hist: {hist_faces}')
            log(f'    OBB hist:   {hist_obb}')

            if not small_roots:
                log(f'  converged at iter {it+1}')
                break

            # Adjacency between components via cross-component edge pairs
            roots_a = parent[pair_a]
            roots_b = parent[pair_b]
            cross_mask = roots_a != roots_b
            cra = roots_a[cross_mask].tolist()
            crb = roots_b[cross_mask].tolist()

            # shared-boundary length per (small_root, neighbor_root): count cross-edges
            small_neighbors = defaultdict(lambda: defaultdict(int))
            for ra, rb in zip(cra, crb):
                if ra in small_roots:
                    small_neighbors[ra][rb] += 1
                if rb in small_roots:
                    small_neighbors[rb][ra] += 1

            yield (f'Merging islands iter {it+1}/{max_iters}: reassigning...', 65)
            iter_reassigned = 0
            for root in small_roots:
                nbrs = small_neighbors.get(root)
                if not nbrs:
                    continue
                # prefer non-small neighbors; fall back to small ones
                non_small = {c: w for c, w in nbrs.items() if c not in small_roots}
                pool = non_small if non_small else nbrs
                # pick by longest shared boundary; tie-break by neighbor size
                target = max(pool.items(), key=lambda kv: (kv[1], len(comp_faces[kv[0]])))[0]
                target_label = int(face_labels[comp_faces[target][0]])
                faces = comp_faces[root]
                face_labels[faces] = target_label
                iter_reassigned += len(faces)

            log(f'  iter {it+1}: reassigned {iter_reassigned} faces')
            reassigned += iter_reassigned
            if iter_reassigned == 0:
                log(f'  no progress at iter {it+1}, stopping')
                break

        # Optional morphological erosion passes
        passes = int(getattr(self, 'erosion_passes', 0))
        if passes > 0:
            yield ('Merging islands: erosion setup...', 66)
            all_a = np.concatenate([pair_a, pair_b])
            all_b = np.concatenate([pair_b, pair_a])
            sort_idx = np.argsort(all_a, kind='stable')
            sorted_a = all_a[sort_idx]
            sorted_b = all_b[sort_idx]
            unique_faces, start_idx, counts = np.unique(sorted_a, return_index=True, return_counts=True)
            uf_list = unique_faces.tolist()
            st_list = start_idx.tolist()
            ct_list = counts.tolist()
            strength = float(getattr(self, 'erosion_strength', 0.7))
            log(f'  erosion strength threshold = {strength}')
            erosion_total = 0
            prev_changed = None
            for pass_i in range(passes):
                yield (f'Erosion pass {pass_i+1}/{passes}...', min(68 + pass_i, 72))
                neighbor_labels = face_labels[sorted_b]
                new_labels = face_labels.copy()
                changed = 0
                for fi, st, ct in zip(uf_list, st_list, ct_list):
                    nb = neighbor_labels[st:st + ct]
                    cur = int(face_labels[fi])
                    same = int((nb == cur).sum())
                    # flip if same-fraction below strength
                    if ct > 0 and (same / ct) < strength:
                        mn = int(np.bincount(nb).argmax())
                        if mn != cur:
                            new_labels[fi] = mn
                            changed += 1
                face_labels[:] = new_labels
                erosion_total += changed
                log(f'  erosion pass {pass_i+1}: changed {changed} faces')
                if changed == 0:
                    log('  erosion converged, stopping early')
                    break
                # Oscillation detection: if change count is plateauing high, stop
                if prev_changed is not None and abs(changed - prev_changed) < max(100, prev_changed // 50):
                    log(f'  erosion oscillating around {changed} flips/pass, stopping (limit cycle)')
                    break
                prev_changed = changed
            log(f'  total erosion changes: {erosion_total}')
            reassigned += erosion_total
        return reassigned

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'num_clusters')
        layout.prop(self, 'samples_per_face')
        layout.prop(self, 'use_hsv')
        layout.prop(self, 'do_separate')
        layout.prop(self, 'progressive_separate')
        layout.prop(self, 'remove_modifier')
        layout.prop(self, 'solidify_thickness')
        layout.separator()
        layout.prop(self, 'merge_small_islands')
        sub = layout.column(align=True)
        sub.enabled = self.merge_small_islands
        sub.label(text='Axis-aligned bbox thresholds (0 = ignore):')
        sub.prop(self, 'min_island_size_x')
        sub.prop(self, 'min_island_size_y')
        sub.prop(self, 'min_island_size_z')
        sub.label(text='Oriented bbox / face count:')
        sub.prop(self, 'min_island_feature_width')
        sub.prop(self, 'min_island_face_count')
        sub.prop(self, 'merge_max_iters')
        sub.label(text='Morphological smoothing:')
        sub.prop(self, 'erosion_passes')
        sub.prop(self, 'erosion_strength')
        col = layout.column(align=True)
        col.label(text='Advanced:')
        col.prop(self, 'kmeans_iters')
        col.prop(self, 'kmeans_subsample')


class SNA_OT_voxel_block_remesh(bpy.types.Operator):
    bl_idname = 'sna.voxel_block_remesh'
    bl_label = 'Voxel Block Remesh'
    bl_description = 'Octree voxel remesh: convert textured mesh into colored blocks (Minecraft-style). Each occupied voxel becomes a cube face, colored by texture sampling, then quantized into K palette colors via k-means'
    bl_options = {'REGISTER', 'UNDO'}

    cell_size_mm: bpy.props.FloatProperty(
        name='Block Size (mm)', default=5.0, min=0.5, max=100.0,
        description='Size of each block/cube in millimeters. Smaller = finer blocks, more geometry',
        precision=1, step=10,
    )
    num_colors: bpy.props.IntProperty(
        name='Total Colors', default=16, min=2, max=256,
        description='Number of palette colors (K for k-means). Each color becomes one material',
    )
    kmeans_iters: bpy.props.IntProperty(
        name='K-means Iterations', default=20, min=2, max=100,
    )
    kmeans_subsample: bpy.props.IntProperty(
        name='K-means Sample Cap', default=20000, min=500, max=200000,
        description='Cap face-color samples for k-means clustering to keep it fast',
    )
    use_hsv: bpy.props.BoolProperty(
        name='Cluster in HSV', default=True,
        description='K-means in HSV space (better perceptual grouping). Off = RGB',
    )
    do_separate: bpy.props.BoolProperty(
        name='Separate by Color', default=True,
        description='Separate the result into one mesh object per material/color',
    )
    remove_original: bpy.props.BoolProperty(
        name='Remove Original', default=False,
        description='Remove the source mesh object after the remesh is built',
    )

    _SPIN = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):
        import numpy as np

        obj = context.view_layer.objects.active
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, 'No active mesh'); return {'CANCELLED'}
        mod = obj.modifiers.get('KIRI_Edit_By_Colour_GN')
        if mod is None:
            self.report({'ERROR'}, 'Add Edit By Colour modifier first'); return {'CANCELLED'}
        try: uv_name = mod['Socket_2']
        except Exception: uv_name = ''
        try: image = mod['Socket_4']
        except Exception: image = None
        if not uv_name or uv_name not in obj.data.uv_layers:
            self.report({'ERROR'}, 'UV Map not set in modifier'); return {'CANCELLED'}
        if image is None:
            self.report({'ERROR'}, 'Base Texture not set in modifier'); return {'CANCELLED'}
        if image.size[0] == 0 or image.size[1] == 0:
            self.report({'ERROR'}, 'Image has zero size'); return {'CANCELLED'}

        self._gen = self._work(context, obj, image, uv_name)
        self._spin_idx = 0
        self._last_text = ''
        try:
            first = next(self._gen)
            self._apply_status(context, first)
        except StopIteration:
            self._cleanup(context)
            return {'FINISHED'}
        except Exception as e:
            self._cleanup(context)
            self.report({'ERROR'}, f'{type(e).__name__}: {e}')
            return {'CANCELLED'}
        wm = context.window_manager
        wm.progress_begin(0, 100)
        self._timer = wm.event_timer_add(0.08, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            print('[VoxelRemesh] cancelled by ESC', flush=True)
            self._cleanup(context)
            self.report({'WARNING'}, 'Voxel Block Remesh cancelled')
            return {'CANCELLED'}
        if event.type == 'TIMER':
            try:
                status = next(self._gen)
                self._apply_status(context, status)
            except StopIteration:
                self._cleanup(context)
                return {'FINISHED'}
            except Exception as e:
                print(f'[VoxelRemesh] FAILED: {type(e).__name__}: {e}', flush=True)
                self._cleanup(context)
                self.report({'ERROR'}, f'{type(e).__name__}: {e}')
                return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def _apply_status(self, context, status):
        if isinstance(status, tuple):
            if len(status) >= 2:
                text, pct = status[0], status[1]
            elif len(status) == 1:
                text, pct = status[0], None
            else:
                text, pct = str(status), None
        else:
            text, pct = status, None
        self._spin_idx = (self._spin_idx + 1) % len(self._SPIN)
        spin = self._SPIN[self._spin_idx]
        full = f'{spin}  EBC Voxel Remesh: {text}   (ESC to cancel)'
        try:
            if context.workspace:
                context.workspace.status_text_set(full)
        except Exception:
            pass
        if pct is not None:
            try: context.window_manager.progress_update(max(0, min(100, int(pct))))
            except Exception: pass
        self._last_text = text

    def _cleanup(self, context):
        wm = context.window_manager
        if getattr(self, '_timer', None) is not None:
            try: wm.event_timer_remove(self._timer)
            except Exception: pass
            self._timer = None
        try: wm.progress_end()
        except Exception: pass
        try:
            if context.workspace:
                context.workspace.status_text_set(None)
        except Exception:
            pass

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'cell_size_mm')
        layout.prop(self, 'num_colors')
        layout.prop(self, 'use_hsv')
        layout.prop(self, 'do_separate')
        layout.prop(self, 'remove_original')
        col = layout.column(align=True)
        col.label(text='Advanced:')
        col.prop(self, 'kmeans_iters')
        col.prop(self, 'kmeans_subsample')

    def _work(self, context, obj, image, uv_name):
        """Generator: yields ('text', pct 0..100). Core voxel remesh pipeline."""
        import math, time
        import numpy as np

        def log(msg):
            print(f'[VoxelRemesh] {msg}', flush=True)

        t_start = time.time()
        log(f'=== Voxel Block Remesh: cell={self.cell_size_mm:.1f}mm, K={self.num_colors}, HSV={self.use_hsv} ===')

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Face directions: +X, -X, +Y, -Y, +Z, -Z (constant across all phases)
        DIRS = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

        # Phase 1: Read image
        w_img, h_img = image.size[0], image.size[1]
        yield (f'Reading image {w_img}x{h_img}...', 0)
        npx = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(npx)
        img = npx.reshape(h_img, w_img, 4)[:, :, :3]
        log(f'Image read in {time.time() - t_start:.1f}s')

        # Phase 2: Build BVHTree from world-space mesh
        yield ('Building BVHTree...', 2)
        t_bvh = time.time()
        mesh = obj.data
        n_verts = len(mesh.vertices)
        n_polys = len(mesh.polygons)
        if n_polys == 0:
            raise RuntimeError('Mesh has no polygons')

        # Collect world-space vertices
        verts_local = np.empty(n_verts * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', verts_local)
        verts_local = verts_local.reshape(n_verts, 3)
        M = np.array(obj.matrix_world, dtype=np.float32)
        verts_world = verts_local @ M[:3, :3].T + M[:3, 3]

        # Build BVHTree (needs Python list of coords + list of index-triplets)
        import mathutils
        verts_list = verts_world.tolist()
        polys_list = []
        poly_loop_start = np.empty(n_polys, dtype=np.int32)
        poly_loop_total = np.empty(n_polys, dtype=np.int32)
        mesh.polygons.foreach_get('loop_start', poly_loop_start)
        mesh.polygons.foreach_get('loop_total', poly_loop_total)
        loop_verts = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', loop_verts)

        # Build mapping: BVH face index -> (original polygon index, sub-triangle index)
        bvh_face_to_poly = []
        for pi in range(n_polys):
            s = int(poly_loop_start[pi]); t = int(poly_loop_total[pi])
            vs = loop_verts[s:s + t].tolist()
            # Triangulate n-gon for BVH
            for ti in range(1, t - 1):
                polys_list.append((vs[0], vs[ti], vs[ti + 1]))
                bvh_face_to_poly.append((pi, ti))

        bvh = mathutils.bvhtree.BVHTree.FromPolygons(verts_list, polys_list)
        log(f'BVHTree built ({len(polys_list)} tris) in {time.time() - t_bvh:.1f}s')

        # Phase 3: Voxel occupancy via surface sampling (fast)
        cell_size = self.cell_size_mm / 1000.0  # mm → meters (Blender units)
        log(f'Voxel grid: cell_size={self.cell_size_mm:.1f}mm ({cell_size:.4f}m)')

        # Axis-aligned bounding box with margin
        bbox_min = np.min(verts_world, axis=0) - cell_size
        bbox_max = np.max(verts_world, axis=0) + cell_size
        # Snap to cell grid
        grid_size_x = int(np.ceil((bbox_max[0] - bbox_min[0]) / cell_size))
        grid_size_y = int(np.ceil((bbox_max[1] - bbox_min[1]) / cell_size))
        grid_size_z = int(np.ceil((bbox_max[2] - bbox_min[2]) / cell_size))
        bbox_max = bbox_min + np.array([grid_size_x, grid_size_y, grid_size_z], dtype=np.float32) * cell_size
        total_cells = grid_size_x * grid_size_y * grid_size_z
        log(f'Grid: {grid_size_x}×{grid_size_y}×{grid_size_z} = {total_cells} cells, bbox=[{bbox_min}] → [{bbox_max}]')

        yield (f'Grid: {grid_size_x}×{grid_size_y}×{grid_size_z} = {total_cells} cells', 3)

        # Phase 3: Voxel occupancy via vertex seeding + BVH verification
        # 1. Seed cells from every mesh vertex (guaranteed occupied)
        # 2. 2-ring expand to get surface band
        # 3. BVH find_nearest per band cell to verify surface proximity
        half_diag = cell_size * math.sqrt(3) * 0.5
        log(f'Voxel grid: half_diag={half_diag*1000:.2f}mm')
        yield ('Seeding cells from mesh vertices...', 5)
        t_occ = time.time()

        occupied = set()
        # Step 1: vertex seeding
        for vi in range(n_verts):
            v = verts_world[vi]
            ix = int((v[0] - bbox_min[0]) / cell_size)
            iy = int((v[1] - bbox_min[1]) / cell_size)
            iz = int((v[2] - bbox_min[2]) / cell_size)
            if 0 <= ix < grid_size_x and 0 <= iy < grid_size_y and 0 <= iz < grid_size_z:
                occupied.add((ix, iy, iz))
        log(f'Vertex seeds: {len(occupied)} cells, in {time.time() - t_occ:.1f}s')
        yield (f'{len(occupied)} vertex cells', 8)

        # Step 2: 1-ring expand
        seeds = list(occupied)
        for (ix, iy, iz) in seeds:
            for dx, dy, dz in DIRS:
                nx, ny, nz = ix + dx, iy + dy, iz + dz
                if 0 <= nx < grid_size_x and 0 <= ny < grid_size_y and 0 <= nz < grid_size_z:
                    occupied.add((nx, ny, nz))
        band1 = list(occupied - set(seeds))
        log(f'1-ring expand: {len(occupied)} cells')
        yield (f'{len(occupied)} cells after 1-ring expand', 10)

        # Step 3: 2-ring expand (candidates for BVH check)
        candidates = set()
        for (ix, iy, iz) in band1:
            for dx, dy, dz in DIRS:
                nx, ny, nz = ix + dx, iy + dy, iz + dz
                if 0 <= nx < grid_size_x and 0 <= ny < grid_size_y and 0 <= nz < grid_size_z:
                    nk = (nx, ny, nz)
                    if nk not in occupied:
                        candidates.add(nk)
        log(f'2-ring candidates: {len(candidates)} cells')
        yield (f'{len(candidates)} BVH candidates', 12)

        # Step 4: BVH verify each candidate
        verified = 0
        rejected = 0
        cand_list = list(candidates)
        chunk = 10000
        for ci, start in enumerate(range(0, len(cand_list), chunk)):
            end = min(start + chunk, len(cand_list))
            for i in range(start, end):
                ix, iy, iz = cand_list[i]
                cx = bbox_min[0] + (ix + 0.5) * cell_size
                cy = bbox_min[1] + (iy + 0.5) * cell_size
                cz = bbox_min[2] + (iz + 0.5) * cell_size
                nearest = bvh.find_nearest(mathutils.Vector((cx, cy, cz)))
                if nearest is not None and nearest[3] < half_diag:
                    occupied.add((ix, iy, iz))
                    verified += 1
                else:
                    rejected += 1
            pct = 12 + int(5 * (ci + 1) / max(1, (len(cand_list) + chunk - 1) // chunk))
            yield (f'BVH verifying {end}/{len(cand_list)} (+{verified}/-{rejected})', pct)

        log(f'BVH verified: +{verified} -{rejected}, total occupied={len(occupied)} in {time.time() - t_occ:.1f}s')
        yield (f'{len(occupied)} occupied cells (+{verified} BVH verified)', 17)

        # Phase 3b: Cull inside-facing cells. Keep only cells on the OUTSIDE
        # of the mesh surface (like Blender Remesh Blocks exterior shell).
        yield ('Culling interior cells...', 18)
        t_cull = time.time()
        inside = []
        occ_list = list(occupied)
        for i, (ix, iy, iz) in enumerate(occ_list):
            cx = bbox_min[0] + (ix + 0.5) * cell_size
            cy = bbox_min[1] + (iy + 0.5) * cell_size
            cz = bbox_min[2] + (iz + 0.5) * cell_size
            nearest = bvh.find_nearest(mathutils.Vector((cx, cy, cz)))
            if nearest is not None:
                hit_loc, hit_norm, _, _ = nearest
                # cell_center to surface: positive = outside (same dir as normal)
                to_cell = mathutils.Vector((cx - hit_loc[0], cy - hit_loc[1], cz - hit_loc[2]))
                if to_cell.dot(hit_norm) < 0:
                    inside.append((ix, iy, iz))
            if i % 10000 == 0 and i > 0:
                yield (f'Culling {i}/{len(occ_list)}...', 18)
        for k in inside:
            occupied.discard(k)
        log(f'Culled {len(inside)} interior cells, {len(occupied)} exterior remain, in {time.time() - t_cull:.1f}s')
        yield (f'{len(occupied)} exterior cells (culled {len(inside)} interior)', 20)

        # Phase 4: Surface face extraction - keep face only if neighbor is empty
        yield ('Extracting surface faces...', 22)
        t_faces = time.time()
        # For each face, we store: (ix, iy, iz, dir_idx)
        faces_to_emit = []
        for (ix, iy, iz) in occupied:
            for di, (dx, dy, dz) in enumerate(DIRS):
                neighbor = (ix + dx, iy + dy, iz + dz)
                if neighbor not in occupied:
                    faces_to_emit.append((ix, iy, iz, di))
        log(f'Surface faces: {len(faces_to_emit)} (culled from {len(occupied) * 6} potential) in {time.time() - t_faces:.1f}s')
        yield (f'{len(faces_to_emit)} surface faces', 25)

        # Phase 5: Color sampling per face via BVHTree -> UV -> texture
        yield ('Sampling texture color per face...', 27)
        t_color = time.time()
        uv_layer = mesh.uv_layers[uv_name].data
        face_colors = np.zeros((len(faces_to_emit), 3), dtype=np.float32)
        M_inv = np.array(obj.matrix_world.inverted(), dtype=np.float32)

        for fi, (ix, iy, iz, di) in enumerate(faces_to_emit):
            # Voxel center
            vx = bbox_min[0] + (ix + 0.5) * cell_size
            vy = bbox_min[1] + (iy + 0.5) * cell_size
            vz = bbox_min[2] + (iz + 0.5) * cell_size
            # Face center (offset by half cell in the face-normal direction)
            dx, dy, dz = DIRS[di]
            fc = mathutils.Vector((vx + dx * cell_size * 0.5, vy + dy * cell_size * 0.5, vz + dz * cell_size * 0.5))

            nearest = bvh.find_nearest(fc)
            if nearest is None:
                continue
            hit_loc, hit_norm, bvh_face_idx, dist = nearest

            # Get original polygon index + sub-triangle
            poly_idx, sub_ti = bvh_face_to_poly[bvh_face_idx]
            poly = mesh.polygons[poly_idx]
            li = poly.loop_indices
            ln = poly.loop_total

            if ln < 3:
                continue

            # Barycentric interpolation of UV at hit_location
            # Use the correct sub-triangle from BVH triangulation
            uv0 = uv_layer[li[0]].uv
            uv1 = uv_layer[li[sub_ti]].uv
            uv2 = uv_layer[li[sub_ti + 1]].uv

            # Transform hit to local space for barycentric computation
            hit_local_pt = M_inv[:3, :3] @ np.array(hit_loc, dtype=np.float32) + M_inv[:3, 3]

            v0_local = verts_local[poly.vertices[0]]
            v1_local = verts_local[poly.vertices[sub_ti]]
            v2_local = verts_local[poly.vertices[sub_ti + 1]]

            # Barycentric weights in 3D space
            e0 = v1_local - v0_local
            e1 = v2_local - v0_local
            ep = hit_local_pt - v0_local
            d00 = float(np.dot(e0, e0)); d01 = float(np.dot(e0, e1))
            d11 = float(np.dot(e1, e1)); dp0 = float(np.dot(ep, e0))
            dp1 = float(np.dot(ep, e1))
            denom = d00 * d11 - d01 * d01
            if abs(denom) < 1e-12:
                u = 0.0; v = 0.0; w = 1.0  # degenerate -> use v0
            else:
                v = (d11 * dp0 - d01 * dp1) / denom
                w = (d00 * dp1 - d01 * dp0) / denom
                u = 1.0 - v - w

            # Clamp barycentric coords to [0,1] (hit_loc may be slightly outside triangle)
            u = max(0.0, min(1.0, u))
            v = max(0.0, min(1.0, v))
            w = max(0.0, min(1.0, w))
            total = u + v + w
            if total > 1e-8:
                u /= total; v /= total; w /= total

            # Interpolate UV
            u_hit = u * uv0[0] + v * uv1[0] + w * uv2[0]
            v_hit = u * uv0[1] + v * uv1[1] + w * uv2[1]
            u_hit = u_hit - math.floor(u_hit)
            v_hit = v_hit - math.floor(v_hit)

            # Sample texture (nearest-neighbor)
            tx = min(w_img - 1, int(u_hit * w_img))
            ty = min(h_img - 1, int(v_hit * h_img))
            face_colors[fi, 0] = img[ty, tx, 0]
            face_colors[fi, 1] = img[ty, tx, 1]
            face_colors[fi, 2] = img[ty, tx, 2]

            if fi % 10000 == 0 and fi > 0:
                pct = 22 + int(18 * fi / len(faces_to_emit))
                yield (f'Sampling colors {fi}/{len(faces_to_emit)}...', pct)

        log(f'Color sampling done in {time.time() - t_color:.1f}s')
        yield (f'Colors sampled ({len(faces_to_emit)} faces)', 40)

        # Phase 6: K-means palette
        K = self.num_colors
        log(f'K-means: K={K}, iters={self.kmeans_iters}, cap={self.kmeans_subsample}')
        yield (f'K-means palette K={K}...', 42)

        t_km = time.time()
        if self.use_hsv:
            cluster_data = _sna_rgb_to_hsv_np(face_colors)
            # Circular hue encoding
            hx = np.cos(cluster_data[:, 0] * 2.0 * math.pi) * cluster_data[:, 1]
            hy = np.sin(cluster_data[:, 0] * 2.0 * math.pi) * cluster_data[:, 1]
            cluster_data = np.stack([hx, hy, cluster_data[:, 2]], axis=1)
        else:
            cluster_data = face_colors.copy()

        N = cluster_data.shape[0]
        cap = min(N, max(K * 50, self.kmeans_subsample))
        if N > cap:
            idx = np.random.choice(N, cap, replace=False)
            sample = cluster_data[idx]
        else:
            sample = cluster_data

        rng = np.random.default_rng(42)
        first = rng.integers(0, sample.shape[0])
        centers = [sample[first]]
        dist_sq = np.full(sample.shape[0], np.inf)
        for _ in range(K - 1):
            diff = sample - centers[-1]
            d2 = np.sum(diff * diff, axis=1)
            dist_sq = np.minimum(dist_sq, d2)
            probs = dist_sq / max(dist_sq.sum(), 1e-12)
            nxt = rng.choice(sample.shape[0], p=probs)
            centers.append(sample[nxt])
        centers = np.stack(centers, axis=0)

        for it in range(self.kmeans_iters):
            d2 = np.sum((sample[:, None, :] - centers[None, :, :]) ** 2, axis=2)
            labels = np.argmin(d2, axis=1)
            new_centers = np.zeros_like(centers)
            for c in range(K):
                mask = labels == c
                if mask.any():
                    new_centers[c] = sample[mask].mean(axis=0)
                else:
                    new_centers[c] = centers[c]
            shift = float(np.linalg.norm(new_centers - centers))
            centers = new_centers
            pct = 42 + int(6 * (it + 1) / self.kmeans_iters)
            yield (f'K-means {it+1}/{self.kmeans_iters} (shift={shift:.4f})', pct)
            if shift < 1e-5:
                log(f'  converged early at iter {it+1}')
                break
        log(f'K-means done in {time.time() - t_km:.1f}s')

        # Phase 7: Assign each face to nearest cluster center
        yield ('Assigning faces to palette...', 50)
        t_assign = time.time()
        face_labels = np.empty(cluster_data.shape[0], dtype=np.int32)
        chunk = 50000
        total_chunks = (cluster_data.shape[0] + chunk - 1) // chunk
        for ci, start in enumerate(range(0, cluster_data.shape[0], chunk)):
            end = min(start + chunk, cluster_data.shape[0])
            seg = cluster_data[start:end]
            d2_seg = np.sum((seg[:, None, :] - centers[None, :, :]) ** 2, axis=2)
            face_labels[start:end] = np.argmin(d2_seg, axis=1)
            pct = 50 + int(5 * (ci + 1) / total_chunks)
            yield (f'Assigning {ci+1}/{total_chunks}...', pct)
        log(f'Assignment done in {time.time() - t_assign:.1f}s')

        # Phase 8: Create materials (one per non-empty cluster)
        yield ('Creating materials...', 56)
        if self.use_hsv:
            # Recover HSV from encoded centroids (hx=cos(H)*S, hy=sin(H)*S, V)
            h_recovered = (np.arctan2(centers[:, 1], centers[:, 0]) / (2.0 * math.pi)) % 1.0
            s_recovered = np.sqrt(centers[:, 0]**2 + centers[:, 1]**2)
            s_recovered = np.clip(s_recovered, 0.0, 1.0)
            v_recovered = centers[:, 2]
            cluster_rgb = np.zeros((K, 3), dtype=np.float32)
            import colorsys
            for c in range(K):
                r, g, b = colorsys.hsv_to_rgb(float(h_recovered[c]), float(s_recovered[c]), float(v_recovered[c]))
                cluster_rgb[c] = (r, g, b)
        else:
            cluster_rgb = np.zeros((K, 3), dtype=np.float32)
            for c in range(K):
                mask = face_labels == c
                if mask.any():
                    cluster_rgb[c] = face_colors[mask].mean(axis=0)

        slot_map = {}
        for c in range(K):
            if not (face_labels == c).any():
                continue
            r, g, b = float(cluster_rgb[c, 0]), float(cluster_rgb[c, 1]), float(cluster_rgb[c, 2])
            mat_name = f'EBC_Voxel_{c:03d}'
            mat = bpy.data.materials.get(mat_name)
            if mat is None:
                mat = bpy.data.materials.new(mat_name)
                mat.use_nodes = True
            if mat.use_nodes and mat.node_tree:
                for nd in mat.node_tree.nodes:
                    if nd.type == 'BSDF_PRINCIPLED':
                        nd.inputs['Base Color'].default_value = (r, g, b, 1.0); break
            mat.diffuse_color = (r, g, b, 1.0)
            slot_idx = -1
            for si, s in enumerate(obj.material_slots):
                if s.material and s.material.name == mat.name:
                    slot_idx = si; break
            if slot_idx < 0:
                obj.data.materials.append(mat)
                slot_idx = len(obj.material_slots) - 1
            slot_map[c] = slot_idx
        log(f'Materials: {len(slot_map)} non-empty clusters')
        yield (f'{len(slot_map)} materials created', 60)

        # Phase 9: Build output geometry via bmesh
        yield ('Building block geometry...', 62)
        t_geo = time.time()
        import bmesh

        # Create new mesh object for the result
        result_mesh = bpy.data.meshes.new(obj.name + '_Voxel')
        result_obj = bpy.data.objects.new(obj.name + '_Voxel', result_mesh)
        context.collection.objects.link(result_obj)
        result_obj.matrix_world = mathutils.Matrix.Identity(4)

        bm = bmesh.new()
        # Copy materials to result object slots
        result_slot_map = {}
        for c in slot_map:
            mat_name = f'EBC_Voxel_{c:03d}'
            mat = bpy.data.materials.get(mat_name)
            if mat is None:
                continue
            # Check if already in result object slots
            found = -1
            for si, s in enumerate(result_obj.material_slots):
                if s.material and s.material.name == mat.name:
                    found = si; break
            if found < 0:
                result_obj.data.materials.append(mat)
                found = len(result_obj.material_slots) - 1
            result_slot_map[c] = found

        def get_face_corners(ix, iy, iz, di):
            """Return 4 world-space corner positions of the face (quad, counter-clockwise from outside)."""
            dx, dy, dz = DIRS[di]
            # Cell min corner
            x0 = bbox_min[0] + ix * cell_size
            y0 = bbox_min[1] + iy * cell_size
            z0 = bbox_min[2] + iz * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            z1 = z0 + cell_size
            if di == 0:  # +X
                return [(x1,y0,z0), (x1,y1,z0), (x1,y1,z1), (x1,y0,z1)]
            elif di == 1:  # -X
                return [(x0,y0,z0), (x0,y0,z1), (x0,y1,z1), (x0,y1,z0)]
            elif di == 2:  # +Y
                return [(x0,y1,z0), (x0,y1,z1), (x1,y1,z1), (x1,y1,z0)]
            elif di == 3:  # -Y
                return [(x0,y0,z0), (x1,y0,z0), (x1,y0,z1), (x0,y0,z1)]
            elif di == 4:  # +Z
                return [(x0,y0,z1), (x1,y0,z1), (x1,y1,z1), (x0,y1,z1)]
            else:  # -Z
                return [(x0,y1,z0), (x1,y1,z0), (x1,y0,z0), (x0,y0,z0)]

        for fi, (ix, iy, iz, di) in enumerate(faces_to_emit):
            cluster = face_labels[fi]
            if cluster not in result_slot_map:
                continue  # empty cluster, skip
            corners = get_face_corners(ix, iy, iz, di)
            verts = [bm.verts.new(c) for c in corners]
            bm.verts.ensure_lookup_table()
            face = bm.faces.new(verts)  # corners already CCW from outside
            face.material_index = result_slot_map[cluster]

            if fi % 10000 == 0 and fi > 0:
                pct = 62 + int(26 * fi / len(faces_to_emit))
                yield (f'Building geometry {fi}/{len(faces_to_emit)}...', pct)

        bm.to_mesh(result_mesh)
        bm.free()
        result_mesh.update()
        log(f'Geometry built ({len(faces_to_emit)} faces) in {time.time() - t_geo:.1f}s')
        yield (f'Geometry built: {len(faces_to_emit)} faces', 88)

        # Phase 10: Separate by material (optional) and cleanup
        if self.do_separate:
            log('Separating by material...')
            yield ('Separating by material...', 92)
            t_sep = time.time()
            bpy.ops.object.select_all(action='DESELECT')
            result_obj.select_set(True)
            context.view_layer.objects.active = result_obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            try:
                bpy.ops.mesh.separate(type='MATERIAL')
            except RuntimeError as e:
                log(f'Separate warning: {e}')
            bpy.ops.object.mode_set(mode='OBJECT')
            log(f'Separation done in {time.time() - t_sep:.1f}s')

        if self.remove_original:
            log(f'Removing original object {obj.name}')
            bpy.data.objects.remove(obj, do_unlink=True)
            yield ('Original removed', 98)

        elapsed = time.time() - t_start
        log(f'=== Voxel Block Remesh finished in {elapsed:.1f}s ===')
        yield (f'Done in {elapsed:.0f}s — {len(slot_map)} colors', 100)

class SNA_OT_test_progressive_separate(bpy.types.Operator):
    bl_idname = 'sna.test_progressive_separate'
    bl_label = 'Self-Test: Progressive Separate'
    bl_description = 'Builds a synthetic plane with 4 materials, runs the same loop logic, and reports pass/fail in the console'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            import numpy as np
        except Exception:
            self.report({'ERROR'}, 'numpy not available')
            return {'CANCELLED'}

        def p(msg):
            print(f'[TestSep] {msg}', flush=True)

        p('=== test start ===')
        # Build subdivided plane
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_plane_add(location=(100, 100, 100))
        plane = context.active_object
        plane.name = '_ebc_test_plane'
        p(f'created {plane.name}')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=10)
        bpy.ops.object.mode_set(mode='OBJECT')
        n = len(plane.data.polygons)
        p(f'subdivided to {n} polys')

        # 4 materials
        mats = []
        for i in range(4):
            m = bpy.data.materials.new(f'_ebc_test_mat_{i}')
            plane.data.materials.append(m)
            mats.append(m)
        mi = np.array([i % 4 for i in range(n)], dtype=np.int32)
        plane.data.polygons.foreach_set('material_index', mi)
        plane.data.update()
        counts = [int((mi == k).sum()) for k in range(4)]
        p(f'mat counts: {counts}')

        ok = True
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        plane.select_set(True)
        context.view_layer.objects.active = plane
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        for target_mi in range(3):  # last stays on source
            p(f'--- iter mi={target_mi} ---')
            try:
                active = context.view_layer.objects.active
                p(f'  active before: {active.name if active else None}')
                active.active_material_index = target_mi
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.material_slot_select()
                before = set(bpy.data.objects)
                bpy.ops.mesh.separate(type='SELECTED')
                new = list(set(bpy.data.objects) - before)
                for o in new:
                    p(f'  new: {o.name} polys={len(o.data.polygons)}')
                active_after = context.view_layer.objects.active
                if active_after is not None:
                    try: pc = len(active_after.data.polygons)
                    except Exception: pc = '?'
                    p(f'  active after: {active_after.name} polys={pc}')
            except Exception as e:
                p(f'  ERROR: {type(e).__name__}: {e}')
                ok = False
                break
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except Exception: pass

        # final
        test_objs = [o for o in bpy.data.objects if o.name.startswith('_ebc_test_plane')]
        p(f'FINAL inventory: {len(test_objs)} test objects')
        for o in test_objs:
            p(f'  {o.name}: {len(o.data.polygons)} polys')
        if len(test_objs) == 4 and ok:
            p('=== PASS ===')
            self.report({'INFO'}, 'TestSep PASS')
        else:
            p(f'=== FAIL: expected 4 objects, got {len(test_objs)} ===')
            self.report({'ERROR'}, f'TestSep FAIL ({len(test_objs)} objects)')

        # cleanup
        for o in test_objs:
            bpy.data.objects.remove(o, do_unlink=True)
        for m in mats:
            if m.users == 0:
                bpy.data.materials.remove(m, do_unlink=True)
        return {'FINISHED'}


class SNA_OT_test_voxel_block_remesh(bpy.types.Operator):
    bl_idname = 'sna.test_voxel_block_remesh'
    bl_label = 'Self-Test: Voxel Block Remesh'
    bl_description = 'Builds a UV-mapped cube with checker texture, runs voxel occupancy + face extraction, validates output. Reports PASS/FAIL in console'
    bl_options = {'REGISTER'}

    def execute(self, context):
        import numpy as np

        def p(msg):
            print(f'[TestVoxel] {msg}', flush=True)

        p('=== test start ===')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        cube = context.active_object
        cube.name = '_ebc_test_voxel_cube'

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide(number_cuts=2)
        bpy.ops.uv.cube_project()
        bpy.ops.object.mode_set(mode='OBJECT')

        img = bpy.data.images.new('_ebc_test_voxel_tex', 64, 64, alpha=False)
        px = np.zeros(64 * 64 * 4, dtype=np.float32)
        for y in range(64):
            for x in range(64):
                i = (y * 64 + x) * 4
                if (x // 8 + y // 8) % 2 == 0:
                    px[i] = 1.0; px[i+1] = 0.0; px[i+2] = 0.0
                else:
                    px[i] = 0.0; px[i+1] = 1.0; px[i+2] = 0.0
        img.pixels[:] = px.tolist()
        p('created test texture 64x64')

        import mathutils
        mesh = cube.data
        n_verts = len(mesh.vertices)
        verts_local = np.empty(n_verts * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', verts_local)
        verts_local = verts_local.reshape(n_verts, 3)
        verts_world = verts_local.copy()  # cube at origin, identity matrix

        verts_list = verts_world.tolist()
        polys_list = []
        poly_loop_start = np.empty(len(mesh.polygons), dtype=np.int32)
        poly_loop_total = np.empty(len(mesh.polygons), dtype=np.int32)
        mesh.polygons.foreach_get('loop_start', poly_loop_start)
        mesh.polygons.foreach_get('loop_total', poly_loop_total)
        loop_verts = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', loop_verts)
        for pi in range(len(mesh.polygons)):
            s = int(poly_loop_start[pi]); t = int(poly_loop_total[pi])
            vs = loop_verts[s:s + t].tolist()
            for ti in range(1, t - 1):
                polys_list.append((vs[0], vs[ti], vs[ti + 1]))

        bvh = mathutils.bvhtree.BVHTree.FromPolygons(verts_list, polys_list)
        p(f'BVHTree: {len(polys_list)} tris — OK')

        depth = 3; grid_size = 1 << depth
        bbox_min = np.min(verts_world, axis=0); bbox_max = np.max(verts_world, axis=0)
        cell_size_ = np.max(bbox_max - bbox_min) / grid_size
        bbox_min -= cell_size_; bbox_max += cell_size_
        max_dim = np.max(bbox_max - bbox_min)
        center_ = (bbox_min + bbox_max) / 2.0; half_ = max_dim / 2.0
        bbox_min = center_ - half_; bbox_max = center_ + half_
        cell_size_ = max_dim / grid_size
        half_diag = cell_size_ * np.sqrt(3) * 0.5
        DIRS = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

        occupied = set()
        for fi, tri_verts_idx in enumerate(polys_list):
            v0 = verts_world[tri_verts_idx[0]]
            v1 = verts_world[tri_verts_idx[1]]
            v2 = verts_world[tri_verts_idx[2]]
            tri_min = np.minimum(np.minimum(v0, v1), v2)
            tri_max = np.maximum(np.maximum(v0, v1), v2)
            ix0 = max(0, int((tri_min[0] - bbox_min[0]) / cell_size_))
            iy0 = max(0, int((tri_min[1] - bbox_min[1]) / cell_size_))
            iz0 = max(0, int((tri_min[2] - bbox_min[2]) / cell_size_))
            ix1 = min(grid_size - 1, int((tri_max[0] - bbox_min[0]) / cell_size_) + 1)
            iy1 = min(grid_size - 1, int((tri_max[1] - bbox_min[1]) / cell_size_) + 1)
            iz1 = min(grid_size - 1, int((tri_max[2] - bbox_min[2]) / cell_size_) + 1)
            for ix in range(ix0, ix1 + 1):
                for iy in range(iy0, iy1 + 1):
                    for iz in range(iz0, iz1 + 1):
                        key = (ix, iy, iz)
                        if key in occupied:
                            continue
                        cx = bbox_min[0] + (ix + 0.5) * cell_size_
                        cy = bbox_min[1] + (iy + 0.5) * cell_size_
                        cz = bbox_min[2] + (iz + 0.5) * cell_size_
                        nearest = bvh.find_nearest(mathutils.Vector((cx, cy, cz)))
                        if nearest is not None and nearest[3] < half_diag:
                            occupied.add(key)

        p(f'Occupied: {len(occupied)} / {grid_size**3} voxels')

        faces_to_emit = []
        for (ix, iy, iz) in occupied:
            for di, (dx, dy, dz) in enumerate(DIRS):
                neighbor = (ix + dx, iy + dy, iz + dz)
                if neighbor not in occupied:
                    faces_to_emit.append((ix, iy, iz, di))

        n_surface = len(faces_to_emit)
        n_potential = len(occupied) * 6
        p(f'Surface faces: {n_surface} / {n_potential} potential')

        ok = n_surface > 0 and n_surface < n_potential
        if ok:
            p('=== PASS ===')
            self.report({'INFO'}, f'TestVoxel PASS: {len(occupied)} voxels, {n_surface} faces')
        else:
            p(f'=== FAIL: faces={n_surface} occupied={len(occupied)} ===')
            self.report({'ERROR'}, 'TestVoxel FAIL')

        bpy.data.objects.remove(cube, do_unlink=True)
        bpy.data.images.remove(img, do_unlink=True)
        return {'FINISHED' if ok else 'CANCELLED'}


class SNA_OT_test_merge_islands(bpy.types.Operator):
    bl_idname = 'sna.test_merge_islands'
    bl_label = 'Self-Test: Merge Small Islands'
    bl_description = 'Builds a 200mm grid plane with 1-cell and 3x3-cell off-cluster islands, runs the island merge logic with 15mm threshold, asserts the small island merged and the big one survived. Reports PASS/FAIL in console'
    bl_options = {'REGISTER'}

    def execute(self, context):
        import numpy as np

        def p(msg):
            print(f'[TestMerge] {msg}', flush=True)

        p('=== test start ===')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_plane_add(size=0.2, location=(50, 50, 50))
        plane = context.active_object
        plane.name = '_ebc_test_merge_plane'
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=19)
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh = plane.data
        n = len(mesh.polygons)
        p(f'plane: {n} polys (expected 400)')

        face_labels = np.zeros(n, dtype=np.int32)
        a_count = b_count = 0
        b_xs = [0.035, 0.045, 0.055]
        b_ys = [-0.035, -0.025, -0.015]
        for pi, poly in enumerate(mesh.polygons):
            cx, cy, _ = poly.center
            face_labels[pi] = 1 if cx > 0 else 0
            if abs(cx - 0.015) < 0.002 and abs(cy - 0.005) < 0.002:
                face_labels[pi] = 0
                a_count += 1
            elif (any(abs(cx - x) < 0.002 for x in b_xs)
                  and any(abs(cy - y) < 0.002 for y in b_ys)):
                face_labels[pi] = 0
                b_count += 1
        n_l0_before = int((face_labels == 0).sum())
        n_l1_before = int((face_labels == 1).sum())
        p(f'before: A={a_count} faces, B={b_count} faces, label0={n_l0_before}, label1={n_l1_before}')

        class _Stub:
            pass
        stub = _Stub()
        stub.min_island_size_x = 0.015  # 15mm
        stub.min_island_size_y = 0.015
        stub.min_island_size_z = 0.0   # plane has no Z extent — disable
        stub.min_island_face_count = 0
        stub.min_island_feature_width = 0.0  # disable OBB check for plane test
        stub.erosion_passes = 0
        stub.erosion_strength = 0.7
        stub.merge_max_iters = 8

        gen = SNA_OT_auto_palette_split._merge_islands_gen(stub, plane, face_labels, p)
        reassigned = 0
        try:
            while True:
                next(gen)
        except StopIteration as si:
            reassigned = si.value if si.value is not None else 0
        p(f'reassigned: {reassigned}')

        n_l0 = int((face_labels == 0).sum())
        n_l1 = int((face_labels == 1).sum())
        p(f'after: label0={n_l0}, label1={n_l1}')

        expected_reassigned = a_count
        expected_l0 = n_l0_before - a_count
        expected_l1 = n_l1_before + a_count
        ok = (reassigned == expected_reassigned
              and n_l0 == expected_l0
              and n_l1 == expected_l1
              and a_count == 1
              and b_count == 9)

        if ok:
            p('=== PASS ===')
            self.report({'INFO'}, 'TestMerge PASS')
        else:
            p(f'=== FAIL: expected reassigned={expected_reassigned} label0={expected_l0} label1={expected_l1}, a_count={a_count} b_count={b_count} ===')
            self.report({'ERROR'}, 'TestMerge FAIL')

        bpy.data.objects.remove(plane, do_unlink=True)
        return {'FINISHED'}


class SNA_OT_remove_ebc_modifier_from_selected(bpy.types.Operator):
    bl_idname = 'sna.remove_ebc_modifier_from_selected'
    bl_label = 'Remove EBC Modifier from Selected'
    bl_description = 'Removes KIRI_Edit_By_Colour_GN from all selected mesh objects'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        n = 0
        for o in context.selected_objects:
            if o.type != 'MESH':
                continue
            m = o.modifiers.get('KIRI_Edit_By_Colour_GN')
            if m is not None:
                o.modifiers.remove(m)
                n += 1
        self.report({'INFO'}, f'Removed modifier from {n} objects')
        return {'FINISHED'}


def sna_auto_palette_interface(layout_function):
    box = layout_function.box()
    box.label(text='Auto Palette Split (k-means)', icon_value=string_to_icon('GROUP_VCOL'))
    obj = bpy.context.view_layer.objects.active
    mod = obj.modifiers.get('KIRI_Edit_By_Colour_GN') if obj else None
    if mod is not None:
        box.operator('sna.auto_palette_split', text='Auto Detect & Split',
                     icon_value=string_to_icon('MOD_EXPLODE'))
    else:
        box.label(text='Add Edit By Colour modifier first', icon_value=0)
    box.operator('sna.remove_ebc_modifier_from_selected',
                 text='Remove EBC Modifier from Selected',
                 icon_value=string_to_icon('TRASH'))
    box.operator('sna.test_merge_islands',
                 text='Self-Test: Merge Small Islands',
                 icon_value=string_to_icon('EXPERIMENTAL'))


def sna_voxel_block_remesh_interface(layout_function):
    box = layout_function.box()
    box.label(text='Voxel Block Remesh (3D Print)', icon_value=string_to_icon('MESH_CUBE'))
    obj = bpy.context.view_layer.objects.active
    mod = obj.modifiers.get('KIRI_Edit_By_Colour_GN') if obj else None
    if mod is not None:
        box.operator('sna.voxel_block_remesh', text='Voxel Remesh & Colorize',
                     icon_value=string_to_icon('MOD_BUILD'))
    else:
        box.label(text='Add Edit By Colour modifier first', icon_value=0)
    box.operator('sna.test_voxel_block_remesh', text='Self-Test: Voxel Block Remesh',
                 icon_value=string_to_icon('EXPERIMENTAL'))


def sna_palette_split_interface(layout_function):
    box = layout_function.box()
    box.label(text='Palette Split (3D Print)', icon_value=string_to_icon('COLOR'))
    obj = bpy.context.view_layer.objects.active
    mod = obj.modifiers.get('KIRI_Edit_By_Colour_GN') if obj else None
    if mod is None:
        box.label(text='Add Edit By Colour modifier first', icon_value=0)
        return
    row = box.row()
    row.template_list('SNA_UL_palette_colors', '', bpy.context.scene, 'sna_palette_colors',
                      bpy.context.scene, 'sna_palette_active_index', rows=4)
    col = row.column(align=True)
    col.operator('sna.palette_add', text='', icon_value=string_to_icon('ADD'))
    col.operator('sna.palette_remove', text='', icon_value=string_to_icon('REMOVE'))
    box.operator('sna.palette_split_and_colorize', text='Split & Colorize',
                 icon_value=string_to_icon('MOD_EXPLODE'))


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.sna_ebc_colour_selection = bpy.props.FloatVectorProperty(name='EBC_Colour_Selection', description='', size=4, default=(0.0, 0.0, 0.0, 0.0), subtype='COLOR', unit='NONE', step=3, precision=6)
    bpy.types.Scene.sna_ebc_active_menu_full = bpy.props.EnumProperty(name='EBC_Active_Menu_Full', description='', items=[('Colour Selection', 'Colour Selection', '', 0, 0), ('Texture', 'Texture', '', 0, 1), ('Edit Mesh', 'Edit Mesh', '', 0, 2), ('Sculpt', 'Sculpt', '', 0, 3)])
    bpy.types.Scene.sna_ebc_active_menu_retopo_loops = bpy.props.EnumProperty(name='EBC_Active_Menu_Retopo_Loops', description='', items=[('Colour Selection', 'Colour Selection', '', 0, 0), ('Retopo Loops', 'Retopo Loops', '', 0, 1)])
    bpy.types.Scene.sna_ebc_base_material = bpy.props.PointerProperty(name='EBC_Base_Material', description='', type=bpy.types.Material)
    bpy.types.Scene.sna_ebc_bake_base_object = bpy.props.PointerProperty(name='EBC_Bake_Base_Object', description='', type=bpy.types.Object)
    bpy.types.Scene.sna_ebc_bake_patch_object = bpy.props.PointerProperty(name='EBC_Bake_Patch_Object', description='', type=bpy.types.Object)
    bpy.types.Scene.sna_ebc_bake_patch_material = bpy.props.PointerProperty(name='EBC_Bake_Patch_Material', description='', type=bpy.types.Material)
    bpy.types.Object.sna_ebc_live_effects_proxy_switch = bpy.props.EnumProperty(name='EBC_Live_Effects_Proxy_Switch', description='', items=[('None', 'None', '', 0, 0), ('Delete Faces', 'Delete Faces', '', 0, 1), ('Smooth', 'Smooth', '', 0, 2), ('Set Material', 'Set Material', '', 0, 3), ('Smooth and Set Material', 'Smooth and Set Material', '', 0, 4), ('Retopo Loops', 'Retopo Loops', '', 0, 5)], update=sna_update_sna_ebc_live_effects_proxy_switch_52B23)
    bpy.types.Scene.sna_ebc_combined_bake_material = bpy.props.PointerProperty(name='EBC_Combined_Bake_Material', description='', type=bpy.types.Material)
    bpy.types.Scene.sna_ebc_baked_diffuse_image = bpy.props.PointerProperty(name='EBC_Baked_DIFFUSE_Image', description='', type=bpy.types.Image)
    bpy.types.Scene.sna_ebc_baked_roughness_image = bpy.props.PointerProperty(name='EBC_Baked_ROUGHNESS_Image', description='', type=bpy.types.Image)
    bpy.types.Scene.sna_ebc_baked_normal_image = bpy.props.PointerProperty(name='EBC_Baked_NORMAL_Image', description='', type=bpy.types.Image)
    bpy.utils.register_class(SNA_OT_Remove_Edit_By_Colour_Modifier_C523D)
    bpy.utils.register_class(SNA_OT_Add_Edit_By_Colour_Modifier_381C0)
    bpy.utils.register_class(SNA_OT_Apply_Edit_By_Colour_Modifier_45130)
    bpy.utils.register_class(SNA_OT_Add_Wire_Cube_24Ccd)
    bpy.utils.register_class(SNA_OT_Edit_By_Colour__Select_77Ba8)
    bpy.utils.register_class(SNA_OT_Edit_By_Colour__Split_819Ad)
    bpy.utils.register_class(SNA_OT_Edit_By_Colour__Duplicate_F7267)
    bpy.utils.register_class(SNA_OT_Apply_Retopo_Loops_7Ea68)
    bpy.utils.register_class(SNA_OT_Selection_To_Face_Sets_69A50)
    bpy.utils.register_class(SNA_PT_EDIT_BY_COLOUR_BY_KIRI_ENGINE_955BF)
    bpy.utils.register_class(SNA_OT_Open_Edit_By_Colour_Documentation_1Eac5)
    bpy.utils.register_class(SNA_OT_Open_Edit_By_Colour_Tutorial_Video_A4Fe6)
    bpy.utils.register_class(SNA_OT_Ebclaunch_Kiri_Site_D26Bf)
    bpy.utils.register_class(SNA_OT_Ebclaunch_Blender_Market_77F72)
    bpy.utils.register_class(SNA_OT_Add_Ebc_Attribute_To_Selected_Material_3F5C9)
    bpy.utils.register_class(SNA_OT_Bake_Set_Material__Original_Dafdb)
    bpy.utils.register_class(SNA_OT_Switch_To_Combined_Bake_Material_A7D5F)
    bpy.utils.register_class(SNA_OT_Bake_To_Patch_Fa828)
    bpy.utils.register_class(SNA_OT_Add_Bake_Patch_68526)
    bpy.utils.register_class(SNA_OT_Link_Baked_Textures_Patch_067F8)
    bpy.utils.register_class(SNA_PaletteColorItem)
    bpy.utils.register_class(SNA_UL_palette_colors)
    bpy.utils.register_class(SNA_OT_palette_add)
    bpy.utils.register_class(SNA_OT_palette_remove)
    bpy.utils.register_class(SNA_OT_palette_split_and_colorize)
    bpy.utils.register_class(SNA_OT_auto_palette_split)
    bpy.utils.register_class(SNA_OT_remove_ebc_modifier_from_selected)
    bpy.utils.register_class(SNA_OT_test_progressive_separate)
    bpy.utils.register_class(SNA_OT_test_merge_islands)
    bpy.utils.register_class(SNA_OT_voxel_block_remesh)
    bpy.utils.register_class(SNA_OT_test_voxel_block_remesh)
    bpy.types.Scene.sna_palette_colors = bpy.props.CollectionProperty(type=SNA_PaletteColorItem)
    bpy.types.Scene.sna_palette_active_index = bpy.props.IntProperty(default=0)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_ebc_baked_normal_image
    del bpy.types.Scene.sna_ebc_baked_roughness_image
    del bpy.types.Scene.sna_ebc_baked_diffuse_image
    del bpy.types.Scene.sna_ebc_combined_bake_material
    del bpy.types.Object.sna_ebc_live_effects_proxy_switch
    del bpy.types.Scene.sna_ebc_bake_patch_material
    del bpy.types.Scene.sna_ebc_bake_patch_object
    del bpy.types.Scene.sna_ebc_bake_base_object
    del bpy.types.Scene.sna_ebc_base_material
    del bpy.types.Scene.sna_ebc_active_menu_retopo_loops
    del bpy.types.Scene.sna_ebc_active_menu_full
    del bpy.types.Scene.sna_ebc_colour_selection
    bpy.utils.unregister_class(SNA_OT_Remove_Edit_By_Colour_Modifier_C523D)
    bpy.utils.unregister_class(SNA_OT_Add_Edit_By_Colour_Modifier_381C0)
    bpy.utils.unregister_class(SNA_OT_Apply_Edit_By_Colour_Modifier_45130)
    bpy.utils.unregister_class(SNA_OT_Add_Wire_Cube_24Ccd)
    bpy.utils.unregister_class(SNA_OT_Edit_By_Colour__Select_77Ba8)
    bpy.utils.unregister_class(SNA_OT_Edit_By_Colour__Split_819Ad)
    bpy.utils.unregister_class(SNA_OT_Edit_By_Colour__Duplicate_F7267)
    bpy.utils.unregister_class(SNA_OT_Apply_Retopo_Loops_7Ea68)
    bpy.utils.unregister_class(SNA_OT_Selection_To_Face_Sets_69A50)
    bpy.utils.unregister_class(SNA_PT_EDIT_BY_COLOUR_BY_KIRI_ENGINE_955BF)
    bpy.utils.unregister_class(SNA_OT_Open_Edit_By_Colour_Documentation_1Eac5)
    bpy.utils.unregister_class(SNA_OT_Open_Edit_By_Colour_Tutorial_Video_A4Fe6)
    bpy.utils.unregister_class(SNA_OT_Ebclaunch_Kiri_Site_D26Bf)
    bpy.utils.unregister_class(SNA_OT_Ebclaunch_Blender_Market_77F72)
    bpy.utils.unregister_class(SNA_OT_Add_Ebc_Attribute_To_Selected_Material_3F5C9)
    bpy.utils.unregister_class(SNA_OT_Bake_Set_Material__Original_Dafdb)
    bpy.utils.unregister_class(SNA_OT_Switch_To_Combined_Bake_Material_A7D5F)
    bpy.utils.unregister_class(SNA_OT_Bake_To_Patch_Fa828)
    bpy.utils.unregister_class(SNA_OT_Add_Bake_Patch_68526)
    bpy.utils.unregister_class(SNA_OT_Link_Baked_Textures_Patch_067F8)
    del bpy.types.Scene.sna_palette_active_index
    del bpy.types.Scene.sna_palette_colors
    bpy.utils.unregister_class(SNA_OT_test_merge_islands)
    bpy.utils.unregister_class(SNA_OT_test_voxel_block_remesh)
    bpy.utils.unregister_class(SNA_OT_voxel_block_remesh)
    bpy.utils.unregister_class(SNA_OT_test_progressive_separate)
    bpy.utils.unregister_class(SNA_OT_remove_ebc_modifier_from_selected)
    bpy.utils.unregister_class(SNA_OT_auto_palette_split)
    bpy.utils.unregister_class(SNA_OT_palette_split_and_colorize)
    bpy.utils.unregister_class(SNA_OT_palette_remove)
    bpy.utils.unregister_class(SNA_OT_palette_add)
    bpy.utils.unregister_class(SNA_UL_palette_colors)
    bpy.utils.unregister_class(SNA_PaletteColorItem)
