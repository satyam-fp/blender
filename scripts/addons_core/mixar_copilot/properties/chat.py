import bpy

class ChatMessage(bpy.types.PropertyGroup):
    """Property group for storing chat messages"""
    content: bpy.props.StringProperty(
        name="Content",
        description="Message content"
    )
    is_user: bpy.props.BoolProperty(
        name="Is User",
        description="Whether the message is from the user"
    )
    timestamp: bpy.props.StringProperty(
        name="Timestamp",
        description="Message timestamp"
    )