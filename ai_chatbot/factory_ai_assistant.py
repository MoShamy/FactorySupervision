import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Object-Oriented Message Classes
class Message:
    """Base class for all message types"""
    def __init__(self, content):
        self.content = content
        self.role = None
    
    def to_dict(self):
        """Convert message to dictionary format for OpenAI API"""
        return {
            "role": self.role,
            "content": self.content
        }

class SystemMessage(Message):
    """System message for setting AI behavior and context"""
    def __init__(self, content):
        super().__init__(content)
        self.role = "system"

class UserMessage(Message):
    """User message for user queries and inputs"""
    def __init__(self, content):
        super().__init__(content)
        self.role = "user"

class AssistantMessage(Message):
    """Assistant message for AI responses"""
    def __init__(self, content):
        super().__init__(content)
        self.role = "assistant"

class FunctionMessage(Message):
    """Function message for function call results"""
    def __init__(self, content, function_name):
        super().__init__(content)
        self.role = "function"
        self.function_name = function_name
    
    def to_dict(self):
        """Convert function message to dictionary format for OpenAI API"""
        return {
            "role": self.role,
            "name": self.function_name,
            "content": self.content
        }

# Object-Oriented Messenger Classes
class Messenger:
    """Base class for all messenger types"""
    def __init__(self, name):
        self.name = name
        self.messages = []
    
    def add_message(self, message):
        """Add a message to the messenger's message history"""
        self.messages.append(message)
    
    def get_messages_dict(self):
        """Get all messages in dictionary format for API"""
        return [msg.to_dict() for msg in self.messages]

class UserMessenger(Messenger):
    """User messenger for handling user interactions"""
    def __init__(self, name="User"):
        super().__init__(name)
    
    def send_message(self, content):
        """Send a user message"""
        user_msg = UserMessage(content)
        self.add_message(user_msg)
        return user_msg

class AIBotMessenger(Messenger):
    """AI Bot messenger for handling AI assistant interactions with Azure OpenAI setup"""
    def __init__(self, name="AI Assistant"):
        super().__init__(name)
        
        # Load Azure OpenAI credentials from environment variables
        openai.api_type = os.getenv("AZURE_API_TYPE", "azure")
        openai.api_base = os.getenv("AZURE_ENDPOINT") or os.getenv("AZURE_API_BASE")
        openai.api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        openai.api_key = os.getenv("AZURE_API_KEY")
        self.engine = os.getenv("AZURE_DEPLOYMENT_NAME") or os.getenv("AZURE_ENGINE", "gpt-35-turbo")
        
        # Validate that required environment variables are set
        if not openai.api_key:
            raise ValueError("AZURE_API_KEY environment variable is required")
        if not openai.api_base:
            raise ValueError("AZURE_ENDPOINT or AZURE_API_BASE environment variable is required")
        
        # Initialize system message
        system_content = (
            "You are a helpful assistant that only answers questions about the conveyor belt system. "
            "You should respond to queries related to machine status, object detection, object counts, conveyor operations, and system stoppages. "
            "You have access to functions to check machine status, get activity logs, and detect objects on the conveyor belt. "
            "If the question is completely unrelated to the conveyor system, say: 'Sorry, I can only help with conveyor system operations.'"
        )
        system_msg = SystemMessage(system_content)
        self.add_message(system_msg)
        
        # Define available functions
        self.functions = [
            {
                "name": "get_machine_status",
                "description": "Check if the machine is running",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_activity_log",
                "description": "Get the activity log of the machine",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_objects_on_belt",
                "description": "Get information about objects currently detected on the conveyor belt",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_object_count",
                "description": "Get the count of objects detected on the conveyor belt",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def respond_to(self, user_message):
        """Generate AI response to user message"""
        # Add user message to conversation
        self.add_message(user_message)
        
        # Get all messages for API call
        all_messages = self.get_messages_dict()
        
        # Call Azure OpenAI
        response = openai.ChatCompletion.create(
            engine=self.engine,
            messages=all_messages,
            functions=self.functions,
            function_call="auto"
        )
        
        response_message = response["choices"][0]["message"]
        
        # Handle function calls if present
        if "function_call" in response_message:
            return self._handle_function_call(response_message, all_messages)
        else:
            assistant_msg = AssistantMessage(response_message["content"])
            self.add_message(assistant_msg)
            return assistant_msg
    
    def _handle_function_call(self, response_message, all_messages):
        """Handle function call execution"""
        function_name = response_message["function_call"]["name"]
        
        # Add assistant's function call message
        all_messages.append(response_message)
        
        # Execute function and add result
        if function_name == "get_machine_status":
            function_result = FunctionMessage(str(get_machine_status()), function_name)
        elif function_name == "get_activity_log":
            function_result = FunctionMessage(str(get_activity_log()), function_name)
        elif function_name == "get_objects_on_belt":
            function_result = FunctionMessage(str(get_objects_on_belt()), function_name)
        elif function_name == "get_object_count":
            function_result = FunctionMessage(str(get_object_count()), function_name)
        else:
            function_result = FunctionMessage("Function not found", function_name)
        
        all_messages.append(function_result.to_dict())
        
        # Get final response
        final_response = openai.ChatCompletion.create(
            engine=self.engine,
            messages=all_messages
        )
        
        final_assistant_msg = AssistantMessage(final_response["choices"][0]["message"]["content"])
        self.add_message(final_assistant_msg)
        return final_assistant_msg

# Define simulated backend functions
def get_machine_status():
    return {"status": "Running"}

def get_activity_log():
    return {
        "Log": """Machine 1: Stopped Tuesday 11:30 AM
Machine 1: Started Tuesday 3:30 PM
Machine 3: Stopped Tuesday 11:30 AM
Machine 2: Stopped Tuesday 11:30 AM"""
    }

def get_objects_on_belt():
    return {
        "objects": [
            {"type": "product_box", "position": "belt_section_1", "confidence": 0.95},
            {"type": "product_box", "position": "belt_section_3", "confidence": 0.87},
            {"type": "package", "position": "belt_section_5", "confidence": 0.92}
        ],
        "total_count": 3
    }

def get_object_count():
    return {"count": 3, "timestamp": "2025-07-22 10:30:00"}

# Main execution using the new Messenger classes
if __name__ == "__main__":
    # Create messengers
    user = UserMessenger("Factory Operator")
    ai_bot = AIBotMessenger("Conveyor Assistant")
    
    # User sends a message
    user_message = user.send_message("What are the objects on the conveyor belt?")
    
    # AI bot responds
    ai_response = ai_bot.respond_to(user_message)
    
    # Print the conversation
    print(f"{user.name}: {user_message.content}")
    print(f"{ai_bot.name}: {ai_response.content}")
