# Enhanced SolarTracer.py with complete Modbus protocol support
# Based on LS-B Series Protocol ModBus Register Address List V1.1
# Full implementation of all available registers and functionality

import sys
import datetime
import time
import minimalmodbus

class SolarTracer:
    """Enhanced class representing a Tracer device with full Modbus protocol support"""

    # Rated data registers (read only) - 0x3000 series
    RATED_REGISTERS = {
        'PV_rated_voltage': 0x3000,
        'PV_rated_current': 0x3001, 
        'PV_rated_power_L': 0x3002,
        'PV_rated_power_H': 0x3003,
        'battery_rated_voltage': 0x3004,
        'rated_charging_current': 0x3005,
        'rated_charging_power_L': 0x3006,
        'rated_charging_power_H': 0x3007,
        'charging_mode': 0x3008,
        'rated_load_current': 0x300E
    }

    # Real-time data registers (read only) - 0x3100 series
    REALTIME_REGISTERS = {
        'PV_voltage': 0x3100,
        'PV_current': 0x3101,
        'PV_power_L': 0x3102,
        'PV_power_H': 0x3103,
        'battery_voltage': 0x3104,
        'battery_current': 0x3105,
        'battery_power_L': 0x3106,
        'battery_power_H': 0x3107,
        'load_voltage': 0x310C,
        'load_current': 0x310D,
        'load_power_L': 0x310E,
        'load_power_H': 0x310F,
        'battery_temperature': 0x3110,
        'case_temperature': 0x3111,
        'power_components_temperature': 0x3112,
        'battery_SOC': 0x311A,
        'remote_battery_temperature': 0x311B,
        'battery_real_rated_voltage': 0x311D
    }

    # Status registers (read only) - 0x3200 series  
    STATUS_REGISTERS = {
        'battery_status': 0x3200,
        'charging_equipment_status': 0x3201
    }

    # Statistical registers (read only) - 0x3300 series
    STATS_REGISTERS = {
        'max_PV_voltage_today': 0x3300,
        'min_PV_voltage_today': 0x3301,
        'max_battery_voltage_today': 0x3302,
        'min_battery_voltage_today': 0x3303,
        'consumed_energy_today_L': 0x3304,
        'consumed_energy_today_H': 0x3305,
        'consumed_energy_month_L': 0x3306,
        'consumed_energy_month_H': 0x3307,
        'consumed_energy_year_L': 0x3308,
        'consumed_energy_year_H': 0x3309,
        'total_consumed_energy_L': 0x330A,
        'total_consumed_energy_H': 0x330B,
        'generated_energy_today_L': 0x330C,
        'generated_energy_today_H': 0x330D,
        'generated_energy_month_L': 0x330E,
        'generated_energy_month_H': 0x330F,
        'generated_energy_year_L': 0x3310,
        'generated_energy_year_H': 0x3311,
        'total_generated_energy_L': 0x3312,
        'total_generated_energy_H': 0x3313,
        'CO2_reduction_L': 0x3314,
        'CO2_reduction_H': 0x3315,
        'net_battery_current_L': 0x331B,
        'net_battery_current_H': 0x331C,
        'battery_temp': 0x331D,
        'ambient_temp': 0x331E
    }

    # Setting registers (read-write) - 0x9000 series
    SETTING_REGISTERS = {
        'battery_type': 0x9000,
        'battery_capacity': 0x9001,
        'temp_compensation_coeff': 0x9002,
        'high_volt_disconnect': 0x9003,
        'charging_limit_voltage': 0x9004,
        'over_voltage_reconnect': 0x9005,
        'equalization_voltage': 0x9006,
        'boost_voltage': 0x9007,
        'float_voltage': 0x9008,
        'boost_reconnect_voltage': 0x9009,
        'low_voltage_reconnect': 0x900A,
        'under_voltage_recover': 0x900B,
        'under_voltage_warning': 0x900C,
        'low_voltage_disconnect': 0x900D,
        'discharging_limit_voltage': 0x900E,
        'real_time_clock_sec_min': 0x9013,
        'real_time_clock_hour_day': 0x9014,
        'real_time_clock_month_year': 0x9015,
        'equalization_charging_cycle': 0x9016,
        'battery_temp_warning_upper': 0x9017,
        'battery_temp_warning_lower': 0x9018,
        'controller_temp_upper_limit': 0x9019,
        'controller_temp_upper_recover': 0x901A,
        'power_component_temp_upper': 0x901B,
        'power_component_temp_recover': 0x901C,
        'line_impedance': 0x901D,
        'night_time_threshold_volt': 0x901E,
        'light_signal_startup_delay': 0x901F,
        'day_time_threshold_volt': 0x9020,
        'light_signal_turn_off_delay': 0x9021,
        'load_controlling_mode': 0x903D,
        'working_time_length_1': 0x903E,
        'working_time_length_2': 0x903F,
        'turn_on_timing_1_sec': 0x9042,
        'turn_on_timing_1_min': 0x9043,
        'turn_on_timing_1_hour': 0x9044,
        'turn_off_timing_1_sec': 0x9045,
        'turn_off_timing_1_min': 0x9046,
        'turn_off_timing_1_hour': 0x9047,
        'turn_on_timing_2_sec': 0x9048,
        'turn_on_timing_2_min': 0x9049,
        'turn_on_timing_2_hour': 0x904A,
        'turn_off_timing_2_sec': 0x904B,
        'turn_off_timing_2_min': 0x904C,
        'turn_off_timing_2_hour': 0x904D,
        'length_of_night': 0x9065,
        'battery_rated_voltage_code': 0x9067,
        'load_timing_control_selection': 0x9069,
        'default_load_on_off_manual': 0x906A,
        'equalize_duration': 0x906B,
        'boost_duration': 0x906C,
        'discharging_percentage': 0x906D,
        'charging_percentage': 0x906E,
        'battery_management_mode': 0x9070
    }

    # Coils (read-write) - 0x0002, 0x0005, 0x0006
    COIL_REGISTERS = {
        'manual_control_load': 0x0002,
        'enable_load_test_mode': 0x0005,
        'force_load_on_off': 0x0006
    }

    # Discrete inputs (read-only) - 0x2000, 0x200C
    DISCRETE_INPUTS = {
        'over_temperature_inside': 0x2000,
        'day_night': 0x200C
    }

    # Constants for battery types and status decoding
    BATTERY_TYPES = {0: "USER", 1: "SEALED", 2: "GEL", 3: "FLOODED"}
    CHARGING_MODES = {1: "PWM"}
    CHARGING_STATUS = {0: "No charging", 1: "Float", 2: "Boost", 3: "Equalization"}

    # Predefined battery settings
    BATTERY_LEAD_ACID = [0, 300, 300, 1620, 1500, 1500, 1460, 1440, 1380, 1630, 1260, 1220, 1200, 1110, 1060]
    BATTERY_LIFEPO4 = [0, 300, 300, 1500, 1460, 1420, 1400, 1380, 1380, 1320, 1240, 1200, 1160, 1080, 1040]

    def __init__(self, device='/dev/tty.usbserial-FTB6SPL3', serialid=1, debug=0):
        """Initialize the SolarTracer with enhanced Modbus support"""
        self.device = device
        self.id = serialid
        self.debug = debug
        self.connected = False

        try:
            instrument = minimalmodbus.Instrument(self.device, self.id)
            if self.debug > 0:
                print("DEBUG: successfully connected to", self.device)
            
            # Set instrument Serial settings per protocol specification
            instrument.serial.baudrate = 115200
            instrument.serial.bytesize = 8
            instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 2
            instrument.mode = minimalmodbus.MODE_RTU
            instrument.debug = False

            self.instrument = instrument
            self.connected = True

        except IOError:
            self.connected = False
            print("ERROR: Failed to connect to", self.device, file=sys.stderr)
            sys.exit(1)

    def __del__(self):
        """Destruct the SolarTracer object"""
        if self.connected:
            self.instrument.serial.close()
            if self.debug > 0: 
                print("DEBUG: successfully disconnected", self.device)

    def __str__(self) -> str:
        """String representation of the controller"""
        stat = "disconnected"
        if self.connected: 
            stat = "connected"
        return f"{self.device}({self.id}): {stat}"
    
    def getTimestamp(self):
        """Get current timestamp from the system"""
        localtime = time.localtime()
        localstamp = time.strftime("%H:%M:%S", localtime)
        timestamp = datetime.datetime.utcnow()
        if self.debug > 0: 
            print("DEBUG: Local time", localstamp, ", UTC timestamp", timestamp)
        return timestamp
    
    def readReg(self, register, decimals=2, function_code=4) -> float:
        """Read a register from the Tracer with proper scaling"""
        try:
            value = self.instrument.read_register(register, decimals, function_code)
            if self.debug > 0: 
                print("DEBUG: Successfully read from 0x%X: %f" % (register, value))
            return value
        except IOError:
            print("ERROR: Failed to read from 0x%X" % register, file=sys.stderr)
            return -1

    def readCoil(self, address) -> bool:
        """Read a coil (discrete output)"""
        try:
            value = self.instrument.read_bit(address)
            if self.debug > 0:
                print("DEBUG: Successfully read coil 0x%X: %s" % (address, value))
            return value
        except IOError:
            print("ERROR: Failed to read coil 0x%X" % address, file=sys.stderr)
            return False

    def writeCoil(self, address, value) -> bool:
        """Write to a coil (discrete output)"""
        try:
            self.instrument.write_bit(address, value)
            if self.debug > 0:
                print("DEBUG: Successfully wrote coil 0x%X: %s" % (address, value))
            return True
        except IOError:
            print("ERROR: Failed to write coil 0x%X" % address, file=sys.stderr)
            return False

    def readDiscreteInput(self, address) -> bool:
        """Read a discrete input"""
        try:
            value = self.instrument.read_bit(address, 2)  # Function code 2 for discrete inputs
            if self.debug > 0:
                print("DEBUG: Successfully read discrete input 0x%X: %s" % (address, value))
            return value
        except IOError:
            print("ERROR: Failed to read discrete input 0x%X" % address, file=sys.stderr)
            return False

    def combine32BitValue(self, low_reg, high_reg) -> float:
        """Combine low and high 16-bit registers into 32-bit value"""
        return (high_reg * 65536 + low_reg) / 100.0

    def decodeBatteryStatus(self, status_value) -> dict:
        """Decode battery status register (0x3200)"""
        return {
            'voltage_status': ['Normal', 'Overvolt', 'Under Volt', 'Low Volt Disconnect', 'Fault'][status_value & 0x0F],
            'temperature_status': ['Normal', 'Over Temp', 'Low Temp'][((status_value >> 4) & 0x0F) % 3],
            'internal_resistance_abnormal': bool(status_value & 0x0100),
            'wrong_voltage_identification': bool(status_value & 0x8000)
        }

    def decodeChargingStatus(self, status_value) -> dict:
        """Decode charging equipment status register (0x3201)"""
        return {
            'input_voltage_status': ['Normal', 'No power', 'Higher volt input', 'Input volt error'][(status_value >> 14) & 0x03],
            'charging_mosfet_short': bool(status_value & 0x2000),
            'charging_anti_reverse_short': bool(status_value & 0x1000),
            'anti_reverse_short': bool(status_value & 0x0800),
            'input_over_current': bool(status_value & 0x0400),
            'load_over_current': bool(status_value & 0x0200),
            'load_short': bool(status_value & 0x0100),
            'load_mosfet_short': bool(status_value & 0x0080),
            'pv_input_short': bool(status_value & 0x0010),
            'charging_status': ['No charging', 'Float', 'Boost', 'Equalization'][(status_value >> 2) & 0x03],
            'fault': bool(status_value & 0x0002),
            'running': bool(status_value & 0x0001)
        }

    def readRatedData(self) -> dict:
        """Read all rated data registers"""
        rated_data = {}
        try:
            # Read block from 0x3000 - only 5 registers that are available
            regs = self.instrument.read_registers(0x3000, 5, 4)
            
            rated_data = {
                'pv_rated_voltage': regs[0] / 100.0,
                'pv_rated_current': regs[1] / 100.0,
                'pv_rated_power': self.combine32BitValue(regs[2], regs[3]),
                'battery_rated_voltage': regs[4] / 100.0
            }
        except IOError as e:
            print(f"ERROR: Failed to read rated data registers: {e}", file=sys.stderr)
            return None  # Return None to indicate failure
        except Exception as e:
            print(f"ERROR: Unexpected error reading rated data: {e}", file=sys.stderr)
            return None  # Return None to indicate failure
            
        return rated_data

    def readCurrent(self) -> dict:
        """Read all real-time data with enhanced register coverage"""
        tracer_current = {}
        
        try:
            # Read main real-time data block - only 20 registers from 0x3100 that are available
            regs = self.instrument.read_registers(0x3100, 20, 4)
            
            tracer_current = {
                'PVvolt': regs[0] / 100.0,
                'PVamps': regs[1] / 100.0,
                'PVwatt': self.combine32BitValue(regs[2], regs[3]),
                'BAvolt': regs[4] / 100.0,
                'BAamps': regs[5] / 100.0,
                'BAwatt': self.combine32BitValue(regs[6], regs[7]),
                'DCvolt': regs[12] / 100.0,
                'DCamps': regs[13] / 100.0,
                'DCwatt': self.combine32BitValue(regs[14], regs[15]),
                'BAtemp': regs[16] / 100.0,
                'CTtemp': regs[17] / 100.0,
                'power_components_temp': regs[18] / 100.0,
                'BAperc': regs[19] / 100.0  # Note: moved from regs[26] to regs[19]
            }

            # Note: Status registers (0x3200 series) are not available on this device
            # so we skip reading them to avoid errors

        except IOError as e:
            print(f"ERROR: Failed to read current data: {e}", file=sys.stderr)
            return None  # Return None to indicate failure
        except Exception as e:
            print(f"ERROR: Unexpected error reading current data: {e}", file=sys.stderr)
            return None  # Return None to indicate failure
            
        return tracer_current

    def readStats(self) -> dict:
        """Read all statistical parameters with enhanced coverage"""
        tracer_stats = {}
        
        try:
            # Read statistics block - only 20 registers from 0x3300 that are available
            regs = self.instrument.read_registers(0x3300, 20, 4)
            
            tracer_stats = {
                'max_pv_voltage_today': regs[0] / 100.0,
                'min_pv_voltage_today': regs[1] / 100.0,
                'max_battery_voltage_today': regs[2] / 100.0,
                'min_battery_voltage_today': regs[3] / 100.0,
                'consumed_energy_today': self.combine32BitValue(regs[4], regs[5]),
                'consumed_energy_month': self.combine32BitValue(regs[6], regs[7]),
                'consumed_energy_year': self.combine32BitValue(regs[8], regs[9]),
                'total_consumed_energy': self.combine32BitValue(regs[10], regs[11]),
                'generated_energy_today': self.combine32BitValue(regs[12], regs[13]),
                'generated_energy_month': self.combine32BitValue(regs[14], regs[15]),
                'generated_energy_year': self.combine32BitValue(regs[16], regs[17]),
                'total_generated_energy': self.combine32BitValue(regs[18], regs[19])
            }
            
        except IOError as e:
            print(f"ERROR: Failed to read statistics: {e}", file=sys.stderr)
            return None  # Return None to indicate failure
        except Exception as e:
            print(f"ERROR: Unexpected error reading statistics: {e}", file=sys.stderr)
            return None  # Return None to indicate failure
            
        return tracer_stats

    def readAllSettings(self) -> dict:
        """Read all setting parameters"""
        # Note: This device does not support reading from holding registers (0x9000 series)
        # so we return an empty dict to indicate no settings are available
        print("INFO: Settings reading not supported on this device (no holding register access)", file=sys.stderr)
        return {}

    def readSystemStatus(self) -> dict:
        """Read system status including coils and discrete inputs"""
        # Note: This device does not support reading coils (0x0000 series) or discrete inputs (0x2000 series)
        # so we return an empty dict to indicate no status information is available
        print("INFO: System status reading not supported on this device (no coil/discrete input access)", file=sys.stderr)
        return {}

    def setBatterySettings(self, settings_list, battery_capacity=100, battery_voltage=12) -> int:
        """Enhanced battery settings with voltage scaling"""
        new_settings = settings_list.copy()
        
        if battery_capacity != 100:
            new_settings[1] = battery_capacity
            
        if battery_voltage > 12:
            volt_adjust = battery_voltage / 12
            for idx in range(3, len(new_settings)):  # Skip first 3 settings
                new_settings[idx] = int(new_settings[idx] * volt_adjust)
        
        try:
            if self.debug > 0: 
                print("DEBUG: Writing new settings to %s(%d)" % (self.device, self.id))
            self.instrument.write_registers(0x9000, new_settings)
            return 0
        except IOError:
            print("ERROR: Failed to write settings to %s" % self.device, file=sys.stderr)
            return -2

    def setLoadControl(self, manual_on=False, test_mode=False, force_on=False) -> bool:
        """Control load outputs via coils"""
        success = True
        success &= self.writeCoil(0x0002, manual_on)
        success &= self.writeCoil(0x0005, test_mode)
        success &= self.writeCoil(0x0006, force_on)
        return success

    def printBatterySettings(self):
        """Print battery settings in a formatted way"""
        settings = self.readAllSettings()
        print("\n=== Battery Settings ===")
        for key, value in settings.items():
            if isinstance(value, float):
                print(f"{key:<30}: {value:.2f}")
            else:
                print(f"{key:<30}: {value}")

    def printFullStatus(self):
        """Print comprehensive system status"""
        print("\n=== Solar Tracer Full Status ===")
        
        print("\n--- Rated Data ---")
        rated = self.readRatedData()
        if rated:
            for key, value in rated.items():
                print(f"{key:<25}: {value}")
        else:
            print("Failed to read rated data.")
            
        print("\n--- Real-time Data ---")
        current = self.readCurrent()
        if current:
            for key, value in current.items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for subkey, subvalue in value.items():
                        print(f"  {subkey:<20}: {subvalue}")
                else:
                    print(f"{key:<25}: {value}")
        else:
            print("Failed to read current data.")
                
        print("\n--- Statistics ---")
        stats = self.readStats()
        if stats:
            for key, value in stats.items():
                print(f"{key:<25}: {value}")
        else:
            print("Failed to read statistics.")
            
        print("\n--- System Status ---")
        status = self.readSystemStatus()
        if status:
            for key, value in status.items():
                print(f"{key:<25}: {value}")
        else:
            print("System status not available on this device.")