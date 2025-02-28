import bpy
from ..api.client import MixarAPIClient
from ..utils.error_handling import operator_error_handler, show_error

class OBJECT_OT_submit_operator(bpy.types.Operator):
    """Operator for submitting user input"""
    bl_idname = "object.submit_operator"
    bl_label = "Submit"
    
    @operator_error_handler
    def execute(self, context):
        custom_props = context.scene.custom_panel_props

        if custom_props.active_tab == 'TAB1':
            # return self._handle_tab1(context, custom_props)
            return self._handle_tab1_async(context, custom_props)
        elif custom_props.active_tab == 'TAB2':
            # return self._handle_tab2(context, custom_props)
            return self._handle_tab2_async(context, custom_props)
        elif custom_props.active_tab == 'TAB3':
            return self._handle_tab3_async(context, custom_props)
        
        return {'FINISHED'}

    def _handle_tab1(self, context, props):
        api_client = MixarAPIClient()
        user_message = props.user_input
        if not user_message.strip():
            # self.report({'ERROR'}, "Please enter a message")
            show_error("Please enter a message", width=250, height=150)
            return {'CANCELLED'}
        
        # Set loading state
        props.is_loading = True
        props.loading_message = "Sending message..."
        self.force_ui_update(context)
        
        bpy.ops.chat.add_message(content=user_message, is_user=True)
        
        try:
            if props.thread_id_tab1:
                response = api_client.send_chat_message(
                    props.thread_id_tab1, 
                    user_message
                )
            else:
                props.loading_message = "Creating new thread..."
                self.force_ui_update(context)
                response = api_client.create_chat_thread(
                    user_message, 
                    props.image_url
                )
                if response:
                    props.thread_id_tab1 = response.get("thread_id", "")
            
            if response:
                ai_response = response.get("message", "Sorry, I couldn't process that.")
                bpy.ops.chat.add_message(content=ai_response, is_user=False)
            else:
                bpy.ops.chat.add_message(
                    content="Error: Couldn't connect to the server.",
                    is_user=False
                )
                show_error("Error: Couldn't connect to the server.", width=250, height=150)
            # props.user_input = ""
            return {'FINISHED'}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            show_error(error_msg, width=250, height=150)
            bpy.ops.chat.add_message(content=error_msg, is_user=False)
            props.user_input = ""
            return {'CANCELLED'}
            
    def _handle_tab1_async(self, context, props):
        if not props.user_input.strip():
            show_error("Please enter a message", width=250, height=150)
            return {'CANCELLED'}
        
        # Add user message to chat
        bpy.ops.chat.add_message(content=props.user_input, is_user=True)
        
        # Start async operation
        bpy.ops.mixar.async_operation(
            'INVOKE_DEFAULT',
            operation="chat",
            message=props.user_input,
            thread_id=props.thread_id_tab1,
            image_url=props.image_url
        )
        
        return {'FINISHED'}
        

    def _handle_tab2(self, context, props):
        api_client = MixarAPIClient()
        self.report({'INFO'}, f"Tab 2: User Input - {props.user_input}, Image URL - {props.image_url}")
        # bpy.ops.chat.add_message(content=props.user_input, is_user=True)
        
        try:
            if not props.user_input.strip():
                # self.report({'ERROR'}, "Please enter a message")
                show_error("Please enter a message", width=250, height=150)
                return {'CANCELLED'}
            if not props.image_url.strip():
                # self.report({'ERROR'}, "Please provide an image URL")
                show_error("Please provide an image URL", width=250, height=150)
                return {'CANCELLED'}
            response = api_client.generate_description(
                props.user_input,
                props.image_url
            )
            
            if response:
                props.thread_id_tab2 = response.get("thread_id", "")
                self._process_description_response(props, response)
                self.report({'INFO'}, "Description generated and displayed.")
            else:
                self.report({'ERROR'}, "API call failed")
        except Exception as e:
            self.report({'ERROR'}, f"Error during API call: {str(e)}")
        
        return {'FINISHED'}

    def _handle_tab2_async(self, context, props):
        if not props.user_input.strip():
                # self.report({'ERROR'}, "Please enter a message")
                show_error("Please enter a message", width=250, height=150)
                return {'CANCELLED'}
        if not props.image_url.strip():
            # self.report({'ERROR'}, "Please provide an image URL")
            show_error("Please provide an image URL", width=250, height=150)
            return {'CANCELLED'}
        
        # Start async operation
        bpy.ops.mixar.async_operation(
            'INVOKE_DEFAULT',
            operation="generate_description",
            message=props.user_input,
            thread_id=props.thread_id_tab2,
            image_url=props.image_url
        )
        
        return {'FINISHED'}
    
    def _process_description_response(self, props, response):
        import json
        description_json = response.get("description", "{}")
        description_data = json.loads(description_json)
        
        props.analysis_results.clear()
        
        for component in description_data.get('components', []):
            item = props.analysis_results.add()
            item.component = component.get("component", "")
            item.count = component.get("count", 0)
            item.basic_shape = component.get("basic_shape", "")
            item.description = component.get("visual_characteristics", "")
            
    def force_ui_update(self, context):
        """Force the UI to update"""
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'UI':
                        region.tag_redraw()
            area.tag_redraw()
            
    def _handle_tab3_async(self, context, props):
        if not props.user_input_for_scripting.strip():
            show_error("Please enter a message", width=250, height=150)
            return {'CANCELLED'}
        
        bpy.ops.chat.add_script(content=props.user_input_for_scripting, is_user=True)
        bpy.ops.mixar.async_operation(
            'INVOKE_DEFAULT',
            operation="scripting",
            message=props.user_input_for_scripting,
            image_url=props.image_url_for_scripting,
            script_thread_id=props.thread_id_tab3
        )
        
        return {'FINISHED'}
