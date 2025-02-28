import bpy

class MIXAR_OT_toggle_text_editor(bpy.types.Operator):
    bl_idname = "mixar.toggle_text_editor"
    bl_label = "Toggle Text Editor"
    
    def execute(self, context):
        props = context.scene.custom_panel_props
        
        if props.show_text_editor:
            text_editor_area = None
            viewport_area = None
            
            for area in context.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    text_editor_area = area
                elif area.type == 'VIEW_3D':
                    viewport_area = area
            
            if text_editor_area and viewport_area:
                direction = 'RIGHT' if text_editor_area.x > viewport_area.x else 'LEFT'
                
                override = context.copy()
                override['area'] = viewport_area
                override['region'] = viewport_area.regions[0]
                
                # if direction == 'RIGHT':
                #     context.window.cursor_warp(
                #         viewport_area.x + viewport_area.width - 1,
                #         viewport_area.y + viewport_area.height // 2
                #     )
                # else:
                #     context.window.cursor_warp(
                #         viewport_area.x,
                #         viewport_area.y + viewport_area.height // 2
                #     )
                
                
                with context.temp_override(**override):
                    bpy.ops.screen.area_join(target_xy=(text_editor_area.x, text_editor_area.y))
            
            props.show_text_editor = False
            
        else:
            text_editor = None
            for area in context.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    text_editor = area
                    break
            
            text_name = "Generated_Script.py"
            text = bpy.data.texts.get(text_name)
            
            if text_editor:
                text_editor.spaces[0].text = text
            
            else:
                current_area = context.area
                with context.temp_override(area=current_area):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.3)

                new_area = context.screen.areas[-1]
                new_area.type = 'TEXT_EDITOR'
                new_area.spaces[0].text = text
            
            props.show_text_editor = True
        
        return {'FINISHED'}