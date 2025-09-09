#!/usr/bin/env python3
"""
Simple HTTP server for Railway Traffic Decision-Support System demo.

This creates a basic web interface to demonstrate the system without
complex dependencies.
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime

class RailwayHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the Railway Traffic Decision-Support System."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.send_dashboard()
        elif self.path == '/health':
            self.send_health()
        elif self.path == '/api/status':
            self.send_api_status()
        elif self.path == '/api/optimize':
            self.send_optimization_result()
        else:
            super().do_GET()
    
    def send_dashboard(self):
        """Send the main dashboard HTML."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Railway Traffic Decision-Support System</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                .status-card { transition: transform 0.2s; }
                .status-card:hover { transform: translateY(-2px); }
                .metric-value { font-size: 2rem; font-weight: bold; }
                .metric-label { font-size: 0.9rem; color: #6c757d; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark">
                <div class="container-fluid">
                    <span class="navbar-brand mb-0 h1">
                        <i class="fas fa-train"></i> Railway Traffic Control
                    </span>
                    <div class="d-flex">
                        <button class="btn btn-outline-light me-2" onclick="refreshData()">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button class="btn btn-outline-warning" onclick="runOptimization()">
                            <i class="fas fa-brain"></i> Run Optimization
                        </button>
                    </div>
                </div>
            </nav>

            <div class="container-fluid mt-3">
                <!-- Status Cards -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card status-card bg-primary text-white">
                            <div class="card-body text-center">
                                <i class="fas fa-train fa-2x mb-2"></i>
                                <div class="metric-value" id="active-trains">12</div>
                                <div class="metric-label">Active Trains</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card status-card bg-danger text-white">
                            <div class="card-body text-center">
                                <i class="fas fa-clock fa-2x mb-2"></i>
                                <div class="metric-value" id="delayed-trains">3</div>
                                <div class="metric-label">Delayed Trains</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card status-card bg-success text-white">
                            <div class="card-body text-center">
                                <i class="fas fa-route fa-2x mb-2"></i>
                                <div class="metric-value" id="available-sections">8</div>
                                <div class="metric-label">Available Sections</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card status-card bg-info text-white">
                            <div class="card-body text-center">
                                <i class="fas fa-chart-line fa-2x mb-2"></i>
                                <div class="metric-value" id="throughput">45</div>
                                <div class="metric-label">Throughput (trains/hr)</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Train Status Table -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-list"></i> Train Status</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Train</th>
                                                <th>Status</th>
                                                <th>Delay</th>
                                                <th>Section</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td><span class="badge bg-success me-2"></span>12345 - Rajdhani Express</td>
                                                <td><span class="badge bg-primary">Running</span></td>
                                                <td>5 min</td>
                                                <td>Mumbai-Delhi</td>
                                            </tr>
                                            <tr>
                                                <td><span class="badge bg-danger me-2"></span>12346 - Shatabdi</td>
                                                <td><span class="badge bg-danger">Delayed</span></td>
                                                <td>15 min</td>
                                                <td>Delhi-Agra</td>
                                            </tr>
                                            <tr>
                                                <td><span class="badge bg-success me-2"></span>12347 - Duronto</td>
                                                <td><span class="badge bg-primary">Running</span></td>
                                                <td>On time</td>
                                                <td>Chennai-Bangalore</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Section Status -->
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-route"></i> Section Status</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Section</th>
                                                <th>Status</th>
                                                <th>Trains</th>
                                                <th>Capacity</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>Mumbai → Delhi</td>
                                                <td><span class="badge bg-success">Available</span></td>
                                                <td>1</td>
                                                <td>2</td>
                                            </tr>
                                            <tr>
                                                <td>Delhi → Agra</td>
                                                <td><span class="badge bg-warning">Occupied</span></td>
                                                <td>2</td>
                                                <td>2</td>
                                            </tr>
                                            <tr>
                                                <td>Chennai → Bangalore</td>
                                                <td><span class="badge bg-success">Available</span></td>
                                                <td>1</td>
                                                <td>3</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Optimization Results -->
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-brain"></i> Optimization Results</h5>
                            </div>
                            <div class="card-body">
                                <div id="optimization-results">
                                    <p class="text-muted">Click "Run Optimization" to generate recommendations.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                function refreshData() {
                    showAlert('Data refreshed successfully!', 'success');
                }

                function runOptimization() {
                    fetch('/api/optimize')
                        .then(response => response.json())
                        .then(data => {
                            displayOptimizationResults(data);
                            showAlert('Optimization completed!', 'success');
                        })
                        .catch(error => {
                            showAlert('Error running optimization', 'danger');
                        });
                }

                function displayOptimizationResults(result) {
                    const container = document.getElementById('optimization-results');
                    container.innerHTML = `
                        <div class="row">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Delay Reduction</h6>
                                    <div class="metric-value text-success">${result.delay_reduction} min</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Throughput Improvement</h6>
                                    <div class="metric-value text-info">${result.throughput_improvement}%</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Confidence</h6>
                                    <div class="metric-value text-warning">${result.confidence}%</div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h6>Computation Time</h6>
                                    <div class="metric-value text-secondary">${result.computation_time}s</div>
                                </div>
                            </div>
                        </div>
                        <hr>
                        <h6>Recommendations:</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Train</th>
                                        <th>Action</th>
                                        <th>Reason</th>
                                        <th>Confidence</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${result.decisions.map(decision => `
                                        <tr>
                                            <td>${decision.train}</td>
                                            <td><span class="badge bg-primary">${decision.action}</span></td>
                                            <td>${decision.reason}</td>
                                            <td>${decision.confidence}%</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                }

                function showAlert(message, type) {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
                    alertDiv.style.top = '20px';
                    alertDiv.style.right = '20px';
                    alertDiv.style.zIndex = '9999';
                    alertDiv.innerHTML = `
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    document.body.appendChild(alertDiv);
                    
                    setTimeout(() => {
                        if (alertDiv.parentNode) {
                            alertDiv.parentNode.removeChild(alertDiv);
                        }
                    }, 5000);
                }
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_health(self):
        """Send health check response."""
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": "Railway Traffic Decision-Support System",
            "version": "1.0.0-demo"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_api_status(self):
        """Send API status response."""
        response = {
            "status": "operational",
            "active_trains": 12,
            "delayed_trains": 3,
            "sections_occupied": 4,
            "total_sections": 12,
            "system_health": "operational",
            "last_optimization": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_optimization_result(self):
        """Send optimization result."""
        response = {
            "delay_reduction": 25,
            "throughput_improvement": 18.5,
            "confidence": 87.3,
            "computation_time": 2.34,
            "decisions": [
                {
                    "train": "12345 - Rajdhani Express",
                    "action": "proceed",
                    "reason": "Highest priority in precedence order",
                    "confidence": 92
                },
                {
                    "train": "12346 - Shatabdi",
                    "action": "wait",
                    "reason": "Waiting for higher priority train",
                    "confidence": 85
                },
                {
                    "train": "12347 - Duronto",
                    "action": "proceed",
                    "reason": "No conflicts detected",
                    "confidence": 95
                }
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def main():
    """Main entry point."""
    PORT = 8000
    
    print(f"🚆 Starting Railway Traffic Decision-Support System Demo")
    print(f"📍 Server running at http://localhost:{PORT}")
    print(f"🏥 Health check: http://localhost:{PORT}/health")
    print(f"📊 Dashboard: http://localhost:{PORT}/")
    print(f"🔧 API Status: http://localhost:{PORT}/api/status")
    print(f"🧠 Optimization: http://localhost:{PORT}/api/optimize")
    print(f"\nPress Ctrl+C to stop the server")
    
    with socketserver.TCPServer(("", PORT), RailwayHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    main()
