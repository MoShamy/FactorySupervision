import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from simplified_chatgpt_data import SimplifiedProductionData, simplify_for_chatgpt

# Load environment variables
load_dotenv()

class ProductionChatBot:
    """
    Simplified ChatBot for real-time production analysis.
    Uses optimized data structures for faster ChatGPT processing.
    """
    
    def __init__(self):
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-35-turbo')
        
        if not self.api_key:
            print("⚠️ Warning: AZURE_OPENAI_API_KEY not found in environment variables")
            print("Please set up your .env file with the API key")
    
    def analyze_production_data(self, yolo_output: Dict[str, Any]) -> str:
        """
        Analyze production data using simplified format for faster ChatGPT processing.
        
        Args:
            yolo_output: Raw YOLO/computer vision output
            
        Returns:
            ChatGPT analysis of the production data
        """
        # Step 1: Simplify the data (76.5% size reduction)
        simplified_data = simplify_for_chatgpt(yolo_output)
        
        # Step 2: Create business-focused summary
        detailed_obj = SimplifiedProductionData.from_yolo_output(yolo_output)
        summary = detailed_obj.get_chatgpt_summary()
        
        # Step 3: Send to ChatGPT for analysis
        if self.api_key:
            return self._query_chatgpt(summary, simplified_data)
        else:
            return self._offline_analysis(summary, simplified_data)
    
    def _query_chatgpt(self, summary: str, data: Dict[str, Any]) -> str:
        """Send simplified data to ChatGPT for analysis."""
        
        prompt = f"""
        You are a production line supervisor analyzing real-time factory data.
        
        Current Production Summary:
        {summary}
        
        Detailed Metrics:
        {json.dumps(data, indent=2)}
        
        Please provide:
        1. Overall production status assessment
        2. Any issues or concerns identified
        3. Recommendations for optimization
        4. Priority actions needed
        
        Keep the response concise and actionable for factory floor use.
        """
        
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key
        }
        
        payload = {
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert factory production analyst. Provide clear, actionable insights for production line optimization.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 500,
            'temperature': 0.3
        }
        
        try:
            url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2023-12-01-preview"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"API Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Connection Error: {str(e)}"
    
    def _offline_analysis(self, summary: str, data: Dict[str, Any]) -> str:
        """Provide basic analysis when ChatGPT is not available."""
        
        analysis = "🏭 OFFLINE PRODUCTION ANALYSIS\n\n"
        analysis += f"Summary: {summary}\n\n"
        
        # Basic rule-based analysis
        total_objects = data.get('summary', {}).get('total_objects', 0)
        efficiency = data.get('summary', {}).get('efficiency_score', '0%')
        alerts = data.get('alerts', [])
        
        analysis += "📊 STATUS:\n"
        if total_objects > 10:
            analysis += "✅ Production volume: GOOD\n"
        elif total_objects > 5:
            analysis += "⚠️ Production volume: MODERATE\n"
        else:
            analysis += "🔴 Production volume: LOW\n"
        
        if '90' in efficiency or '95' in efficiency or '100' in efficiency:
            analysis += "✅ Quality efficiency: EXCELLENT\n"
        elif '80' in efficiency or '85' in efficiency:
            analysis += "⚠️ Quality efficiency: GOOD\n"
        else:
            analysis += "🔴 Quality efficiency: NEEDS ATTENTION\n"
        
        if alerts:
            analysis += f"\n⚠️ ALERTS ({len(alerts)}):\n"
            for alert in alerts[:3]:
                analysis += f"- {alert}\n"
            analysis += "\n💡 RECOMMENDATIONS:\n- Review quality control\n- Check camera positioning\n- Verify lighting conditions\n"
        else:
            analysis += "\n✅ No critical alerts detected\n"
        
        return analysis

def main():
    """Example usage of the simplified chatbot."""
    
    # Initialize chatbot
    chatbot = ProductionChatBot()
    
    # Sample production data (simulating YOLO output)
    sample_data = {
        'detections': [
            {'class': 'product', 'confidence': 0.95, 'bbox': [100, 100, 200, 200]},
            {'class': 'product', 'confidence': 0.87, 'bbox': [300, 150, 400, 250]},
            {'class': 'defect', 'confidence': 0.65, 'bbox': [150, 200, 180, 230]},
            {'class': 'product', 'confidence': 0.92, 'bbox': [500, 100, 600, 200]},
            {'class': 'product', 'confidence': 0.88, 'bbox': [700, 200, 800, 300]}
        ],
        'frame_count': 300,
        'fps': 30,
        'processing_time': 0.05
    }
    
    print("🏭 Production ChatBot Analysis")
    print("=" * 50)
    
    # Show data size comparison
    original_size = len(json.dumps(sample_data))
    simplified = simplify_for_chatgpt(sample_data)
    simplified_size = len(json.dumps(simplified))
    
    print(f"📊 Data Optimization:")
    print(f"Original size: {original_size} bytes")
    print(f"Simplified size: {simplified_size} bytes")
    print(f"Reduction: {((original_size - simplified_size) / original_size * 100):.1f}%")
    print()
    
    # Get analysis
    analysis = chatbot.analyze_production_data(sample_data)
    print("🤖 ChatGPT Analysis:")
    print(analysis)

if __name__ == "__main__":
    main()
