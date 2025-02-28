import bpy
import textwrap
from .ui_utils import draw_markdown
from ..utils.error_handling import ui_error_handler
from .loading import draw_loading_spinner

class VIEW3D_PT_main_panel(bpy.types.Panel):
    """Main panel for the Mixar Copilot"""
    bl_label = "Mixar Copilot"
    bl_idname = "VIEW3D_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Mixar Copilot"

    def get_wrap_width(self, context):
        """Calculate the wrap width based on UI scale"""
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'UI':
                        ui_scale = context.preferences.view.ui_scale
                        char_width = 9 * ui_scale  
                        return int((region.width * 0.85) // char_width)
        return 30

    def wrap_text(self, context, text, width_percentage=1.0):
        """Wrap text to fit the panel width"""
        max_width = int(self.get_wrap_width(context) * width_percentage)
        if not text:
            return [""]
        return textwrap.wrap(text, width=max_width)

    def draw_wrapped_text(self, layout, context, text, width_percentage=1.0):
        """Draw wrapped text in the panel"""
        wrapped_lines = self.wrap_text(context, text, width_percentage)
        for line in wrapped_lines:
            layout.label(text=line)

    def draw_chat_message(self, layout, context, message):
        """Draw a chat message in the panel"""
        message_box = layout.box()
        header_row = message_box.row()
        
        # Message header
        header_label = header_row.column()
        header_label.alignment = 'LEFT'
        header_label.label(text="User:" if message.is_user else "Agent:")
        
        # Timestamp
        timestamp_label = header_row.column()
        timestamp_label.alignment = 'RIGHT'
        timestamp_label.label(text=message.timestamp)
        
        # Message content
        content_col = message_box.column()
        dpi = bpy.context.preferences.system.dpi
        ui_scale = dpi / 72
        
        # Calculate row length
        for r in context.area.regions:
            if r.type == "UI":
                width = r.width
        row_length = width
        row_length -= 20 * ui_scale  # tool bar
        row_length -= 40 * ui_scale  # margin
        row_length /= 6 * ui_scale  # 1 char per 6 px
        
        # Draw message content with markdown formatting
        # print("########### message.content", message.content)
        draw_markdown(content_col, message.content, row_length)

    @ui_error_handler
    def draw(self, context):
        """Draw the panel UI"""
        layout = self.layout
        custom_props = context.scene.custom_panel_props
        
        # if custom_props.is_loading:
        #     draw_loading_spinner(layout, custom_props)
        #     return  # Don't draw other UI while loading

        # Tab selector
        row = layout.row()
        row.prop(custom_props, "active_tab", expand=True)
        
        def draw_input_area(layout, context, props):
            """Draw the input area for both tabs"""
            input_box = layout.box()
            input_box.label(text="Prompt:")
            input_box.prop(props, "user_input", text="", icon='TEXT')
            input_box.label(text="Image URL:")
            input_box.prop(props, "image_url", text="", icon='URL')
            
            if custom_props.is_loading:
                draw_loading_spinner(layout, custom_props)
                return  # Don't draw other UI while loading
        
        def draw_input_area_for_scripting(layout, context, props):
            input_box = layout.box()
            input_box.label(text="Prompt:")
            input_box.prop(props, "user_input_for_scripting", text="", icon='TEXT')
            input_box.label(text="Image URL:")
            input_box.prop(props, "image_url_for_scripting", text="", icon='URL')
            
            if custom_props.is_loading:
                draw_loading_spinner(layout, custom_props)
                return  # Don't draw other UI while loading


        if custom_props.active_tab == 'TAB2':
            # Scripting tab
            draw_input_area(layout, context, custom_props)
            layout.operator("object.submit_operator", text="Submit")
            
            if custom_props.analysis_results:
                self._draw_analysis_results(layout, context, custom_props)

        elif custom_props.active_tab == 'TAB1':
            # Chat tab
            draw_input_area(layout, context, custom_props)
            layout.operator("object.submit_operator", text="Submit")
            box = layout.box()
            for message in reversed(custom_props.chat_messages):
                self.draw_chat_message(box, context, message)
        elif custom_props.active_tab == 'TAB3':
            draw_input_area_for_scripting(layout, context, custom_props)
            layout.operator("object.submit_operator", text="Submit")
            box = layout.box()
            for message in reversed(custom_props.scripts):
                self.draw_chat_message(box, context, message)

    def _draw_analysis_results(self, layout, context, props):
        """Draw analysis results in the panel"""
        result_box = layout.box()
        
        # Header
        header_row = result_box.row()
        col1 = header_row.column()
        col1.label(text="Component")
        col2 = header_row.column()
        col2.label(text="Count")
        col3 = header_row.column()
        col3.label(text="Basic Shape")
        col4 = header_row.column()
        col4.label(text="Visual Characteristics")
        
        result_box.separator()
        
        # Results
        for result in props.analysis_results:
            row_box = result_box.box()
            main_row = row_box.row()
            
            split = main_row.split(factor=0.15)
            col1 = split.column()
            self.draw_wrapped_text(col1, context, result.component, 0.15)
            
            remaining = split.split(factor=0.1)
            col2 = remaining.column()
            col2.label(text=str(result.count))
            
            remaining2 = remaining.split(factor=0.3)
            col3 = remaining2.column()
            self.draw_wrapped_text(col3, context, result.basic_shape, 0.25)
            
            col4 = remaining2.column()
            self.draw_wrapped_text(col4, context, result.description, 0.5)
        
        # Action buttons
        button_row = layout.row()
        button_row.operator("object.approve_operator", text="Approve")
        button_row.operator("object.edit_operator", text="Edit")
        button_row.operator("mixar.toggle_text_editor", text="Show Script")