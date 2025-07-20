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

from simplified_chatgpt_data import analyze_production_data
from YoloLineTest import OperationStatus, functioning

def main():
    """Main pipeline for Factory Supervision."""
    
    print("🏭 FactorySupervision - Production Line Analysis")
    print("=" * 50)
    
    # Test video path
    test_video = "Dataset/Video/test_vid_2.mp4"
    
    if os.path.exists(test_video):
        print(f"📹 Analyzing video: {test_video}")
        
        # Step 1: Video Analysis with production parameters
        # Parameters for OperationStatus:
        # video_path, out_path, line, factor, cross_threshold, targets, obj_per_time, time_th, bounds
        
        out_path = "logs/production_status.log"
        os.makedirs("logs", exist_ok=True)
        
        line = False  # True for horizontal line, False for vertical line
        factor = 0.35  # Line position factor (35% of width/height)
        cross_threshold = 4  # Time threshold for stopped detection
        targets = [0, 1, 2, 3, 4, 5, 6]  # Target classes: Box, Fruit, bag, bottle, jar, mask, pallet
        obj_per_time = 3  # Expected objects per time period
        time_th = 10  # Time threshold for production check (seconds)
        bounds = 1  # Margin of error for object count
        
        print(f"🔧 Production Parameters:")
        print(f"  • Line: {'Horizontal' if line else 'Vertical'} at {factor*100}%")
        print(f"  • Expected: {obj_per_time}±{bounds} objects per {time_th}s")
        print(f"  • Stop threshold: {cross_threshold}s")
        
        # Run analysis
        OperationStatus(test_video, out_path, line, factor, cross_threshold, targets, obj_per_time, time_th, bounds)
        
        # Check global functioning status
        from YoloLineTest import functioning
        status = "Running" if functioning else "Issues Detected"
        print(f"✅ Production Status: {status}")
        print(f"🔍 Global functioning state: {functioning}")
        
        # Step 2: AI Analysis of logs
        print("\n🤖 Starting AI analysis of production data...")
        
        # Read recent logs
        log_file = "logs/production_status.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                recent_logs = f.read()
            
            if recent_logs.strip():
                # Analyze with ChatGPT
                analysis = analyze_production_data(recent_logs)
                print(f"\n📊 AI Analysis Results:")
                print("-" * 40)
                print(analysis)
                
                # Save analysis
                analysis_file = f"Results/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                os.makedirs("Results", exist_ok=True)
                with open(analysis_file, 'w') as f:
                    f.write(f"Production Analysis - {datetime.now()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(analysis)
                
                print(f"\n💾 Analysis saved to: {analysis_file}")
            else:
                print("⚠️  No log data found for analysis")
        else:
            print(f"⚠️  Log file not found: {log_file}")
    else:
        print(f"❌ Test video not found: {test_video}")
        print("Available commands:")
        print("• python main.py")
        print("• python YoloLineTest.py [video_path]") 
        print("• python simplified_chatgpt_data.py")

def analyze_production_video(video_path):
    """
    Analyze a specific video file using the new OperationStatus function.
    """
    print(f"🎥 Analyzing video: {video_path}")
    
    try:
        # Production parameters
        out_path = "logs/production_status.log"
        os.makedirs("logs", exist_ok=True)
        
        line = False  # Vertical line detection
        factor = 0.35  # Line at 35% of frame width
        cross_threshold = 4  # Stop threshold in seconds
        targets = [0, 1, 2, 3, 4, 5, 6]  # All target classes
        obj_per_time = 3  # Expected objects per period
        time_th = 10  # Time period in seconds
        bounds = 1  # Tolerance
        
        # Run analysis
        OperationStatus(video_path, out_path, line, factor, cross_threshold, targets, obj_per_time, time_th, bounds)
        
        # Check functioning status
        from YoloLineTest import functioning
        status = "Running" if functioning else "Issues Detected"
        print(f"✅ Video analysis complete. Status: {status}")
        return status
    except Exception as e:
        print(f"❌ Error during video analysis: {e}")
        return None

if __name__ == "__main__":
    main()
