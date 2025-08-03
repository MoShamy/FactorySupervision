"""
==============================================================================
SYSTEM STATUS MODULE - ENHANCED WITH LOG INTEGRATION
==============================================================================
File: system_status.py
Author: Factory Supervision Team
Date: July 27, 2025
Version: 2.0.0

Description:
    Enhanced system status management that integrates with production logs.
    Provides persistent status tracking, log parsing, and real-time updates.

Features:
    - Log file integration
    - Persistent status across restarts
    - Real-time status updates
    - Historical status tracking
==============================================================================
"""

import os
import time
from datetime import datetime
import json
from typing import Dict, List, Optional

# Global status variables (for backward compatibility)
functioning = True
previous_functioning = True

class SystemStatusManager:
    """Enhanced system status manager with log integration"""
    
    def __init__(self, log_file_path="../logs/production_status.log", status_file_path="status_cache.json"):
        self.log_file_path = log_file_path
        self.status_file_path = status_file_path
        self.functioning = True
        self.previous_functioning = True
        self.last_status_change = None
        self.status_history = []
        
        # Load status from cache and logs
        self._load_status_from_cache()
        self._update_from_logs()
    
    def _load_status_from_cache(self):
        """Load status from cached JSON file"""
        try:
            if os.path.exists(self.status_file_path):
                with open(self.status_file_path, 'r') as f:
                    data = json.load(f)
                    self.functioning = data.get('functioning', True)
                    self.last_status_change = data.get('last_change')
                    self.status_history = data.get('history', [])
                    print(f"📂 Loaded cached status: {self.functioning}")
        except Exception as e:
            print(f"⚠️ Could not load status cache: {e}")
    
    def _save_status_to_cache(self):
        """Save current status to cache file"""
        try:
            data = {
                'functioning': self.functioning,
                'last_change': self.last_status_change,
                'history': self.status_history[-10:],  # Keep last 10 entries
                'timestamp': datetime.now().isoformat()
            }
            with open(self.status_file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save status cache: {e}")
    
    def _update_from_logs(self):
        """Parse log file to get the latest status"""
        try:
            if not os.path.exists(self.log_file_path):
                print(f"📝 Log file not found: {self.log_file_path}")
                return
            
            with open(self.log_file_path, 'r') as f:
                lines = f.readlines()
            
            # Parse the last few log entries to determine current status
            recent_entries = lines[-5:] if len(lines) > 5 else lines
            
            for line in reversed(recent_entries):
                line = line.strip()
                if not line:
                    continue
                
                # Parse different status types
                if "Returned to normal operation" in line:
                    self._update_status(True, "Normal operation restored")
                    break
                elif "Stopped" in line:
                    self._update_status(False, "System stopped")
                    break
                elif "Too Fast" in line:
                    self._update_status(False, "Running too fast")
                    break
                elif "Too Slow" in line:
                    self._update_status(False, "Running too slow")
                    break
            
            print(f"📊 Status updated from logs: {self.functioning}")
            
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    
    def _update_status(self, new_status: bool, reason: str = ""):
        """Update system status with reason tracking"""
        if new_status != self.functioning:
            self.previous_functioning = self.functioning
            self.functioning = new_status
            self.last_status_change = datetime.now().isoformat()
            
            # Add to history
            self.status_history.append({
                'status': new_status,
                'reason': reason,
                'timestamp': self.last_status_change
            })
            
            # Update global variables for backward compatibility
            global functioning, previous_functioning
            functioning = new_status
            previous_functioning = self.previous_functioning
            
            # Save to cache
            self._save_status_to_cache()
            
            print(f"🔄 Status changed: {self.previous_functioning} → {new_status} ({reason})")
    
    def get_status(self) -> Dict:
        """Get comprehensive status information"""
        return {
            'functioning': self.functioning,
            'previous_functioning': self.previous_functioning,
            'last_change': self.last_status_change,
            'status_text': "Running" if self.functioning else "Stopped",
            'uptime': self._calculate_uptime(),
            'recent_history': self.status_history[-3:] if self.status_history else []
        }
    
    def _calculate_uptime(self) -> Optional[str]:
        """Calculate system uptime since last normal operation"""
        if not self.functioning or not self.status_history:
            return None
        
        # Find the last time it returned to normal
        for entry in reversed(self.status_history):
            if entry['status'] and 'normal' in entry.get('reason', '').lower():
                start_time = datetime.fromisoformat(entry['timestamp'])
                uptime_seconds = (datetime.now() - start_time).total_seconds()
                hours, remainder = divmod(uptime_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return f"{int(hours)}h {int(minutes)}m"
        
        return None
    
    def set_status(self, new_status: bool, reason: str = "Manual update"):
        """Manually set system status"""
        self._update_status(new_status, reason)
    
    def refresh_from_logs(self):
        """Force refresh status from log files"""
        self._update_from_logs()

# Initialize the enhanced status manager
_status_manager = SystemStatusManager()

# Convenience functions for backward compatibility
def get_status():
    """Get current system status"""
    return _status_manager.get_status()

def set_status(new_status: bool, reason: str = ""):
    """Set system status"""
    _status_manager.set_status(new_status, reason)

def refresh_status():
    """Refresh status from logs"""
    _status_manager.refresh_from_logs()

# Update global variables from manager
functioning = _status_manager.functioning
previous_functioning = _status_manager.previous_functioning

print(f"🏭 System Status Manager initialized - Current status: {functioning}")