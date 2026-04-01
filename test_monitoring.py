#!/usr/bin/env python3
"""
Test script for monitoring dashboard
"""

import time
from monitoring_dashboard import MonitoringDashboard

def test_monitoring_dashboard():
    """Test the monitoring dashboard functionality"""
    print("Testing Monitoring Dashboard...")
    print("="*60)
    
    # Create dashboard instance
    dashboard = MonitoringDashboard(history_size=10)
    
    # Test 1: Collect system metrics
    print("\n1. Testing system metrics collection...")
    metrics = dashboard.collect_system_metrics()
    print(f"   CPU: {metrics.cpu_percent:.1f}%")
    print(f"   Memory: {metrics.memory_percent:.1f}%")
    print(f"   Disk: {metrics.disk_usage_percent:.1f}%")
    print(f"   Network: ↑{metrics.network_sent_mb:.1f}MB ↓{metrics.network_recv_mb:.1f}MB")
    print(f"   Processes: {metrics.processes_running}")
    print(f"   Uptime: {metrics.system_uptime_seconds/3600:.1f}h")
    
    # Test 2: Check service health
    print("\n2. Testing service health checks...")
    services = ['API Service', 'Command System', 'Card Generator']
    for service in services:
        health = dashboard.check_service_health(service)
        print(f"   {service}: {health.status.value} "
              f"({health.response_time_ms:.1f}ms)" if health.response_time_ms else "N/A")
    
    # Test 3: Collect performance metrics
    print("\n3. Testing performance metrics collection...")
    perf_metrics = dashboard.collect_performance_metrics()
    print(f"   API Response: {perf_metrics.api_response_time_ms:.1f}ms")
    print(f"   Command Execution: {perf_metrics.command_execution_time_ms:.1f}ms")
    print(f"   Card Generation: {perf_metrics.card_generation_time_ms:.1f}ms")
    print(f"   Tasks: {perf_metrics.active_tasks} active, "
          f"{perf_metrics.completed_tasks} completed")
    
    # Test 4: Generate report
    print("\n4. Testing report generation...")
    report = dashboard.generate_report()
    print(f"   Report generated with {len(report['alerts'])} alerts")
    print(f"   System metrics history: {report['system']['history_size']}")
    print(f"   Performance metrics history: {report['performance']['history_size']}")
    
    # Test 5: Get metrics summary
    print("\n5. Testing metrics summary...")
    summary = dashboard.get_metrics_summary()
    print(f"   Services: {summary['services_healthy']}/{summary['services_total']} healthy")
    if summary['system']['cpu_avg']:
        print(f"   CPU Average: {summary['system']['cpu_avg']:.1f}%")
    
    # Test 6: Display current status
    print("\n6. Testing status display...")
    dashboard.display_current_status()
    
    # Test 7: Save report to file
    print("\n7. Testing report saving...")
    dashboard.save_report("test_monitoring_report.json")
    print("   Report saved to test_monitoring_report.json")
    
    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("="*60)
    
    return True

def test_monitoring_loop():
    """Test continuous monitoring"""
    print("\nTesting continuous monitoring (5 seconds)...")
    print("="*60)
    
    dashboard = MonitoringDashboard(history_size=5)
    
    try:
        # Start monitoring
        dashboard.start_monitoring(interval_seconds=1)
        
        # Let it run for 5 seconds
        time.sleep(5)
        
        # Stop monitoring
        dashboard.stop_monitoring()
        
        print(f"Collected {len(dashboard.system_metrics_history)} system metrics")
        print(f"Collected {len(dashboard.performance_metrics_history)} performance metrics")
        
    except KeyboardInterrupt:
        dashboard.stop_monitoring()
        print("\nMonitoring stopped by user")
    
    print("="*60)
    print("Continuous monitoring test completed!")

if __name__ == "__main__":
    # Run basic tests
    test_monitoring_dashboard()
    
    # Ask user if they want to test continuous monitoring
    response = input("\nDo you want to test continuous monitoring? (y/n): ")
    if response.lower() == 'y':
        test_monitoring_loop()
    
    print("\nMonitoring dashboard tests completed!")