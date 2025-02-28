bl_info = {
    "name": "Mixar Copilot", #! Must match bl_idname
    "description": "AI integration for Mixar",
    "author": "Team Mixar",
    "version": (1, 0, 0),
    "blender": (3, 2, 0),
    "location": "View3D > Sidebar > Mixar Copilot",
    "category": "3D View",
    'bl_options': {'HIDDEN'}
}

import bpy
import sys
from datetime import datetime

# Error handling for dependency imports
class DependencyError(Exception):
    """Custom exception for dependency-related errors"""
    pass

class InitializationError(Exception):
    """Custom exception for initialization-related errors"""
    pass

def setup_addon():
    """Initialize the addon and handle any setup errors"""
    try:
        from . import dependencies
        dependencies.setup_dependencies()
        
        # Import all required modules after dependencies are set up
        from .properties import register_properties, unregister_properties
        from .operators import register_operators, unregister_operators
        from .ui import register_ui, unregister_ui
        
        return (register_properties, unregister_properties,
                register_operators, unregister_operators,
                register_ui, unregister_ui)
    
    except ImportError as e:
        raise DependencyError(f"Failed to import required modules: {str(e)}")
    except Exception as e:
        raise InitializationError(f"Failed to initialize addon: {str(e)}")

def error_handler(func):
    """Decorator for handling registration errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            error_msg = f"Error in {func.__name__}: {str(e)}"
            print(f"MixarAI Error: {error_msg}")
            
            # Show error in Blender's UI
            def draw(self, context):
                self.layout.label(text=error_msg)
            
            bpy.context.window_manager.popup_menu(draw, title="MixarAI Error", icon='ERROR')
            
            # Re-raise the exception for Blender's error handling
            raise
    return wrapper

class MixarAIPreferenceNew(bpy.types.AddonPreferences):
    # bl_idname = "Mixar Copilot"
    bl_idname = __name__

    user_id: bpy.props.StringProperty(
        name="User ID",
        description="Enter your User ID",
        default="",
        # subtype="PASSWORD",
    )
    license_key: bpy.props.StringProperty(
        name="License Key",
        description="Enter your Mixar AI License Key",
        default="",
        # subtype="PASSWORD",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "user_id")
        layout.prop(self, "license_key")

@error_handler
def register():
    """Register the addon with error handling"""
    try:
        bpy.utils.register_class(MixarAIPreferenceNew)
        # Get all registration functions
        (register_properties, _, 
         register_operators, _,
         register_ui, _) = setup_addon()
        
        # Register all components in order
        register_properties()
        register_operators()
        register_ui()
        
        print("MixarAI: Successfully registered all components")
        
    except DependencyError as e:
        raise Exception(f"Dependency Error: {str(e)}")
    except InitializationError as e:
        raise Exception(f"Initialization Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Registration Error: {str(e)}")

@error_handler
def unregister():
    """Unregister the addon with error handling"""
    try:
        bpy.utils.unregister_class(MixarAIPreferenceNew)
        # Get all unregistration functions
        (_, unregister_properties,
         _, unregister_operators,
         _, unregister_ui) = setup_addon()
        
        # Unregister in reverse order
        unregister_ui()
        unregister_operators()
        unregister_properties()
        
        print("MixarAI: Successfully unregistered all components")
        
    except Exception as e:
        raise Exception(f"Unregistration Error: {str(e)}")

# Error handling for the API client
class APIErrorHandler:
    """Global error handler for API operations"""
    
    @staticmethod
    def handle_api_error(error, context=None):
        """Handle API errors and show appropriate messages"""
        from .api.client import APIError
        
        error_msg = str(error)
        print(f"MixarAI API Error: {error_msg}")
        
        if context and hasattr(context, 'scene'):
            # Add error message to chat if possible
            try:
                bpy.ops.chat.add_message(
                    content=f"Error: {error_msg}",
                    is_user=False
                )
            except Exception:
                pass
        
        # Show error in Blender's UI
        def draw(self, context):
            self.layout.label(text=error_msg)
        
        bpy.context.window_manager.popup_menu(draw, title="MixarAI API Error", icon='ERROR')

# from .api.client import APIError

# # Global exception handler for the addon
# def global_exception_handler(exc_type, exc_value, exc_traceback):
#     """Handle uncaught exceptions in the addon"""
#     if issubclass(exc_type, (DependencyError, InitializationError, APIError)):
#         # Handle known addon errors
#         error_msg = f"MixarAI Error: {str(exc_value)}"
#         print(error_msg)
        
#         def draw(self, context):
#             self.layout.label(text=str(exc_value))
        
#         bpy.context.window_manager.popup_menu(draw, title="MixarAI Error", icon='ERROR')
#     else:
#         # Handle other exceptions normally
#         sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Set up global exception handler
# sys.excepthook = global_exception_handler

if __name__ == "__main__":
    register()