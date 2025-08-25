#!/usr/bin/python3
"""
Enhanced Solar Tracer Data Logger
Logs comprehensive solar charge controller data to InfluxDB
Supports all Modbus registers from LS-B Series Protocol V1.1
"""

import sys
import time
import json
import argparse
from datetime import datetime
from influxdb import InfluxDBClient
from SolarTracer import SolarTracer
from InfluxConf import *

class SolarDataLogger:
    """Enhanced solar data logger with comprehensive Modbus support"""
    
    def __init__(self, tracer_port=TRACER_PORT, tracer_id=TRACER_ID, debug=0):
        """Initialize the logger with tracer connection"""
        self.debug = debug
        self.tracer = None
        self.ifclient = None
        
        # Initialize tracer connection
        try:
            self.tracer = SolarTracer(tracer_port, tracer_id, debug)
            if self.debug > 0:
                print(f"DEBUG: Connected to tracer: {self.tracer}")
        except Exception as e:
            print(f"ERROR: Failed to initialize tracer: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Initialize InfluxDB connection
        try:
            self.ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)
            # Test connection
            self.ifclient.ping()
            if self.debug > 0:
                print(f"DEBUG: Connected to InfluxDB: {ifhost}:{ifport}")
        except Exception as e:
            print(f"ERROR: Failed to connect to InfluxDB: {e}", file=sys.stderr)
            sys.exit(1)
    
    def create_measurement_point(self, measurement_name, fields, tags=None, timestamp=None):
        """Create a properly formatted InfluxDB measurement point"""
        if timestamp is None:
            timestamp = self.tracer.getTimestamp()
        
        point = {
            "measurement": measurement_name,
            "time": timestamp,
            "fields": fields
        }
        
        if tags:
            point["tags"] = tags
            
        return point
    
    def flatten_nested_dict(self, data, prefix="", separator="_"):
        """Flatten nested dictionaries for InfluxDB storage"""
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self.flatten_nested_dict(value, new_key, separator))
            elif isinstance(value, (int, float, bool)):
                flattened[new_key] = value
            elif isinstance(value, str):
                # Convert string values to tags or numeric if possible
                try:
                    flattened[new_key] = float(value)
                except ValueError:
                    # Store as tag instead of field for string values
                    pass
            else:
                # Skip unsupported data types
                if self.debug > 1:
                    print(f"DEBUG: Skipping unsupported data type for {new_key}: {type(value)}")
        
        return flattened
    
    def log_realtime_data(self, measurement_name="solar_realtime"):
        """Log real-time solar data"""
        try:
            current_data = self.tracer.readCurrent()
            if not current_data:
                if current_data is None:
                    print("ERROR: Failed to read current data", file=sys.stderr)
                else:
                    print("WARNING: No real-time data received", file=sys.stderr)
                return False
            
            # Flatten nested status data
            flattened_data = self.flatten_nested_dict(current_data)
            
            # Create measurement point
            point = self.create_measurement_point(measurement_name, flattened_data)
            
            if self.debug > 0:
                print(f"DEBUG: Real-time data point: {json.dumps(point, indent=2, default=str)}")
            
            # Write to InfluxDB
            self.ifclient.write_points([point])
            
            if self.debug > 0:
                print(f"SUCCESS: Logged {len(flattened_data)} real-time fields to {measurement_name}")
                
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to log real-time data: {e}", file=sys.stderr)
            return False
    
    def log_statistics(self, measurement_name="solar_statistics"):
        """Log statistical data"""
        try:
            stats_data = self.tracer.readStats()
            if not stats_data:
                if stats_data is None:
                    print("ERROR: Failed to read statistics data", file=sys.stderr)
                else:
                    print("WARNING: No statistics data received", file=sys.stderr)
                return False
            
            # Create measurement point
            point = self.create_measurement_point(measurement_name, stats_data)
            
            if self.debug > 0:
                print(f"DEBUG: Statistics data point: {json.dumps(point, indent=2, default=str)}")
            
            # Write to InfluxDB
            self.ifclient.write_points([point])
            
            if self.debug > 0:
                print(f"SUCCESS: Logged {len(stats_data)} statistics fields to {measurement_name}")
                
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to log statistics: {e}", file=sys.stderr)
            return False
    
    def log_rated_data(self, measurement_name="solar_rated"):
        """Log rated specification data (usually static, log less frequently)"""
        try:
            rated_data = self.tracer.readRatedData()
            if not rated_data:
                if rated_data is None:
                    print("ERROR: Failed to read rated data", file=sys.stderr)
                else:
                    print("WARNING: No rated data received", file=sys.stderr)
                return False
            
            # Create measurement point
            point = self.create_measurement_point(measurement_name, rated_data)
            
            if self.debug > 0:
                print(f"DEBUG: Rated data point: {json.dumps(point, indent=2, default=str)}")
            
            # Write to InfluxDB
            self.ifclient.write_points([point])
            
            if self.debug > 0:
                print(f"SUCCESS: Logged {len(rated_data)} rated fields to {measurement_name}")
                
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to log rated data: {e}", file=sys.stderr)
            return False
    
    def log_settings(self, measurement_name="solar_settings"):
        """Log system settings (usually static, log infrequently)"""
        try:
            settings_data = self.tracer.readAllSettings()
            if not settings_data:
                if settings_data is None:
                    print("ERROR: Failed to read settings data", file=sys.stderr)
                else:
                    print("WARNING: No settings data received", file=sys.stderr)
                return False
            
            # Create measurement point
            point = self.create_measurement_point(measurement_name, settings_data)
            
            if self.debug > 0:
                print(f"DEBUG: Settings data point: {json.dumps(point, indent=2, default=str)}")
            
            # Write to InfluxDB
            self.ifclient.write_points([point])
            
            if self.debug > 0:
                print(f"SUCCESS: Logged {len(settings_data)} settings fields to {measurement_name}")
                
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to log settings: {e}", file=sys.stderr)
            return False
    
    def log_system_status(self, measurement_name="solar_system_status"):
        """Log system status (coils and discrete inputs)"""
        try:
            status_data = self.tracer.readSystemStatus()
            if not status_data:
                print("WARNING: No system status data received", file=sys.stderr)
                return False
            
            # Convert boolean values to integers for InfluxDB
            numeric_status = {}
            for key, value in status_data.items():
                if isinstance(value, bool):
                    numeric_status[key] = 1 if value else 0
                elif isinstance(value, str):
                    # Convert string status to numeric (Day=0, Night=1)
                    if value == 'Night':
                        numeric_status[key] = 1
                    elif value == 'Day':
                        numeric_status[key] = 0
                    else:
                        numeric_status[key] = hash(value) % 1000  # Simple hash for other strings
                else:
                    numeric_status[key] = value
            
            # Create measurement point
            point = self.create_measurement_point(measurement_name, numeric_status)
            
            if self.debug > 0:
                print(f"DEBUG: System status data point: {json.dumps(point, indent=2, default=str)}")
            
            # Write to InfluxDB
            self.ifclient.write_points([point])
            
            if self.debug > 0:
                print(f"SUCCESS: Logged {len(numeric_status)} system status fields to {measurement_name}")
                
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to log system status: {e}", file=sys.stderr)
            return False
    
    def log_all_data(self):
        """Log all available data types"""
        success_count = 0
        total_attempts = 5
        
        # Log real-time data (most important)
        if self.log_realtime_data():
            success_count += 1
            
        # Log statistics
        if self.log_statistics():
            success_count += 1
            
        # Log system status
        if self.log_system_status():
            success_count += 1
            
        # Log rated data (less frequently needed)
        if self.log_rated_data():
            success_count += 1
            
        # Log settings (least frequently needed)
        if self.log_settings():
            success_count += 1
        
        if self.debug > 0:
            print(f"SUCCESS: Logged {success_count}/{total_attempts} data categories")
            
        return success_count > 0
    
    def run_single_log(self, data_type="realtime"):
        """Run a single logging operation"""
        if data_type == "realtime":
            return self.log_realtime_data()
        elif data_type == "statistics":
            return self.log_statistics()
        elif data_type == "rated":
            return self.log_rated_data()
        elif data_type == "settings":
            return self.log_settings()
        elif data_type == "status":
            return self.log_system_status()
        elif data_type == "all":
            return self.log_all_data()
        else:
            print(f"ERROR: Unknown data type: {data_type}", file=sys.stderr)
            return False
    
    def run_continuous_log(self, interval=60, data_types=None):
        """Run continuous logging at specified interval"""
        if data_types is None:
            data_types = ["realtime", "statistics"]  # Default to most important data
        
        print(f"Starting continuous logging every {interval} seconds")
        print(f"Logging data types: {data_types}")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] Logging cycle started")
                
                success_count = 0
                for data_type in data_types:
                    if self.run_single_log(data_type):
                        success_count += 1
                
                print(f"[{timestamp}] Logging cycle completed: {success_count}/{len(data_types)} successful")
                
                # Sleep for the specified interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nLogging stopped by user")
        except Exception as e:
            print(f"ERROR: Continuous logging failed: {e}", file=sys.stderr)
    
    def print_current_data(self):
        """Print current data to console for debugging"""
        print("\n=== CURRENT SOLAR DATA ===")
        
        try:
            # Real-time data
            print("\n--- Real-time Data ---")
            current = self.tracer.readCurrent()
            if current:
                for key, value in current.items():
                    if isinstance(value, dict):
                        print(f"{key}:")
                        for subkey, subvalue in value.items():
                            print(f"  {subkey}: {subvalue}")
                    else:
                        print(f"{key}: {value}")
            else:
                print("Failed to read real-time data")
            
            # Statistics
            print("\n--- Statistics ---")
            stats = self.tracer.readStats()
            if stats:
                for key, value in stats.items():
                    print(f"{key}: {value}")
            else:
                print("Failed to read statistics")
            
            # System status
            print("\n--- System Status ---")
            status = self.tracer.readSystemStatus()
            if status:
                for key, value in status.items():
                    print(f"{key}: {value}")
            else:
                print("Failed to read system status")
                
        except Exception as e:
            print(f"ERROR: Failed to read data: {e}", file=sys.stderr)


def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Solar Tracer Data Logger')
    parser.add_argument('--debug', '-d', type=int, default=0, choices=[0, 1, 2], 
                       help='Debug level (0=none, 1=normal, 2=verbose)')
    parser.add_argument('--mode', '-m', choices=['single', 'continuous', 'print'], 
                       default='single', help='Logging mode')
    parser.add_argument('--data-type', '-t', choices=['realtime', 'statistics', 'rated', 'settings', 'status', 'all'],
                       default='realtime', help='Data type to log (single mode only)')
    parser.add_argument('--interval', '-i', type=int, default=60,
                       help='Logging interval in seconds (continuous mode only)')
    parser.add_argument('--port', '-p', default=TRACER_PORT,
                       help='Serial port for tracer communication')
    parser.add_argument('--id', type=int, default=TRACER_ID,
                       help='Modbus device ID')
    
    args = parser.parse_args()
    
    # Initialize logger
    try:
        logger = SolarDataLogger(args.port, args.id, args.debug)
    except Exception as e:
        print(f"FATAL: Failed to initialize logger: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run based on mode
    if args.mode == 'single':
        print(f"Running single log operation: {args.data_type}")
        success = logger.run_single_log(args.data_type)
        sys.exit(0 if success else 1)
        
    elif args.mode == 'continuous':
        data_types = ['realtime', 'statistics', 'status']  # Default continuous types
        logger.run_continuous_log(args.interval, data_types)
        
    elif args.mode == 'print':
        logger.print_current_data()
    
    else:
        print("ERROR: Invalid mode specified", file=sys.stderr)
        sys.exit(1)


# Legacy compatibility - maintain original simple interface
def simple_log():
    """Simple logging function for backward compatibility"""
    try:
        tracer = SolarTracer(TRACER_PORT, TRACER_ID, debug=0)
        measurement_name = "solar"
        
        # Get real-time data using original method
        current_data = tracer.readCurrent()
        if not current_data:
            if current_data is None:
                print("ERROR: Failed to read current data from tracer", file=sys.stderr)
            else:
                print("WARNING: No current data received from tracer", file=sys.stderr)
            return False
        
        # Create InfluxDB point in original format
        body_solar = [
            {
                "measurement": measurement_name,
                "time": tracer.getTimestamp(),
                "fields": current_data
            }
        ]
        
        print(body_solar)
        
        # Connect to InfluxDB and write
        ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)
        ifclient.write_points(body_solar)
        
        return True
        
    except IOError:
        print("Could not obtain measurements from tracer", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Check if running with arguments (new enhanced mode) or without (legacy mode)
    if len(sys.argv) > 1:
        main()
    else:
        # Legacy mode for backward compatibility
        print("Running in legacy compatibility mode")
        print("Use --help to see enhanced logging options")
        simple_log()