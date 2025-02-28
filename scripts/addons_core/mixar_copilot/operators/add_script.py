import bpy
from datetime import datetime
from ..utils.error_handling import operator_error_handler

class CHAT_OT_add_script(bpy.types.Operator):
    """Operator for adding chat messages"""
    bl_idname = "chat.add_script"
    bl_label = "Add Script"
    
    content: bpy.props.StringProperty()
    is_user: bpy.props.BoolProperty()
    
    @operator_error_handler
    def execute(self, context):
        props = context.scene.custom_panel_props
        script = props.scripts.add()
        script.content = self.content
        script.is_user = self.is_user
        script.timestamp = datetime.now().strftime("%H:%M")
        return {'FINISHED'}