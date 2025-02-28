
# API Configuration
API_BASE_URL = "https://ai.mixar.app/api/blender-plugin"
# API_BASE_URL = "http://localhost:8000/api/blender-plugin"
API_ENDPOINTS = {
    "continue_chat": f"{API_BASE_URL}/v1/chat/",
    "create_thread": f"{API_BASE_URL}/v1/create_chat_thread/",
    "generate_description": f"{API_BASE_URL}/v1/generate_description/",
    "generate_script": f"{API_BASE_URL}/v1/generate_script/",
    "create_thread_and_generate_script": f"{API_BASE_URL}/v2/create-thread-and-generate-script/",
    "continue_script_generation": f"{API_BASE_URL}/v2/continue-script-generation/"
}