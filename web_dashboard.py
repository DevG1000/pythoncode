#!/usr/bin/env python3
"""
Web-based Monitoring Dashboard for PythonCode Project
Provides a web interface for monitoring system metrics and service health
"""

from flask import Flask, render_template_string, jsonify
import threading
import time
from datetime import datetime
import json

# Import the monitoring dashboard
from monitoring_dashboard import MonitoringDashboard

app = Flask(__name__)
dashboard = MonitoringDashboard(history_size=50)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PythonCode Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 28px;
            font-weight: 600;
        }
        
        .header .timestamp {
            color: #666;
            font-size: 16px;
            background: #f0f0f0;
            padding: 8px 15px;
            border-radius: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 i {
            font-size: 24px;
        }
        
        .metric {
            margin-bottom: 15px;
        }
        
        .metric-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            color: #666;
            font-size: 14px;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 600;
            color: #333;
        }
        
        .progress-bar {
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .cpu-progress { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
        .memory-progress { background: linear-gradient(90deg, #2196F3, #03A9F4); }
        .disk-progress { background: linear-gradient(90deg, #FF9800, #FFC107); }
        
        .service-status {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #ccc;
        }
        
        .service-status.healthy { border-left-color: #4CAF50; }
        .service-status.degraded { border-left-color: #FF9800; }
        .service-status.unhealthy { border-left-color: #F44336; }
        
        .service-name {
            font-weight: 600;
            color: #333;
        }
        
        .service-response {
            color: #666;
            font-size: 14px;
        }
        
        .alert {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            color: white;
            font-weight: 500;
        }
        
        .alert.warning {
            background: linear-gradient(135deg, #FF9800, #FF5722);
        }
        
        .alert.critical {
            background: linear-gradient(135deg, #F44336, #D32F2F);
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.3s ease;
        }
        
        .btn:hover {
            opacity: 0.9;
        }
        
        .btn.secondary {
            background: linear-gradient(135deg, #6c757d, #495057);
        }
        
        .refresh-info {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 20px;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .header {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> PythonCode Monitoring Dashboard</h1>
            <div class="timestamp" id="timestamp">{{ timestamp }}</div>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Metrics Card -->
            <div class="card">
                <h2><i class="fas fa-server"></i> System Metrics</h2>
                <div class="metric">
                    <div class="metric-label">
                        <span>CPU Usage</span>
                        <span id="cpu-value">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill cpu-progress" id="cpu-progress" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Memory Usage</span>
                        <span id="memory-value">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill memory-progress" id="memory-progress" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Disk Usage</span>
                        <span id="disk-value">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill disk-progress" id="disk-progress" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Network</span>
                        <span id="network-value">0 MB/s</span>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Uptime</span>
                        <span id="uptime-value">0h</span>
                    </div>
                </div>
            </div>
            
            <!-- Service Health Card -->
            <div class="card">
                <h2><i class="fas fa-heartbeat"></i> Service Health</h2>
                <div id="services-container">
                    <!-- Services will be populated by JavaScript -->
                </div>
            </div>
            
            <!-- Performance Metrics Card -->
            <div class="card">
                <h2><i class="fas fa-tachometer-alt"></i> Performance</h2>
                <div class="metric">
                    <div class="metric-label">
                        <span>API Response</span>
                        <span id="api-response">0ms</span>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Command Execution</span>
                        <span id="command-execution">0ms</span>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Card Generation</span>
                        <span id="card-generation">0ms</span>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">
                        <span>Active Tasks</span>
                        <span id="active-tasks">0</span>
                    </div>
                </div>
            </div>
            
            <!-- Alerts Card -->
            <div class="card">
                <h2><i class="fas fa-exclamation-triangle"></i> Alerts</h2>
                <div id="alerts-container">
                    <!-- Alerts will be populated by JavaScript -->
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="refreshDashboard()">
                <i class="fas fa-sync-alt"></i> Refresh Now
            </button>
            <button class="btn secondary" onclick="generateReport()">
                <i class="fas fa-download"></i> Download Report
            </button>
            <button class="btn secondary" onclick="toggleAutoRefresh()">
                <i class="fas fa-play" id="auto-refresh-icon"></i> 
                <span id="auto-refresh-text">Auto Refresh: On</span>
            </button>
        </div>
        
        <div class="refresh-info">
            Dashboard auto-refreshes every 5 seconds. Last updated: <span id="last-updated">Just now</span>
        </div>
    </div>
    
    <script>
        let autoRefresh = true;
        let refreshInterval;
        
        // Format bytes to human readable
        function formatBytes(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Format time
        function formatTime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
        
        // Update dashboard with data
        function updateDashboard(data) {
            // Update timestamp
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
            document.getElementById('last-updated').textContent = 'Just now';
            
            // Update system metrics
            if (data.system && data.system.current) {
                const sys = data.system.current;
                document.getElementById('cpu-value').textContent = sys.cpu_percent.toFixed(1) + '%';
                document.getElementById('cpu-progress').style.width = sys.cpu_percent + '%';
                
                document.getElementById('memory-value').textContent = sys.memory_percent.toFixed(1) + '%';
                document.getElementById('memory-progress').style.width = sys.memory_percent + '%';
                
                document.getElementById('disk-value').textContent = sys.disk_usage_percent.toFixed(1) + '%';
                document.getElementById('disk-progress').style.width = sys.disk_usage_percent + '%';
                
                const networkSpeed = ((sys.network_sent_mb + sys.network_recv_mb) / 5).toFixed(1); // MB per 5 seconds
                document.getElementById('network-value').textContent = networkSpeed + ' MB/s';
                
                document.getElementById('uptime-value').textContent = formatTime(sys.system_uptime_seconds);
            }
            
            // Update performance metrics
            if (data.performance && data.performance.current) {
                const perf = data.performance.current;
                document.getElementById('api-response').textContent = perf.api_response_time_ms.toFixed(1) + 'ms';
                document.getElementById('command-execution').textContent = perf.command_execution_time_ms.toFixed(1) + 'ms';
                document.getElementById('card-generation').textContent = perf.card_generation_time_ms.toFixed(1) + 'ms';
                document.getElementById('active-tasks').textContent = perf.active_tasks;
            }
            
            // Update services
            const servicesContainer = document.getElementById('services-container');
            servicesContainer.innerHTML = '';
            
            if (data.services) {
                for (const [serviceName, service] of Object.entries(data.services)) {
                    const statusClass = service.status;
                    const statusIcon = statusClass === 'healthy' ? 'fa-check-circle' : 
                                      statusClass === 'degraded' ? 'fa-exclamation-circle' : 'fa-times-circle';
                    const statusColor = statusClass === 'healthy' ? '#4CAF50' : 
                                       statusClass === 'degraded' ? '#FF9800' : '#F44336';
                    
                    const serviceEl = document.createElement('div');
                    serviceEl.className = `service-status ${statusClass}`;
                    serviceEl.innerHTML = `
                        <div>
                            <div class="service-name">${serviceName}</div>
                            <div class="service-response">${service.response_time_ms ? service.response_time_ms.toFixed(1) + 'ms' : 'N/A'}</div>
                        </div>
                        <i class="fas ${statusIcon}" style="color: ${statusColor}; font-size: 24px;"></i>
                    `;
                    servicesContainer.appendChild(serviceEl);
                }
            }
            
            // Update alerts
            const alertsContainer = document.getElementById('alerts-container');
            alertsContainer.innerHTML = '';
            
            if (data.alerts && data.alerts.length > 0) {
                data.alerts.forEach(alert => {
                    const alertEl = document.createElement('div');
                    alertEl.className = `alert ${alert.type}`;
                    alertEl.innerHTML = `
                        <i class="fas ${alert.type === 'critical' ? 'fa-exclamation-circle' : 'fa-exclamation-triangle'}"></i>
                        ${alert.message}
                    `;
                    alertsContainer.appendChild(alertEl);
                });
            } else {
                alertsContainer.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">No alerts at this time</div>';
            }
        }
        
        // Fetch data from server
        async function fetchDashboardData() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            }
        }
        
        // Refresh dashboard
        function refreshDashboard() {
            fetchDashboardData();
        }
        
        // Toggle auto-refresh
        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const icon = document.getElementById('auto-refresh-icon');
            const text = document.getElementById('auto-refresh-text');
            
            if (autoRefresh) {
                icon.className = 'fas fa-play';
                text.textContent = 'Auto Refresh: On';
                startAutoRefresh();
            } else {
                icon.className = 'fas fa-pause';
                text.textContent = 'Auto Refresh: Off';
                clearInterval(refreshInterval);
            }
        }
        
        // Start auto-refresh
        function startAutoRefresh() {
            clearInterval(refreshInterval);
            refreshInterval = setInterval(refreshDashboard, 5000);
        }
        
        // Generate report
        async function generateReport() {
            try {
                const response = await fetch('/api/report');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'monitoring_report.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                console.error('Error generating report:', error);
                alert('Error generating report. Please try again.');
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshDashboard();
            startAutoRefresh();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template_string(DASHBOARD_TEMPLATE, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    # Collect latest metrics
    dashboard.collect_system_metrics()
    dashboard.check_all_services()
    dashboard.collect_performance_metrics()
    
    # Generate report
    report = dashboard.generate_report()
    return jsonify(report)

@app.route('/api/report')
def api_report():
    """API endpoint for downloading report"""
    dashboard.save_report("monitoring_report_latest.json")
    
    with open("monitoring_report_latest.json", "r", encoding="utf-8") as f:
        content = f.read()
    
    return content, 200, {
        'Content-Type': 'application/json',
        'Content-Disposition': 'attachment; filename=monitoring_report.json'
    }

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': len(dashboard.service_health_status)
    })

def start_monitoring_background():
    """Start background monitoring thread"""
    dashboard.start_monitoring(interval_seconds=5)
    print("Background monitoring started")

if __name__ == '__main__':
    # Start background monitoring
    monitoring_thread = threading.Thread(target=start_monitoring_background, daemon=True)
    monitoring_thread.start()
    
    # Start Flask app
    print("Starting web dashboard on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)