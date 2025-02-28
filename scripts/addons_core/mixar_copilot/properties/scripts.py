import bpy

class Script(bpy.types.PropertyGroup):
    content: bpy.props.StringProperty(
        name="Content",
        description="Script content"
    )
    is_user: bpy.props.BoolProperty(
        name="Is User",
        description="Whether the message is from the user"
    )
    timestamp: bpy.props.StringProperty(
        name="Timestamp",
        description="Message timestamp"
    )

