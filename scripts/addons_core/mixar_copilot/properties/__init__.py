import bpy
from .chat import ChatMessage
from .analysis import DummyAnalysisItem
from .panel import CustomPanelProperties
from .scripts import Script

__all__ = ['ChatMessage', 'DummyAnalysisItem', 'CustomPanelProperties', 'Script']

def register_properties():
    bpy.utils.register_class(ChatMessage)
    bpy.utils.register_class(Script)
    bpy.utils.register_class(DummyAnalysisItem)
    bpy.utils.register_class(CustomPanelProperties)
    bpy.types.Scene.custom_panel_props = bpy.props.PointerProperty(type=CustomPanelProperties)

def unregister_properties():
    del bpy.types.Scene.custom_panel_props
    bpy.utils.unregister_class(CustomPanelProperties)
    bpy.utils.unregister_class(DummyAnalysisItem)
    bpy.utils.unregister_class(ChatMessage)
    bpy.utils.unregister_class(Script)