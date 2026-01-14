# Cleanup Script - Run this to archive debug files and remove log files
# Run from be/ directory

# Create archive folder
New-Item -ItemType Directory -Force -Path "scripts\archive"

# Move debug scripts (batch 1 - already done)
# Move-Item -Path auto_tune.py,check_crc.py,... -Destination scripts\archive\ -Force

# Move remaining debug scripts (batch 2)
$batch2 = @(
    "dll_reader_test.py",
    "documented_tag_read.py", 
    "find_rfid_protocol_port.py",
    "find_rfid_reader.py",
    "gate_workparam.py",
    "get_all_params.py",
    "gpio_config.py",
    "inspect_gate_param.py",
    "passive_listener.py",
    "proper_inventory.py",
    "quick_reader_find.py",
    "raw_frame_dump.py",
    "rfid_discovery.py",
    "rfid_full_test.py",
    "scan_m200_ports.py",
    "sdk_init.py",
    "set_all_params.py",
    "set_gate_param.py",
    "set_query_param.py",
    "simple_rfid_test.py",
    "simulate_scan.py",
    "sniffer_proxy.py",
    "test_all_commands.py",
    "test_direct_create.py",
    "test_m200.py",
    "test_ws_connection.py",
    "tune_reader.py",
    "verify_scanner_and_tags.py",
    "working_detection.py"
)

foreach ($file in $batch2) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination scripts\archive\ -Force
        Write-Host "Moved: $file"
    }
}

# Delete log/output files
$logs = @(
    "command_test_results.txt",
    "rfid_debug_log.txt",
    "rfid_full_log.txt",
    "rfid_log.txt",
    "server_output.txt"
)

foreach ($log in $logs) {
    if (Test-Path $log) {
        Remove-Item -Path $log -Force
        Write-Host "Deleted: $log"
    }
}

Write-Host ""
Write-Host "Cleanup complete!"
Write-Host "Archived scripts: scripts\archive\"
