"""
AI Chatbot Service for Factory Supervision System
Integrates with OpenAI to provide intelligent assistance based on production logs
"""

import os
import json
import asyncio
import aiofiles
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogWatcher(FileSystemEventHandler):
    """Watches for changes in log files and triggers AI updates"""
    
    def __init__(self, chatbot_service):
        self.chatbot_service = chatbot_service
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.log'):
            logger.info(f"Log file modified: {event.src_path}")
            # Run async function in thread
            threading.Thread(
                target=self.chatbot_service.handle_log_update,
                args=(event.src_path,),
                daemon=True
            ).start()

class AIChatbotService:
    """AI Chatbot service that maintains context from production logs"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=os.getenv('AZURE_API_KEY'),
            base_url=f"{os.getenv('AZURE_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_DEPLOYMENT_NAME')}",
            default_query={"api-version": os.getenv('AZURE_API_VERSION')}
        )
        
        # System context and memory
        self.system_context = []
        self.conversation_history = []
        self.log_memory = {}
        self.last_log_position = {}
        
        # File paths
        self.logs_dir = "/Users/mostafa/Desktop/FactorySupervision/logs"
        self.context_file = "/Users/mostafa/Desktop/FactorySupervision/backend/chatbot_context.json"
        
        # Initialize file watcher
        self.observer = Observer()
        self.log_watcher = LogWatcher(self)
        
        # Available functions for the AI
        self.available_functions = {
            "get_system_status": self.get_system_status,
            "get_recent_logs": self.get_recent_logs,
            "analyze_production_trends": self.analyze_production_trends,
            "get_error_summary": self.get_error_summary,
            "restart_system": self.restart_system,
            "refresh_status": self.refresh_status
        }
        
    async def initialize(self):
        """Initialize the chatbot service on startup"""
        logger.info("Initializing AI Chatbot Service...")
        
        # Load existing context if available
        await self.load_context()
        
        # Read all log files on startup
        await self.read_all_logs_on_startup()
        
        # Start file watcher
        self.start_log_watcher()
        
        # Initialize system context for AI
        await self.initialize_ai_context()
        
        logger.info("AI Chatbot Service initialized successfully")
        
    async def load_context(self):
        """Load existing context from file"""
        try:
            if os.path.exists(self.context_file):
                async with aiofiles.open(self.context_file, 'r') as f:
                    data = json.loads(await f.read())
                    self.log_memory = data.get('log_memory', {})
                    self.last_log_position = data.get('last_log_position', {})
                    logger.info("Loaded existing chatbot context")
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            
    async def save_context(self):
        """Save current context to file"""
        try:
            context_data = {
                'log_memory': self.log_memory,
                'last_log_position': self.last_log_position,
                'last_updated': datetime.now().isoformat()
            }
            async with aiofiles.open(self.context_file, 'w') as f:
                await f.write(json.dumps(context_data, indent=2))
        except Exception as e:
            logger.error(f"Error saving context: {e}")
            
    async def read_all_logs_on_startup(self):
        """Read all log files on startup to build initial context"""
        logger.info("Reading all logs to build initial context...")
        
        try:
            log_files = []
            for file in os.listdir(self.logs_dir):
                if file.endswith('.log'):
                    log_files.append(os.path.join(self.logs_dir, file))
            
            for log_file in log_files:
                await self.process_log_file(log_file, initial_load=True)
                
            # Save context after initial load
            await self.save_context()
            
            logger.info(f"Processed {len(log_files)} log files on startup")
            
        except Exception as e:
            logger.error(f"Error reading logs on startup: {e}")
            
    async def process_log_file(self, log_file: str, initial_load: bool = False):
        """Process a log file and extract relevant information"""
        try:
            file_key = os.path.basename(log_file)
            
            async with aiofiles.open(log_file, 'r') as f:
                lines = await f.readlines()
                
            # Get new lines since last read
            last_position = self.last_log_position.get(file_key, 0)
            new_lines = lines[last_position:] if not initial_load else lines
            
            if new_lines:
                # Process new log entries
                log_entries = []
                for line in new_lines:
                    if line.strip():
                        log_entries.append({
                            'timestamp': datetime.now().isoformat(),
                            'content': line.strip(),
                            'file': file_key
                        })
                
                # Update memory
                if file_key not in self.log_memory:
                    self.log_memory[file_key] = []
                
                self.log_memory[file_key].extend(log_entries)
                
                # Keep only recent entries (last 1000 per file)
                self.log_memory[file_key] = self.log_memory[file_key][-1000:]
                
                # Update position
                self.last_log_position[file_key] = len(lines)
                
                # Send to AI if not initial load
                if not initial_load and new_lines:
                    await self.send_log_update_to_ai(log_entries)
                
        except Exception as e:
            logger.error(f"Error processing log file {log_file}: {e}")
            
    async def send_log_update_to_ai(self, log_entries: List[Dict]):
        """Send new log entries to AI for context update"""
        try:
            log_summary = "\n".join([f"[{entry['file']}] {entry['content']}" for entry in log_entries])
            
            context_message = f"""
New log entries from factory supervision system:
{log_summary}

Please update your context about the factory's current state based on these logs.
These are real-time updates from the production line monitoring system.
"""
            
            # Add to conversation history for context
            self.conversation_history.append({
                "role": "system",
                "content": context_message
            })
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-40:]
                
            logger.info(f"Sent {len(log_entries)} new log entries to AI context")
            
        except Exception as e:
            logger.error(f"Error sending log update to AI: {e}")
            
    async def initialize_ai_context(self):
        """Initialize AI with current system context"""
        try:
            # Prepare system context from all logs
            recent_logs = []
            for file_key, entries in self.log_memory.items():
                recent_logs.extend(entries[-20:])  # Last 20 entries per file
            
            system_message = f"""
You are an AI assistant for a factory supervision system. You have access to real-time production logs and can help monitor, analyze, and troubleshoot the manufacturing line.

Current System Context:
- Factory Supervision System with computer vision monitoring
- YOLO-based object detection for production line
- Real-time status tracking and anomaly detection
- Log-based system state management

Recent Log History:
{chr(10).join([f"[{entry['file']}] {entry['content']}" for entry in recent_logs[-50:]])}

Available Functions:
- get_system_status: Get current system operational status
- get_recent_logs: Retrieve recent log entries
- analyze_production_trends: Analyze production patterns and trends
- get_error_summary: Get summary of recent errors or issues
- restart_system: Restart system components if needed
- refresh_status: Refresh system status from logs

You can call these functions to help users with factory monitoring and troubleshooting.
Provide intelligent assistance based on the log data and system status.
"""

            self.system_context = [{"role": "system", "content": system_message}]
            logger.info("AI context initialized with current system state")
            
        except Exception as e:
            logger.error(f"Error initializing AI context: {e}")
            
    def start_log_watcher(self):
        """Start watching log files for changes"""
        try:
            self.observer.schedule(self.log_watcher, self.logs_dir, recursive=False)
            self.observer.start()
            logger.info("Started log file watcher")
        except Exception as e:
            logger.error(f"Error starting log watcher: {e}")
            
    def handle_log_update(self, log_file_path: str):
        """Handle log file updates (called by file watcher)"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_log_file(log_file_path))
            loop.run_until_complete(self.save_context())
        finally:
            loop.close()
            
    async def chat(self, user_message: str, conversation_id: str = None) -> Dict[str, Any]:
        """Main chat function with function calling capability"""
        try:
            # Prepare messages for API call
            messages = self.system_context.copy()
            messages.extend(self.conversation_history[-10:])  # Recent conversation
            messages.append({"role": "user", "content": user_message})
            
            # Define function schemas for AI
            functions = [
                {
                    "name": "get_system_status",
                    "description": "Get current system operational status",
                    "parameters": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_recent_logs",
                    "description": "Get recent log entries",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {"type": "integer", "description": "Number of recent entries to retrieve"}
                        }
                    }
                },
                {
                    "name": "analyze_production_trends",
                    "description": "Analyze production patterns and trends",
                    "parameters": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_error_summary",
                    "description": "Get summary of recent errors or issues",
                    "parameters": {"type": "object", "properties": {}}
                }
            ]
            
            # Make API call with function calling
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                # Execute function
                if function_name in self.available_functions:
                    function_result = await self.available_functions[function_name](**function_args)
                    
                    # Send function result back to AI
                    messages.append({"role": "assistant", "content": None, "function_call": message.function_call})
                    messages.append({"role": "function", "name": function_name, "content": json.dumps(function_result)})
                    
                    # Get final response
                    final_response = await self.client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    final_message = final_response.choices[0].message.content
                else:
                    final_message = f"Function {function_name} not available."
            else:
                final_message = message.content
                
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": final_message})
            
            return {
                "response": final_message,
                "timestamp": datetime.now().isoformat(),
                "function_called": message.function_call.name if message.function_call else None
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "error": True
            }
            
    # Function implementations for AI to call
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            import sys
            sys.path.append('/Users/mostafa/Desktop/FactorySupervision/config')
            from system_status import SystemStatusManager
            
            status_manager = SystemStatusManager()
            status_info = status_manager.get_status()
            
            return {
                "status": status_info["status"],
                "functioning": status_info["functioning"],
                "uptime": status_info["uptime"],
                "last_change": status_info["last_change"],
                "recent_history": status_info["recent_history"][-5:]  # Last 5 changes
            }
        except Exception as e:
            return {"error": f"Could not get system status: {e}"}
            
    async def get_recent_logs(self, count: int = 20) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        try:
            all_entries = []
            for file_key, entries in self.log_memory.items():
                all_entries.extend(entries[-count:])
            
            # Sort by timestamp and return most recent
            all_entries.sort(key=lambda x: x.get('timestamp', ''))
            return all_entries[-count:]
        except Exception as e:
            return [{"error": f"Could not get recent logs: {e}"}]
            
    async def analyze_production_trends(self) -> Dict[str, Any]:
        """Analyze production patterns and trends"""
        try:
            # Analyze logs for patterns
            box_detections = []
            stops = []
            resumes = []
            
            for file_key, entries in self.log_memory.items():
                for entry in entries:
                    content = entry['content'].lower()
                    if 'box was detected' in content:
                        box_detections.append(entry)
                    elif 'stopped' in content:
                        stops.append(entry)
                    elif 'returned to normal' in content:
                        resumes.append(entry)
            
            return {
                "box_detections_count": len(box_detections),
                "stops_count": len(stops),
                "resumes_count": len(resumes),
                "latest_detection": box_detections[-1] if box_detections else None,
                "latest_stop": stops[-1] if stops else None,
                "latest_resume": resumes[-1] if resumes else None
            }
        except Exception as e:
            return {"error": f"Could not analyze trends: {e}"}
            
    async def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors or issues"""
        try:
            errors = []
            warnings = []
            
            for file_key, entries in self.log_memory.items():
                for entry in entries:
                    content = entry['content'].lower()
                    if any(keyword in content for keyword in ['error', 'failed', 'exception']):
                        errors.append(entry)
                    elif any(keyword in content for keyword in ['warning', 'stopped', 'anomaly']):
                        warnings.append(entry)
            
            return {
                "errors_count": len(errors),
                "warnings_count": len(warnings),
                "recent_errors": errors[-5:],
                "recent_warnings": warnings[-5:]
            }
        except Exception as e:
            return {"error": f"Could not get error summary: {e}"}
            
    async def restart_system(self) -> Dict[str, Any]:
        """Restart system components"""
        return {"message": "System restart functionality would be implemented here", "status": "simulated"}
        
    async def refresh_status(self) -> Dict[str, Any]:
        """Refresh system status"""
        return await self.get_system_status()
        
    def stop(self):
        """Stop the chatbot service"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        logger.info("AI Chatbot Service stopped")

# Global instance
chatbot_service = AIChatbotService()
