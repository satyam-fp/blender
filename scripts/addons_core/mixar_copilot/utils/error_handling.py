import bpy
from functools import wraps
from ..api.client import APIError


def show_error(message, width=300, height=100):
    """Show error dialog with consistent styling"""
    bpy.ops.mixar.error_dialog('INVOKE_DEFAULT', 
        message=message, 
        width=width, 
        height=height
    )

def operator_error_handler(func):
    """Decorator for handling operator errors with loading states and recovery"""
    @wraps(func)
    def wrapper(self, context, *args, **kwargs):
        # Only backup state if context is valid
        backup = None
        props = None
        
        if context and hasattr(context, 'scene') and hasattr(context.scene, 'custom_panel_props'):
            backup = ErrorRecovery.backup_state(context)
            props = context.scene.custom_panel_props
            # Set loading state at start of operation
            props.is_loading = True
            # Force immediate UI update
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'UI':
                            region.tag_redraw()
                area.tag_redraw()
        
        try:
            return func(self, context, *args, **kwargs)
            
        except APIError as e:
            if backup and props:
                ErrorRecovery.restore_state(context, backup)
            error_msg = f"API Error: {str(e)}"
            show_error(error_msg, width=400, height=150)
            log_error(error_msg, context)
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
            
        except Exception as e:
            if backup and props:
                ErrorRecovery.restore_state(context, backup)
            error_msg = f"Operator Handler Exception: {str(e)}"
            show_error(error_msg, width=400, height=150)
            log_error(error_msg, context)
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
            
        finally:
            # Clean up loading state and update UI
            if props:
                print("####################### Finally #######################")
                props.is_loading = False
                props.loading_message = "Processing..."  # Reset to default
                
            # Force final UI update
            if context and hasattr(context, 'screen'):
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
    
    return wrapper

def ui_error_handler(func):
    """Decorator for handling UI drawing errors"""
    @wraps(func)
    def wrapper(self, context):
        try:
            return func(self, context)
        except Exception as e:
            layout = self.layout
            box = layout.box()
            box.label(text=f"Error drawing UI: {str(e)}", icon='ERROR')
    return wrapper

class ErrorDialogOperator(bpy.types.Operator):
    """Operator for displaying error dialogs"""
    bl_idname = "mixar.error_dialog"
    bl_label = "Error"

    message: bpy.props.StringProperty()
    width: bpy.props.IntProperty(default=300)
    height: bpy.props.IntProperty(default=100)
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=self.width)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        col.scale_y = 0.7
        
        # Word wrap the message
        import textwrap
        max_chars = self.width // 10
        wrapped_lines = textwrap.wrap(self.message, width=max_chars)
        
        # Display wrapped text
        for line in wrapped_lines:
            col.label(text=line)

def log_error(error, context=None):
    """Log error to console and optionally to chat"""
    print(f"MixarAI Error: {str(error)}")
    
    if context and hasattr(context, 'scene'):
        try:
            bpy.ops.chat.add_message(
                content=f"Error: {str(error)}",
                is_user=False
            )
        except Exception:
            pass
        
class ErrorRecovery:
    """Handles error recovery and state restoration"""
    
    @staticmethod
    def backup_state(context):
        """Backup current state before risky operations"""
        props = context.scene.custom_panel_props
        return {
            'thread_id_tab1': props.thread_id_tab1,
            'thread_id_tab2': props.thread_id_tab2,
            'thread_id_tab3': props.thread_id_tab3,
            'user_input': props.user_input,
            'image_url': props.image_url,
            'active_tab': props.active_tab,
            'analysis_results': [(
                item.component,
                item.count,
                item.basic_shape,
                item.description
            ) for item in props.analysis_results]
        }
    
    @staticmethod
    def restore_state(context, backup):
        """Restore state from backup"""
        props = context.scene.custom_panel_props
        props.thread_id_tab1 = backup['thread_id_tab1']
        props.thread_id_tab2 = backup['thread_id_tab2']
        props.thread_id_tab3 = backup['thread_id_tab3']
        props.user_input = backup['user_input']
        props.image_url = backup['image_url']
        props.active_tab = backup['active_tab']
        
        props.analysis_results.clear()
        for comp, count, shape, desc in backup['analysis_results']:
            item = props.analysis_results.add()
            item.component = comp
            item.count = count
            item.basic_shape = shape
            item.description = desc