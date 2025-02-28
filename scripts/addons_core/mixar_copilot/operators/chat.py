import bpy
from datetime import datetime
from ..utils.error_handling import operator_error_handler

class CHAT_OT_add_message(bpy.types.Operator):
    """Operator for adding chat messages"""
    bl_idname = "chat.add_message"
    bl_label = "Add Chat Message"
    
    content: bpy.props.StringProperty()
    is_user: bpy.props.BoolProperty()
    
    @operator_error_handler
    def execute(self, context):
        props = context.scene.custom_panel_props
        message = props.chat_messages.add()
        message.content = self.content
        message.is_user = self.is_user
        message.timestamp = datetime.now().strftime("%H:%M")
        return {'FINISHED'}

class TextInputArea(bpy.types.Operator):
    """Operator for handling text input"""
    bl_idname = "custom.text_input_area"
    bl_label = "Text Input"
    
    text: bpy.props.StringProperty(name="Text")
    multiline: bpy.props.StringProperty(
        name="Multiline Input",
        description="Enter your text here",
        default=""
    )
    
    @operator_error_handler
    def execute(self, context):
        context.scene.custom_panel_props.user_input = self.multiline
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.multiline = context.scene.custom_panel_props.user_input
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "multiline", text="")