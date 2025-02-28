import bpy
from .chat import ChatMessage
from .scripts import Script
from .analysis import DummyAnalysisItem

class CustomPanelProperties(bpy.types.PropertyGroup):
    """Main property group for the panel"""
    active_tab: bpy.props.EnumProperty(
        name="Active Tab",
        description="Switch between tabs",
        items=[
            ('TAB1', "Chatting", "First tab"),
            # ('TAB2', "Scripting", "Second tab"),
            ('TAB3', "Modeling", "Model Generation tab"),
        ],
        default='TAB1',
    )
    
    user_input: bpy.props.StringProperty(
        name="Label", 
        description="Enter your prompt", 
        default="", 
        subtype='NONE', 
        options={'TEXTEDIT_UPDATE'}
    )
    
    chat_messages: bpy.props.CollectionProperty(
        type=ChatMessage,
        name="Chat Messages",
        description="Collection of chat messages"
    )
    
    image_path: bpy.props.StringProperty(
        name="Image Path",
        description="Path to the image file",
        subtype='FILE_PATH'
    )
    
    image_url: bpy.props.StringProperty(
        name="Image URL",
        description="Enter your image URL",
        default="",
        subtype='NONE',
        options={'TEXTEDIT_UPDATE'}
    )
    
    analysis_results: bpy.props.CollectionProperty(
        type=DummyAnalysisItem,
        name="Analysis Results",
        description="Collection of analysis results"
    )

    thread_id_tab1: bpy.props.StringProperty(
        name="Thread ID Tab 1",
        description="Thread ID from chat API for Tab 1"
    )
    
    thread_id_tab2: bpy.props.StringProperty(
        name="Thread ID Tab 2",
        description="Thread ID from generate_description API for Tab 2"
    )
    
    thread_id_tab3: bpy.props.StringProperty(
        name="Thread ID Tab 3",
        description="Thread ID from generate_script API for Tab 3"
    )   
    
    is_loading: bpy.props.BoolProperty(
        name="Loading State",
        description="Indicates if an operation is in progress",
        default=False
    )
    
    loading_message: bpy.props.StringProperty(
        name="Loading Message",
        description="Message to display during loading",
        default="Processing..."
    )
    
    generated_script: bpy.props.StringProperty(
        name="Generated Script",
        description="Generated script content",
        default=""
    )
    
    show_text_editor: bpy.props.BoolProperty(
        name="Show Text Editor",
        description="Toggle Text Editor visibility",
        default=False
    )
    
    scripts: bpy.props.CollectionProperty(
        type=Script,
        name="Scripts",
        description="List of scripts"
    )
    user_input_for_scripting: bpy.props.StringProperty(
        name="Label", 
        description="Enter your prompt", 
        default="", 
        subtype='NONE', 
        options={'TEXTEDIT_UPDATE'}
    )
    
    image_url_for_scripting: bpy.props.StringProperty(
        name="Image URL for Scripting",
        description="Enter your image URL for scripting",
        default="",
        subtype='NONE',
        options={'TEXTEDIT_UPDATE'}
    )
