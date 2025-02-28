import bpy
import requests
import json
import asyncio
import aiohttp
from ..config import API_ENDPOINTS

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class MixarAPIClient:
    """Client for interacting with the Mixar API"""
    
    def __init__(self):
        self.licence_key = None
        self.user_id = None
        try:
            name = __name__
            module_name = name.split(".")[0]
            prefs = bpy.context.preferences.addons.get(module_name)
            if prefs:
                self.licence_key = prefs.preferences.license_key
                self.user_id = prefs.preferences.user_id
        except Exception as e:
            print(f"Error: {str(e)}")
            
        if not self.licence_key or not self.user_id:
            raise APIError("Licence key or user ID not found, Please set the License Key and User ID in the addon preferences.")
    
    @staticmethod
    def _handle_response(response, error_message="API request failed"):
        """Handle API response and raise appropriate errors"""
        try:
            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(f"{error_message}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {str(e)}")
    
    def _get_headers(self):
        """Get the headers for the API request"""
        return {
            'Content-Type': 'application/json',
            'X-User-ID': self.user_id,
            'X-License-Key': self.licence_key
        }

    def create_chat_thread(self, prompt, image_url=None):
        """Create a new chat thread"""
        try:
            print(f"Creating chat thread with prompt: {prompt} and image_url: {image_url}, endpoint: {API_ENDPOINTS['create_thread']}")
            response = requests.post(
                API_ENDPOINTS["create_thread"],
                params={
                    "prompt": prompt,
                    "image_url": image_url
                },
                headers=self._get_headers()
            )
            print(f"Response: {response}")
            return self._handle_response(
                response, 
                "Failed to create chat thread"
            )
        except Exception as e:
            raise APIError(f"Error creating chat thread, Exception: {str(e)}")

    def send_chat_message(self, thread_id, prompt):
        """Send a message to an existing chat thread"""
        try:
            response = requests.post(
                API_ENDPOINTS["continue_chat"],
                params={
                    "thread_id": thread_id,
                    "prompt": prompt
                },
                headers=self._get_headers()
            )
            return self._handle_response(
                response, 
                "Failed to send chat message"
            )
        except Exception as e:
            raise APIError(f"Error sending chat message, Exception: {str(e)}")

    def generate_description(self, prompt, image_url):
        """Generate description from image and prompt"""
        try:
            response = requests.post(
                API_ENDPOINTS["generate_description"],
                params={
                    "prompt": prompt,
                    "image_url": image_url
                },
                headers=self._get_headers()
            )
            return self._handle_response(
                response, 
                "Failed to generate description"
            )
        except Exception as e:
            raise APIError(f"Error generating description, Exception: {str(e)}")

    def generate_script(self, thread_id):
        """Generate Blender script from thread"""
        try:
            response = requests.post(
                API_ENDPOINTS["generate_script"],
                params={"thread_id": thread_id},
                headers=self._get_headers()
            )
            return self._handle_response(
                response, 
                "Failed to generate script"
            )
        except Exception as e:
            raise APIError(f"Error generating script, Exception: {str(e)}")

    @staticmethod
    def extract_python_code(script_content):
        """Extract Python code from markdown-formatted script content"""
        if '```python' in script_content:
            try:
                code = script_content.split('```python')[1].split('```')[0]
                return code.strip()
            except IndexError:
                raise APIError("Invalid script format")
        return script_content.strip()

class AsyncMixarAPIClient:
    def __init__(self):
        self._session = None
        # Initialize timeout settings
        self.timeout = aiohttp.ClientTimeout(
            total=60,     # Total timeout
            connect=10,   # Connection timeout
            sock_read=50  # Socket read timeout
        )
        self.max_retries = 3
        self.retry_delay = 1
        
        self.licence_key = None
        self.user_id = None
        try:
            name = __name__
            module_name = name.split(".")[0]
            prefs = bpy.context.preferences.addons.get(module_name)
            if prefs:
                self.licence_key = prefs.preferences.license_key
                self.user_id = prefs.preferences.user_id
        except Exception as e:
            print(f"Error: {str(e)}")
            
        if not self.licence_key or not self.user_id:
            raise APIError("Licence key or user ID not found, Please set the License Key and User ID in the addon preferences.")
    
    async def _ensure_session(self):
        """Ensure we have an active session"""
        if not self._session or self._session.closed:
            print("Creating new session...")
            connector = aiohttp.TCPConnector(
                force_close=False,
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=connector,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
        return self._session
    
    def _get_headers(self):
        """Get the headers for the API request"""
        return {
            'Content-Type': 'application/json',
            'X-User-ID': self.user_id,
            'X-License-Key': self.licence_key
        }

    async def create_chat_thread(self, prompt, image_url=None):
        """Create a new chat thread asynchronously"""
        session = await self._ensure_session()
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}")
                params = {"prompt": prompt}
                if image_url:
                    params["image_url"] = image_url
                
                print(f"Making request to {API_ENDPOINTS['create_thread']}")
                print(f"With params: {params}")
                
                async with session.post(
                    API_ENDPOINTS['create_thread'],
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                ) as response:
                    print(f"Response: {response}")
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        raise APIError(f"Request failed: {response.status}, {text}")
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                continue
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError(f"Failed after {self.max_retries} attempts: {str(last_error)}")

    async def close(self):
        """Close the session properly"""
        if self._session and not self._session.closed:
            print("Closing session...")
            await self._session.close()
            self._session = None
            print("Session closed")
    
    
    async def send_chat_message(self, thread_id, message):
        """Send a chat message asynchronously"""
        session = await self._ensure_session()
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}")
                params = {
                    "thread_id": thread_id,
                    "prompt": message
                }
                
                print(f"Making request to {API_ENDPOINTS['continue_chat']}")
                print(f"With params: {params}")
                
                async with session.post(
                    API_ENDPOINTS['continue_chat'],
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                ) as response:
                    print(f"Response chat: {response}")
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        raise APIError(f"Request failed: {response.status}, {text}")
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                continue
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError(f"Failed after {self.max_retries} attempts: {str(last_error)}")
 
    async def generate_description(self, prompt, image_url):
        """Generate description from image and prompt asynchronously"""
        session = await self._ensure_session()
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}")
                params = {
                    "prompt": prompt,
                    "image_url": image_url
                }
                
                print(f"Making request to {API_ENDPOINTS['generate_description']}")
                print(f"With params: {params}")
                
                async with session.post(
                    API_ENDPOINTS['generate_description'],
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                ) as response:
                    print(f"Response: {response}")
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        raise APIError(f"Request failed: {response.status}, {text}")
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                continue
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError(f"Failed after {self.max_retries} attempts: {str(last_error)}")
    
    async def generate_script(self, thread_id):
        """Generate Blender script from thread asynchronously"""
        session = await self._ensure_session()
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}")
                params = {"thread_id": thread_id}
                
                print(f"Making request to {API_ENDPOINTS['generate_script']}")
                print(f"With params: {params}")
                
                async with session.post(
                    API_ENDPOINTS['generate_script'],
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                ) as response:
                    print(f"Response: {response}")
                    if response.status == 200:
                        # print(f"Response script: {await response.json()}")
                        return await response.json()
                    else:
                        text = await response.text()
                        raise APIError(f"Request failed: {response.status}, {text}")
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                continue
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError(f"Failed after {self.max_retries} attempts: {str(last_error)}")
    
    async def create_thread_and_generate_script(self, prompt, image_url=None):
        session = await self._ensure_session()
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}")
                params = {"prompt": prompt}
                if image_url:
                    params["image_url"] = image_url
                
                print(f"Making request to {API_ENDPOINTS['create_thread_and_generate_script']}")
                print(f"With params: {params}")
                
                async with session.post(
                    API_ENDPOINTS['create_thread_and_generate_script'],
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                ) as response:
                    print(f"Response: {response}")
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        raise APIError(f"Request failed: {response.status}, {text}")
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                continue
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError(f"Failed after {self.max_retries} attempts: {str(last_error)}")
    
    
    async def continue_script_generation(self, thread_id, message):
        """Send a chat message asynchronously"""
        session = await self._ensure_session()
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries}")
                params = {
                    "thread_id": thread_id,
                    "prompt": message
                }
                
                print(f"Making request to {API_ENDPOINTS['continue_script_generation']}")
                print(f"With params: {params}")
                
                async with session.post(
                    API_ENDPOINTS['continue_script_generation'],
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                ) as response:
                    print(f"Response script: {response}")
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        raise APIError(f"Request failed: {response.status}, {text}")
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                print(f"Network error on attempt {attempt + 1}: {str(e)}")
                last_error = e
                attempt += 1
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                continue
                
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
        
        raise APIError(f"Failed after {self.max_retries} attempts: {str(last_error)}")