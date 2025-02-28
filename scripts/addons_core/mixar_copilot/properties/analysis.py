import bpy

class DummyAnalysisItem(bpy.types.PropertyGroup):
    """Property group for storing analysis results"""
    component: bpy.props.StringProperty(
        name="Component",
        description="Component name"
    )
    count: bpy.props.IntProperty(
        name="Count",
        description="Number of components"
    )
    basic_shape: bpy.props.StringProperty(
        name="Basic Shape",
        description="Basic shape description"
    )
    description: bpy.props.StringProperty(
        name="Description",
        description="Detailed component description"
    )