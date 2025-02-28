import bpy
import asyncio
from ..api.client import AsyncMixarAPIClient, APIError
from ..utils.error_handling import show_error
import json
    
active_async_operators = []

class MIXAR_OT_async_operation(bpy.types.Operator):
    """Async operation handler"""
    bl_idname = "mixar.async_operation"
    bl_label = "Async Operation"
    
    operation: bpy.props.StringProperty(
        name="Operation",
        description="Type of async operation",
        default="chat"
    )
    
    message: bpy.props.StringProperty(
        name="Message",
        description="Message content",
        default=""
    )
    
    thread_id: bpy.props.StringProperty(
        name="Thread ID",
        description="Thread ID for chat operations",
        default=""
    )
    
    image_url: bpy.props.StringProperty(
        name="Image URL",
        description="URL of the image",
        default=""
    )
    script_thread_id: bpy.props.StringProperty(
        name="Script Thread ID",
        description="Thread ID for script operations",
        default=""
    )
    
    _timer = None
    _task = None
    _running = False
    
    async def async_operation(self):
        """Execute the appropriate async operation"""
        client = None
        try:
            # Create a new client for each operation
            client = AsyncMixarAPIClient()
            
            if self.operation == "chat":
                print(f"Sending chat message with thread_id: {self.thread_id} and message: {self.message}")
                if self.thread_id:
                    return await client.send_chat_message(self.thread_id, self.message)
                else:
                    return await client.create_chat_thread(self.message, self.image_url)
            elif self.operation == "generate_description":
                return await client.generate_description(self.message, self.image_url)
            elif self.operation == "generate_script":
                return await client.generate_script(self.thread_id)
            elif self.operation == "scripting":
                if self.script_thread_id:
                    return await client.continue_script_generation(self.script_thread_id, self.message)
                else:
                    return await client.create_thread_and_generate_script(self.message, self.image_url)
            else:
                raise APIError(f"Unknown operation: {self.operation}")
        except Exception as e:
            print(f"Error in async_operation: {str(e)}")
            raise
        finally:
            if client:
                await client.close()
    
    def handle_result(self, context, result):
        """Handle successful API response"""
        props = context.scene.custom_panel_props
        
        if self.operation == "chat":
            if not self.thread_id:
                props.thread_id_tab1 = result.get("thread_id", "")
            ai_response = result.get("message", "Sorry, I couldn't process that.")
            bpy.ops.chat.add_message(content=ai_response, is_user=False)
            
        elif self.operation == "generate_description":
            if result.get("status") != "success":
                show_error(result.get("description", "Sorry, I couldn't process that."), width=250, height=150)
                return {'CANCELLED'}
            props.thread_id_tab2 = result.get("thread_id", "")
            description_json = result.get("description", "{}")
            if not description_json:
                show_error("No description received from the API.", width=250, height=150)
                return {'CANCELLED'}
            description_data = json.loads(description_json)
            props.analysis_results.clear()
            for component in description_data.get('components', []):
                item = props.analysis_results.add()
                item.component = component.get("component", "")
                item.count = component.get("count", 0)
                item.basic_shape = component.get("basic_shape", "")
                item.description = component.get("visual_characteristics", "")
                
        elif self.operation == "generate_script":
            if result.get("status") != "success":
                show_error(result.get("message", "Error while generating script"), width=250, height=150)
                return {'CANCELLED'}
            script_content = result.get("script", "")
            self._handle_generated_script(script_content, context, props)
        elif self.operation == "scripting":
            if result.get("status") != "success":
                show_error(result.get("message", "Error while generating script"), width=250, height=150)
                return {'CANCELLED'}
            if not self.script_thread_id:
                props.thread_id_tab3 = result.get("thread_id", "")
            ai_message = result.get("message", "Sorry, I couldn't process that.")
            bpy.ops.chat.add_script(content=ai_message, is_user=False)
            script_content = result.get("script", "")
            self._handle_generated_script(script_content, context, props)
    
    def _handle_generated_script(self, script_content, context, props):
        if script_content:
            if '```python' in script_content:
                script_lines = script_content.split('```python')[1]
                script_lines = script_lines.split('```')[0]
            else:
                script_lines = script_content
            self._handle_script_execution(script_lines, context, props)
            # Create a new text file in Blender's text editor
            text_name = "Generated_Script.py"
            text = bpy.data.texts.get(text_name)
            if text is None:
                text = bpy.data.texts.new(text_name)
            text.clear()
            text.write(script_lines)
            
            self.report({'INFO'}, f"Script generated and loaded in Text Editor: {text_name}")
        else:
            self.report({'ERROR'}, "No script content received from the API.")
            show_error("No script content received from the API.", width=250, height=150)
            # return {'CANCELLED'}
            
    def _handle_script_execution(self, script_content, context, props):
        try:
            exec(script_content, {'bpy': bpy})
            self.report({'INFO'}, "Script executed successfully.")
        except Exception as e:
            error_msg = f"Error during script execution: {str(e)}"
            show_error(error_msg, width=250, height=150)
            # self.report({'ERROR'}, error_msg)

    def execute(self, context):
        print("Starting async operation...")
        self.props = context.scene.custom_panel_props  # Store props reference
        self.props.is_loading = True
        self.props.loading_message = f"Processing {self.operation}..."
        self._running = True
        
        # Register this operator instance
        active_async_operators.append(self)
        print(f"Registered operator, active count: {len(active_async_operators)}")
        
        
        # Create event loop first
        try:
            self.props.loading_message = f"Creating event loop ..."
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        
        # Set up modal timer
        self._timer = context.window_manager.event_timer_add(0.03, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        # Create task
        self.props.loading_message = f"Task Created ..."
        self._task = self._loop.create_task(self.async_operation())
        
        # Force immediate UI update
        for area in context.screen.areas:
            area.tag_redraw()
        
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            try:
                # Force UI update for loading spinner
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                
                # Ensure loading state stays True while task is running
                if self._task and not self._task.done():
                    self.props.is_loading = True
                    try:
                        self.props.loading_message = f"Processing..."
                        if self.operation == "generate_description":
                            self.props.loading_message = f"Generating description..."
                        if self.operation == "generate_script":
                            self.props.loading_message = f"Generating script..."
                        self._loop.run_until_complete(asyncio.sleep(0))
                    except RuntimeError:
                        self._loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(self._loop)
                        self._loop.run_until_complete(asyncio.sleep(0))
                
                # Only check cancellation if task is done or failed
                if self._task and self._task.done():
                    if self._task.exception():
                        print(f"Task failed: {self._task.exception()}")
                        show_error(str(self._task.exception()), width=350, height=250)
                        self.cleanup(context)
                        return {'FINISHED'}
                    
                    try:
                        self.props.loading_message = f"Completed..."
                        result = self._task.result()
                        self.handle_result(context, result)
                    except Exception as e:
                        print(f"Error in modal: {str(e)}")
                        show_error(str(e), width=250, height=150)
                    finally:
                        self.cleanup(context)
                        return {'FINISHED'}
                        
            except Exception as e:
                print(f"Unexpected error in modal: {str(e)}")
                self.cleanup(context)
                return {'FINISHED'}
                
        return {'PASS_THROUGH'}

    def cleanup(self, context):
        """Clean up resources"""
        print("Starting cleanup...")
        
        # Remove this operator from registry
        # if self in active_async_operators:
        #     active_async_operators.remove(self)
        #     print(f"Unregistered operator, active count: {len(active_async_operators)}")
        
        # if self._task and not self._task.done():
        #     print("Cancelling task...")
        #     self._task.cancel()
        
        # if self._timer:
        #     print("Removing timer...")
        #     context.window_manager.event_timer_remove(self._timer)
        #     self._timer = None
        
        # if hasattr(self, '_loop'):
        #     print("Cleaning up event loop...")
        #     try:
        #         pending = asyncio.all_tasks(self._loop)
        #         for task in pending:
        #             task.cancel()
        #         self._loop.stop()
        #     except Exception as e:
        #         print(f"Error cleaning up event loop: {str(e)}")
        
        # Only set is_loading to False at the very end
        self.props.is_loading = False
        self.props.loading_message = "Processing..."
        self._running = False
        print("Cleanup completed")
    
    def cancel(self, context):
        """Handle cancellation"""
        print("Async operation cancel triggered")
        if self._task and not self._task.done():
            print("Cancelling running task...")
            self._task.cancel()
        
        print("Running cleanup...")
        self.cleanup(context)
        
        # Force UI update
        for area in context.screen.areas:
            area.tag_redraw()
            
        print("Async operation cancelled")
        return {'CANCELLED'}