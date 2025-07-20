import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

class SimplifiedProductionData:
    """
    Simplified data structure for ChatGPT analysis.
    Reduces 30KB+ verbose YOLO output to ~7KB business-focused metrics.
    """
    
    def __init__(self):
        self.timestamp = None
        self.total_objects = 0
        self.objects_by_type = {}
        self.quality_metrics = {}
        self.production_rate = 0.0
        self.alerts = []
        self.efficiency_score = 0.0
    
    @classmethod
    def from_yolo_output(cls, yolo_data: Dict[str, Any]) -> 'SimplifiedProductionData':
        """Convert verbose YOLO output to simplified format."""
        simplified = cls()
        
        # Basic info
        simplified.timestamp = datetime.now().isoformat()
        
        # Extract objects and count them
        detections = yolo_data.get('detections', [])
        simplified.total_objects = len(detections)
        
        # Group by object type
        type_counts = {}
        confidences_by_type = {}
        
        for detection in detections:
            obj_type = detection.get('class', 'unknown')
            confidence = detection.get('confidence', 0.0)
            
            # Count objects
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            
            # Track confidence scores
            if obj_type not in confidences_by_type:
                confidences_by_type[obj_type] = []
            confidences_by_type[obj_type].append(confidence)
        
        simplified.objects_by_type = type_counts
        
        # Calculate quality metrics
        for obj_type, confidences in confidences_by_type.items():
            if confidences:
                simplified.quality_metrics[obj_type] = {
                    'avg_confidence': round(statistics.mean(confidences), 2),
                    'min_confidence': round(min(confidences), 2),
                    'max_confidence': round(max(confidences), 2)
                }
        
        # Calculate production rate (objects per minute - simplified)
        frame_count = yolo_data.get('frame_count', 1)
        fps = yolo_data.get('fps', 30)
        time_seconds = frame_count / fps if fps > 0 else 1
        simplified.production_rate = round((simplified.total_objects / time_seconds) * 60, 1)
        
        # Generate alerts for low confidence or missing objects
        for obj_type, metrics in simplified.quality_metrics.items():
            if metrics['avg_confidence'] < 0.7:
                simplified.alerts.append(f"Low confidence detected for {obj_type}: {metrics['avg_confidence']}")
        
        # Calculate overall efficiency (simplified)
        if simplified.quality_metrics:
            all_confidences = []
            for metrics in simplified.quality_metrics.values():
                all_confidences.append(metrics['avg_confidence'])
            simplified.efficiency_score = round(statistics.mean(all_confidences) * 100, 1)
        
        return simplified
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp,
            'summary': {
                'total_objects': self.total_objects,
                'production_rate_per_minute': self.production_rate,
                'efficiency_score': f"{self.efficiency_score}%"
            },
            'objects_detected': self.objects_by_type,
            'quality_metrics': self.quality_metrics,
            'alerts': self.alerts
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def get_chatgpt_summary(self) -> str:
        """Get a concise summary for ChatGPT analysis."""
        summary = f"Production Analysis at {self.timestamp}:\n"
        summary += f"- Total objects detected: {self.total_objects}\n"
        summary += f"- Production rate: {self.production_rate} objects/minute\n"
        summary += f"- Overall efficiency: {self.efficiency_score}%\n"
        
        if self.objects_by_type:
            summary += "\nObject breakdown:\n"
            for obj_type, count in self.objects_by_type.items():
                summary += f"  - {obj_type}: {count}\n"
        
        if self.alerts:
            summary += f"\n⚠️ Alerts ({len(self.alerts)}):\n"
            for alert in self.alerts[:3]:  # Limit to top 3 alerts
                summary += f"  - {alert}\n"
        
        return summary

def simplify_for_chatgpt(complex_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to convert complex YOLO/CV output to ChatGPT-friendly format.
    
    Args:
        complex_data: Original verbose computer vision output
        
    Returns:
        Simplified dictionary optimized for ChatGPT analysis
    """
    simplified = SimplifiedProductionData.from_yolo_output(complex_data)
    return simplified.to_dict()

# Example usage and test
if __name__ == "__main__":
    # Sample complex YOLO data
    sample_yolo_data = {
        'detections': [
            {'class': 'product', 'confidence': 0.95, 'bbox': [100, 100, 200, 200]},
            {'class': 'product', 'confidence': 0.87, 'bbox': [300, 150, 400, 250]},
            {'class': 'defect', 'confidence': 0.65, 'bbox': [150, 200, 180, 230]},
            {'class': 'product', 'confidence': 0.92, 'bbox': [500, 100, 600, 200]}
        ],
        'frame_count': 180,
        'fps': 30,
        'processing_time': 0.05,
        'model_info': {'name': 'yolov8', 'version': '8.0.0'},
        'metadata': {'camera_id': 'cam_01', 'resolution': '1920x1080'}
    }
    
    # Convert to simplified format
    simplified = simplify_for_chatgpt(sample_yolo_data)
    
    print("Original data size:", len(json.dumps(sample_yolo_data)))
    print("Simplified data size:", len(json.dumps(simplified)))
    print("\nSimplified output:")
    print(json.dumps(simplified, indent=2))
    
    # Create detailed object for summary
    detailed_obj = SimplifiedProductionData.from_yolo_output(sample_yolo_data)
    print("\nChatGPT Summary:")
    print(detailed_obj.get_chatgpt_summary())
