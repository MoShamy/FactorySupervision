#!/usr/bin/env python3
"""
FactorySupervision - AI-Powered Production Line Monitoring

This is the main entry point for the Factory Supervision system.
It provides video analysis, production logging, and AI-powered insights.
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from YoloLineTest import OperationStatus

def main():
    """Main pipeline for Factory Supervision."""
    
    
    # Test video path
    test_video = "Slow Only Coffee.mp4"
    
    if os.path.exists(test_video):
        print(f"📹 Analyzing video: {test_video}")
        
        out_path = "logs/production_status.log"
        os.makedirs("logs", exist_ok=True)
        
        line = False  # True for horizontal line, False for vertical line
        fx = 0.5 # Line width position factor 
        fy = 0.7 # line height position factor
        con_line = False # specifies the condition needed whether to check only vertical or horizontal direction or both vertical and horizontal direction of the line
        targets = [2]  # Target classes: Box, Fruit, bag, bottle, jar, mask, pallet
        obj_per_time = 3  # Expected objects per time period
        time_th = 35  # Time threshold for production check (seconds)
        bounds = 1  # Margin of error for object count
        
        # Run analysis
        OperationStatus(test_video, out_path, line, fx,fy,con_line, targets, obj_per_time, time_th, bounds)
        
            
    else:
        print(f"❌ Test video not found: {test_video}")


if __name__ == "__main__":
    main()
