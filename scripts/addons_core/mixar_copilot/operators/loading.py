import bpy

from .async_operator import active_async_operators

class MIXAR_OT_cancel_operation(bpy.types.Operator):
    """Cancel the current operation"""
    bl_idname = "mixar.cancel_operation"
    bl_label = "Cancel Operation"
    
    def execute(self, context):
        print("Cancel operation triggered")
        props = context.scene.custom_panel_props
        
        # Set loading state to False
        props.is_loading = False
        
        # Cancel all active operators
        print(f"Found {len(active_async_operators)} active operators")
        for operator in active_async_operators[:]:  # Use slice to avoid modification during iteration
            try:
                print(f"Cancelling operator: {operator.bl_idname}")
                operator.cancel(context)
            except Exception as e:
                print(f"Error cancelling operator: {str(e)}")
        
        # Force UI update
        for area in context.screen.areas:
            area.tag_redraw()
        
        print("Cancel operation completed")
        return {'FINISHED'}
    