from influxdb import InfluxDBClient

# influx configuration - edit these
ifuser = "grafana"
ifpass = "solar"
ifdb   = "solar"
ifhost = "192.168.0.134"
ifport = 8086

# device configuration - USE cu.* FOR MODBUS ON macOS
SDM_PORT="/dev/cu.usbserial-FTB6SPL3"
TRACER_PORT="/dev/cu.usbserial-FTB6SPL3"
TRACER_ID=1

# UPower configuration - USE cu.* FOR MODBUS ON macOS
UPOWER_PORT = "/dev/cu.usbserial-FTB6SPL3"
UPOWER_ID = 10