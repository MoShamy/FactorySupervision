#!/usr/bin/env python3
"""
FactorySupervision - AI-Powered Production Line Monitoring

This is the main entry point for the Factory Supervision system.
It provides video analysis, production logging, and AI-powered insights.
"""

import sys
import os
from datetime import datetime

# Add project directories to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'computer_vision'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

from computer_vision.conveyor_vision_system import OperationStatus


def main():
    """Main pipeline for Factory Supervision."""
    
    
    # Test video path
    test_video = "Dataset/Video/test_vid_2.mp4"
    
    if os.path.exists(test_video):
        print(f"📹 Analyzing video: {test_video}")
        
        out_path = "logs/production_status.log"
        os.makedirs("logs", exist_ok=True)
        
        line = False  # True for horizontal line, False for vertical line
        factor = 0.5  # Line position factor (35% of width/height)
        cross_threshold = 4  # Time threshold for stopped detection
        targets = [2]  # Target classes: Box, Fruit, bag, bottle, jar, mask, pallet
        obj_per_time = 3  # Expected objects per time period
        time_th = 40  # Time threshold for production check (seconds)
        bounds = 1  # Margin of error for object count
        
        # Run analysis
        OperationStatus(test_video, out_path, line, factor, cross_threshold, targets, obj_per_time, time_th, bounds)
        
            
    else:
        print(f"❌ Test video not found: {test_video}")


if __name__ == "__main__":
    main()
