import bpy
from .chat import CHAT_OT_add_message, TextInputArea
from .submit import OBJECT_OT_submit_operator
from .analyze import (
    MIXAR_OT_analyze_image,
    OBJECT_OT_approve_operator,
    OBJECT_OT_edit_operator
)
from .loading import MIXAR_OT_cancel_operation
from ..utils.error_handling import ErrorDialogOperator
from .async_operator import MIXAR_OT_async_operation
from .toggle import MIXAR_OT_toggle_text_editor
from .add_script import CHAT_OT_add_script
__all__ = [
    'CHAT_OT_add_message',
    'TextInputArea',
    'OBJECT_OT_submit_operator',
    'MIXAR_OT_analyze_image',
    'OBJECT_OT_approve_operator',
    'OBJECT_OT_edit_operator',
    'ErrorDialogOperator',
    'MIXAR_OT_cancel_operation',
    'MIXAR_OT_async_operation',
    'MIXAR_OT_toggle_text_editor',
    'CHAT_OT_add_script'
]

def register_operators():
    bpy.utils.register_class(ErrorDialogOperator)
    bpy.utils.register_class(CHAT_OT_add_message)
    bpy.utils.register_class(TextInputArea)
    bpy.utils.register_class(OBJECT_OT_submit_operator)
    bpy.utils.register_class(MIXAR_OT_analyze_image)
    bpy.utils.register_class(OBJECT_OT_approve_operator)
    bpy.utils.register_class(OBJECT_OT_edit_operator)
    bpy.utils.register_class(MIXAR_OT_cancel_operation)
    bpy.utils.register_class(MIXAR_OT_async_operation)
    bpy.utils.register_class(MIXAR_OT_toggle_text_editor)
    bpy.utils.register_class(CHAT_OT_add_script)
def unregister_operators():
    bpy.utils.unregister_class(OBJECT_OT_edit_operator)
    bpy.utils.unregister_class(OBJECT_OT_approve_operator)
    bpy.utils.unregister_class(MIXAR_OT_analyze_image)
    bpy.utils.unregister_class(OBJECT_OT_submit_operator)
    bpy.utils.unregister_class(TextInputArea)
    bpy.utils.unregister_class(CHAT_OT_add_message)
    bpy.utils.unregister_class(ErrorDialogOperator)
    bpy.utils.unregister_class(MIXAR_OT_cancel_operation)
    bpy.utils.unregister_class(MIXAR_OT_async_operation)
    bpy.utils.unregister_class(MIXAR_OT_toggle_text_editor)
    bpy.utils.unregister_class(CHAT_OT_add_script)