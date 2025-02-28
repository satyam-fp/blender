import bpy
from ..constants import DUMMY_DATA
from ..api.client import MixarAPIClient
from ..utils.error_handling import operator_error_handler, show_error

class MIXAR_OT_analyze_image(bpy.types.Operator):
    """Operator for analyzing images"""
    bl_idname = "mixar.analyze_image"
    bl_label = "Analyze Image"
    
    @operator_error_handler
    def execute(self, context):
        props = context.scene.custom_panel_props
        
        if not props.image_url or not props.user_input:
            self.report({'ERROR'}, "Please select an image and enter a prompt")
            return {'CANCELLED'}
        
        # Using dummy data for testing
        for item_data in DUMMY_DATA:
            item = props.analysis_results.add()
            item.component = item_data["component"]
            item.count = item_data["count"]
            item.basic_shape = item_data["basic_shape"]
            item.description = item_data["description"]
            
        return {'FINISHED'}

class OBJECT_OT_approve_operator(bpy.types.Operator):
    """Operator for approving and executing generated scripts"""
    bl_idname = "object.approve_operator"
    bl_label = "Approve"
    
    @operator_error_handler
    def execute(self, context):
        custom_props = context.scene.custom_panel_props
        thread_id = custom_props.thread_id_tab2
        
        if not thread_id:
            self.report({'ERROR'}, "Thread ID is missing. Please generate a description first.")
            show_error("Thread ID is missing. Please generate a description first.", width=250, height=150)
            return {'CANCELLED'}

        # return self._handle_approve(thread_id)
        return self._handle_approve_async(thread_id)
    
    def _handle_approve(self, thread_id):
        try:
            api_client = MixarAPIClient()
            response = api_client.generate_script(thread_id)
            
            if response:
                script_content = response.get("script", "")
                if script_content:
                    # Extract code between triple backticks if present
                    if '```python' in script_content:
                        script_lines = script_content.split('```python')[1]
                        script_lines = script_lines.split('```')[0]
                    else:
                        script_lines = script_content
                    
                    # Execute the script in Blender's context
                    exec(script_lines, {'bpy': bpy})
                    self.report({'INFO'}, "Script executed successfully.")
                    return {'FINISHED'}
                else:
                    self.report({'ERROR'}, "No script content received from the API.")
                    show_error("No script content received from the API.", width=250, height=150)
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, "API call failed")
                show_error("API call failed", width=250, height=150)
                return {'CANCELLED'}
        except Exception as e:
            error_msg = f"Error during script execution: {str(e)}"
            show_error(error_msg, width=250, height=150)
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
        
    def _handle_approve_async(self, thread_id):
        bpy.ops.mixar.async_operation(
            'INVOKE_DEFAULT',
            operation="generate_script",
            thread_id=thread_id
        )
        
        return {'FINISHED'}

class OBJECT_OT_edit_operator(bpy.types.Operator):
    """Operator for editing generated scripts"""
    bl_idname = "object.edit_operator"
    bl_label = "Edit"
    
    @operator_error_handler
    def execute(self, context):
        self.report({'INFO'}, "Edit action not available in beta version.")
        return {'FINISHED'}