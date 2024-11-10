// server_documentation/scripts.js
document.addEventListener('DOMContentLoaded', () => {
    fetchMonitoringData();
    fetchModelCard();
    fetchConsentLogs();
    fetchSettings();
    checkSystemHealth();

    // Refresh data periodically
    setInterval(() => {
        fetchMonitoringData();
        checkSystemHealth();
    }, 1000); // Every 1 second
});

async function fetchMonitoringData() {
    try {
        const response = await fetch('/monitoring/performance');
        const data = await response.json();
        updatePerformanceDisplay(data);
    } catch (error) {
        console.error('Error fetching monitoring data:', error);
    }
}

async function fetchModelCard() {
    try {
        const response = await fetch('/model/card');
        const data = await response.json();
        updateModelCardDisplay(data);
    } catch (error) {
        console.error('Error fetching model card:', error);
    }
}

async function fetchConsentLogs() {
    try {
        const response = await fetch('/consent/logs');
        const data = await response.json();
        updateConsentLogsDisplay(data);
    } catch (error) {
        console.error('Error fetching consent logs:', error);
    }
}

async function fetchSettings() {
    try {
        const response = await fetch('/system/settings');
        const data = await response.json();
        updateSettingsDisplay(data);
    } catch (error) {
        console.error('Error fetching settings:', error);
    }
}

async function checkSystemHealth() {
    try {
        const response = await fetch('/system/health');
        const data = await response.json();
        updateHealthDisplay(data);
    } catch (error) {
        console.error('Error checking system health:', error);
    }
}

function renderPerformanceCharts(chartData) {
    // Process data
    const timestamps = chartData.map(d => new Date(d.timestamp).getTime());
    const confidenceData = chartData.map(d => d.confidence);
    const processingData = chartData.map(d => d.processing_time);

    // Confidence Chart Options
    const confidenceOptions = {
        series: [{
            name: 'Confidence Score',
            data: confidenceData.map((value, index) => ({
                x: timestamps[index],
                y: value
            }))
        }],
        chart: {
            type: 'line',
            height: 300,
            animations: {
                enabled: true
            },
            toolbar: {
                show: true
            }
        },
        stroke: {
            curve: 'smooth',
            width: 2
        },
        title: {
            text: 'Confidence Scores Over Time',
            align: 'left'
        },
        xaxis: {
            type: 'datetime',
            labels: {
                datetimeFormatter: {
                    year: 'yyyy',
                    month: 'MMM \'yy',
                    day: 'dd MMM',
                    hour: 'HH:mm'
                }
            }
        },
        yaxis: {
            title: {
                text: 'Confidence Score (%)'
            },
            min: 0,
            max: 100
        },
        tooltip: {
            x: {
                format: 'dd MMM yyyy HH:mm:ss'
            }
        }
    };

    // Processing Time Chart Options
    const processingOptions = {
        series: [{
            name: 'Processing Time',
            data: processingData.map((value, index) => ({
                x: timestamps[index],
                y: value
            }))
        }],
        chart: {
            type: 'line',
            height: 300,
            animations: {
                enabled: true
            },
            toolbar: {
                show: true
            }
        },
        stroke: {
            curve: 'smooth',
            width: 2
        },
        title: {
            text: 'Processing Times Over Time',
            align: 'left'
        },
        xaxis: {
            type: 'datetime',
            labels: {
                datetimeFormatter: {
                    year: 'yyyy',
                    month: 'MMM \'yy',
                    day: 'dd MMM',
                    hour: 'HH:mm'
                }
            }
        },
        yaxis: {
            title: {
                text: 'Processing Time (seconds)'
            },
            min: 0
        },
        tooltip: {
            x: {
                format: 'dd MMM yyyy HH:mm:ss'
            }
        }
    };

    // Render charts
    const confidenceChart = new ApexCharts(
        document.querySelector("#confidenceChart"),
        confidenceOptions
    );

    const processingChart = new ApexCharts(
        document.querySelector("#processingTimeChart"),
        processingOptions
    );

    confidenceChart.render();
    processingChart.render();
}

function updatePerformanceDisplay(data) {
    const perfDiv = document.getElementById('performanceMetrics');

    // Update container with charts
    perfDiv.innerHTML = `
        <div class="metrics-grid">
            <div class="chart-card">
                <div id="confidenceChart"></div>
            </div>
            <div class="chart-card">
                <div id="processingTimeChart"></div>
            </div>
        </div>
        <div class="metrics-summary">
            <div class="metric-box">
                <h4>Latest Results</h4>
                <p>Confidence: ${data.logs[data.logs.length - 1]?.confidence.toFixed(2) || 'N/A'}%</p>
                <p>Processing Time: ${data.logs[data.logs.length - 1]?.processing_time.toFixed(3) || 'N/A'}s</p>
            </div>
            <div class="metric-box">
                <h4>Averages</h4>
                <p>Avg Confidence: ${calculateAverage(data.logs, 'confidence').toFixed(2)}%</p>
                <p>Avg Processing: ${calculateAverage(data.logs, 'processing_time').toFixed(3)}s</p>
            </div>
        </div>
    `;

    // Render charts
    renderPerformanceCharts(data.logs);
}

function calculateAverage(logs, field) {
    if (!logs.length) return 0;
    return logs.reduce((acc, log) => acc + log[field], 0) / logs.length;
}

function updateModelCardDisplay(data) {
    const modelDiv = document.getElementById('modelCard');
    modelDiv.innerHTML = `
        <div class="model-info">
            <h3>${data.model_details.name} v${data.model_details.version}</h3>
            <p>${data.model_details.description}</p>
            <h4>Technical Details</h4>
            <ul>
                <li>Architecture: ${data.model_details.model_architecture}</li>
                <li>Backend: ${data.model_details.backend}</li>
            </ul>
            <h4>Performance Thresholds</h4>
            <ul>
                <li>Brightness: ${data.metrics.quality_threshold.brightness}</li>
                <li>Contrast: ${data.metrics.quality_threshold.contrast}</li>
                <li>Resolution: ${data.metrics.quality_threshold.resolution}</li>
            </ul>
        </div>
    `;
}

function updateConsentLogsDisplay(data) {
    const consentDiv = document.getElementById('consentLogs');
    // Sort records by date (most recent first)
    const sortedRecords = [...data.records].sort((a, b) =>
        new Date(b.consent_date) - new Date(a.consent_date)
    );

    consentDiv.innerHTML = `
        <div class="consent-summary">
            <p>Total Records: ${data.records.length}</p>
            <p>Active Consents: ${data.records.filter(r => !r.revoked).length}</p>
        </div>
        <table class="consent-table">
            <thead>
                <tr>
                    <th>User ID</th>
                    <th>Date</th>
                    <th>Purpose</th>
                    <th>Retention (days)</th>
                    <th>Status</th>
                    <th>Expiry Date</th>
                </tr>
            </thead>
            <tbody>
                ${sortedRecords.map(record => {
        const consentDate = new Date(record.consent_date);
        const expiryDate = new Date(consentDate.getTime() + record.retention_period * 24 * 60 * 60 * 1000);
        const isExpired = expiryDate < new Date();

        return `
                    <tr class="${record.revoked ? 'revoked' : ''} ${isExpired ? 'expired' : ''}">
                        <td>${record.user_id}</td>
                        <td>${consentDate.toLocaleDateString()}</td>
                        <td>${record.purpose}</td>
                        <td>${record.retention_period}</td>
                        <td>${record.revoked ? 'Revoked' : (isExpired ? 'Expired' : 'Active')}</td>
                        <td>${expiryDate.toLocaleDateString()}</td>
                    </tr>
                `}).join('')}
            </tbody>
        </table>
    `;
}

function updateSettingsDisplay(data) {
    const settingsDiv = document.getElementById('systemSettings');
    settingsDiv.innerHTML = `
        <div class="settings-grid">
            ${Object.entries(data).map(([category, settings]) => `
                <div class="settings-card">
                    <h3>${category}</h3>
                    <ul>
                        ${Object.entries(settings).map(([key, value]) => `
                            <li><strong>${key}:</strong> ${value}</li>
                        `).join('')}
                    </ul>
                </div>
            `).join('')}
        </div>
    `;
}

function updateHealthDisplay(data) {
    const healthDiv = document.getElementById('systemHealth');
    healthDiv.innerHTML = `
        <div class="health-status ${data.status === 'healthy' ? 'healthy' : 'unhealthy'}">
            <h3>System Health</h3>
            <p>Status: ${data.status}</p>
            <div class="health-details">
                <h4>Model Status</h4>
                <ul>
                    <li>Drift Detected: ${data.model_status.drift_detected ? 'Yes' : 'No'}</li>
                    <li>Last Calibration: ${new Date(data.model_status.last_calibration).toLocaleString()}</li>
                    <li>Performance Samples: ${data.model_status.performance_samples}</li>
                </ul>
                <h4>Storage Status</h4>
                <ul>
                    <li>Consent Records: ${data.storage.consent_records}</li>
                    <li>Monitoring Data: ${data.storage.monitoring_data ? 'Available' : 'Missing'}</li>
                </ul>
            </div>
        </div>
    `;
}