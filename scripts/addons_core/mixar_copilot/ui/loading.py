import bpy
import time

def draw_loading_spinner(layout, props):
    """Draw an animated loading spinner"""
    box = layout.box()
    row = box.row()
    row.alignment = 'CENTER'
    
    # Animated spinner based on time
    spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    current_char = spinner_chars[int(time.time() * 8) % len(spinner_chars)]
    
    col = row.column()
    col.scale_y = 2.0
    
    col.separator()
    loading_row = col.row()
    loading_row.alignment = 'CENTER'
    loading_row.label(text=f"{current_char} {props.loading_message}")
    col.separator()
    
    # Cancel button
    cancel_row = col.row()
    cancel_row.alignment = 'CENTER'
    cancel_row.scale_y = 0.8
    # op = cancel_row.operator("mixar.cancel_operation", text="Cancel", icon='X')
    
    # Force immediate redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()