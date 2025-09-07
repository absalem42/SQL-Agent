// Global variables
const API_BASE_URL = 'http://localhost:8000';
let isLoading = false;

// Agent descriptions
const agentDescriptions = {
    router: "Automatically routes your questions to the most appropriate specialist agent based on your query.",
    sales: "Handles customer management, leads, orders, and all sales-related inquiries.",
    analytics: "Provides business insights, reports, and data analysis (Coming Soon).",
    finance: "Manages financial data, invoices, and accounting tasks (Coming Soon).",
    inventory: "Handles stock management, inventory tracking, and supply chain (Coming Soon)."
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    checkApiHealth();
    updateWelcomeTime();
    updateAgentDescription();
});

// Navigation handling
function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and sections
            navButtons.forEach(b => b.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));

            // Add active class to clicked button
            btn.classList.add('active');

            // Show corresponding section
            const sectionId = btn.id.replace('Btn', '');
            document.getElementById(sectionId).classList.add('active');
        });
    });
}

// Chart initialization
function initializeCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart').getContext('2d');
    new Chart(revenueCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue',
                data: [45000, 52000, 48000, 61000, 55000, 67000],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000) + 'K';
                        }
                    }
                }
            }
        }
    });

    // Pipeline Chart
    const pipelineCtx = document.getElementById('pipelineChart').getContext('2d');
    new Chart(pipelineCtx, {
        type: 'doughnut',
        data: {
            labels: ['Leads', 'Qualified', 'Proposals', 'Closed'],
            datasets: [{
                data: [42, 28, 15, 8],
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#f5576c'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Chat functionality
function initializeChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const exportBtn = document.getElementById('exportBtn');
    const agentSelect = document.getElementById('agentSelect');

    if (!chatInput || !sendBtn) {
        console.error('Chat elements not found');
        return;
    }

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Send message on Enter key (but not Shift+Enter)
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Character counter and validation
    chatInput.addEventListener('input', updateCharCounter);

    // Clear chat
    if (clearBtn) {
        clearBtn.addEventListener('click', clearChat);
    }

    // Export chat
    if (exportBtn) {
        exportBtn.addEventListener('click', exportChat);
    }

    // Agent selection change
    if (agentSelect) {
        agentSelect.addEventListener('change', updateAgentDescription);
    }

    // Focus on input
    chatInput.focus();
    
    // Initial button state
    updateSendButtonState();
}

function updateAgentDescription() {
    const agentSelect = document.getElementById('agentSelect');
    const agentDesc = document.getElementById('agentDescription');
    
    if (!agentSelect || !agentDesc) return;
    
    const selectedAgent = agentSelect.value;
    
    const descriptions = {
        router: '<strong>Router Agent:</strong> Automatically routes your questions to the most appropriate specialist agent based on your query.',
        sales: '<strong>Sales Agent:</strong> Handles customer management, leads, orders, and all sales-related inquiries.',
        analytics: '<strong>Analytics Agent:</strong> Provides business insights, reports, and data analysis (Coming Soon).',
        finance: '<strong>Finance Agent:</strong> Manages financial data, invoices, and accounting tasks (Coming Soon).',
        inventory: '<strong>Inventory Agent:</strong> Handles stock management, inventory tracking, and supply chain (Coming Soon).'
    };
    
    agentDesc.innerHTML = descriptions[selectedAgent] || descriptions.router;
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    console.log('sendMessage called, message:', message, 'isLoading:', isLoading);
    
    // Prevent sending if already loading or no message
    if (!message || isLoading) {
        console.log('Prevented sending: no message or loading');
        return;
    }

    // Clear input immediately
    chatInput.value = '';
    updateCharCounter();

    // Add user message to chat
    addMessage('user', message);

    // Show typing indicator and set loading state
    showTypingIndicator();
    setLoadingState(true);

    try {
        const agentSelect = document.getElementById('agentSelect');
        const selectedAgent = agentSelect ? agentSelect.value : 'router';

        console.log('Sending message:', message, 'to agent:', selectedAgent);

        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                agent: selectedAgent
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Received response:', data);
        
        // Add assistant response
        addMessage('assistant', data.response, data.agent_used, data.execution_time);
        
    } catch (error) {
        console.error('Chat error:', error);
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.', 'error');
        showError('Failed to send message. Please check your connection.');
    } finally {
        hideTypingIndicator();
        setLoadingState(false);
        chatInput.focus(); // Return focus to input
    }
}

function addMessage(sender, content, agentUsed = null, executionTime = null) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    let senderName = sender === 'user' ? 'You' : 'Assistant';
    if (agentUsed && agentUsed !== 'error') {
        senderName = `${agentUsed.charAt(0).toUpperCase() + agentUsed.slice(1)} Agent`;
    }
    
    const executionInfo = executionTime ? ` (${executionTime.toFixed(2)}s)` : '';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${sender === 'user' ? 'fas fa-user' : 'fas fa-robot'}"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="sender-name">${senderName}</span>
                <span class="message-time">${currentTime}${executionInfo}</span>
            </div>
            <div class="message-text">${formatMessage(content)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessage(content) {
    if (!content) return '';
    
    // Convert markdown-style formatting to HTML
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}

function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'block';
        scrollToBottom();
    }
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }
}

function updateCharCounter() {
    const chatInput = document.getElementById('chatInput');
    const charCount = document.getElementById('charCount');
    
    if (!chatInput || !charCount) return;
    
    const currentLength = chatInput.value.length;
    charCount.textContent = currentLength;
    
    // Color coding for character count
    if (currentLength > 450) {
        charCount.style.color = '#dc3545';
    } else if (currentLength > 400) {
        charCount.style.color = '#ffc107';
    } else {
        charCount.style.color = '#6c757d';
    }
    
    updateSendButtonState();
}

function updateSendButtonState() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    
    if (!chatInput || !sendBtn) return;
    
    const hasText = chatInput.value.trim().length > 0;
    const underLimit = chatInput.value.length <= 500;
    
    sendBtn.disabled = !hasText || !underLimit || isLoading;
    
    // Update button appearance
    if (sendBtn.disabled) {
        sendBtn.style.opacity = '0.5';
        sendBtn.style.cursor = 'not-allowed';
    } else {
        sendBtn.style.opacity = '1';
        sendBtn.style.cursor = 'pointer';
    }
    
    console.log('Button state updated:', {
        hasText,
        underLimit,
        isLoading,
        disabled: sendBtn.disabled
    });
}

function setLoadingState(loading) {
    console.log('Setting loading state:', loading);
    isLoading = loading;
    
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    
    if (!chatInput || !sendBtn) return;
    
    if (loading) {
        chatInput.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        sendBtn.style.opacity = '0.7';
    } else {
        chatInput.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        updateSendButtonState();
    }
}

function sendSuggestion(suggestion) {
    if (isLoading) return;
    
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;
    
    chatInput.value = suggestion;
    updateCharCounter();
    
    // Small delay to show the suggestion was selected
    setTimeout(() => {
        sendMessage();
    }, 100);
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">Helios ERP Assistant</span>
                        <span class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <div class="message-text">
                        Chat cleared! How can I help you today?
                    </div>
                </div>
            </div>
        `;
    }
}

function exportChat() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messages = chatMessages.querySelectorAll('.message');
    
    if (messages.length <= 1) {
        showError('No messages to export');
        return;
    }
    
    let chatText = 'Helios Dynamics ERP Chat Export\n';
    chatText += '=' .repeat(40) + '\n\n';
    
    messages.forEach(message => {
        const sender = message.querySelector('.sender-name')?.textContent || 'Unknown';
        const time = message.querySelector('.message-time')?.textContent || '';
        const text = message.querySelector('.message-text')?.textContent || '';
        
        if (text.trim()) {
            chatText += `[${time}] ${sender}:\n${text.trim()}\n\n`;
        }
    });
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `erp-chat-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function updateWelcomeTime() {
    const welcomeTime = document.getElementById('welcomeTime');
    if (welcomeTime) {
        welcomeTime.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}

async function checkApiHealth() {
    const statusDot = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');
    
    if (!statusDot || !statusText) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            statusDot.className = 'status-dot online';
            statusText.textContent = `Connected (${data.customer_count} customers)`;
            console.log('API Health:', data);
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('API Health check failed:', error);
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'Disconnected';
        showError('Could not connect to ERP backend. Please check if the server is running on port 8000.');
    }
}

function showError(message) {
    const errorToast = document.getElementById('errorToast');
    const errorMessage = document.getElementById('errorMessage');
    
    if (!errorToast || !errorMessage) {
        console.error('Error:', message);
        return;
    }
    
    errorMessage.textContent = message;
    errorToast.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

function hideError() {
    const errorToast = document.getElementById('errorToast');
    if (errorToast) {
        errorToast.style.display = 'none';
    }
}

// Sales functions
async function loadCustomers() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/customers`);
        const data = await response.json();
        
        document.getElementById('salesData').innerHTML = `
            <h4><i class="fas fa-users"></i> Customer List</h4>
            <pre>${data.data}</pre>
        `;
    } catch (error) {
        document.getElementById('salesData').innerHTML = `
            <p class="text-danger">Error loading customers: ${error.message}</p>
        `;
    } finally {
        hideLoading();
    }
}

async function loadLeads() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/leads`);
        const data = await response.json();
        
        document.getElementById('salesData').innerHTML = `
            <h4><i class="fas fa-target"></i> Lead List</h4>
            <pre>${data.data}</pre>
        `;
    } catch (error) {
        document.getElementById('salesData').innerHTML = `
            <p class="text-danger">Error loading leads: ${error.message}</p>
        `;
    } finally {
        hideLoading();
    }
}

async function loadOrders() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/orders`);
        const data = await response.json();
        
        document.getElementById('salesData').innerHTML = `
            <h4><i class="fas fa-shopping-cart"></i> Order List</h4>
            <pre>${data.data}</pre>
        `;
    } catch (error) {
        document.getElementById('salesData').innerHTML = `
            <p class="text-danger">Error loading orders: ${error.message}</p>
        `;
    } finally {
        hideLoading();
    }
}

async function loadSummary() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/customers/summary`);
        const data = await response.json();
        
        document.getElementById('salesData').innerHTML = `
            <h4><i class="fas fa-chart-pie"></i> Customer Summary</h4>
            <pre>${data.summary}</pre>
        `;
    } catch (error) {
        document.getElementById('salesData').innerHTML = `
            <p class="text-danger">Error loading summary: ${error.message}</p>
        `;
    } finally {
        hideLoading();
    }
}

// Dashboard data loading
async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/stats`);
        const data = await response.json();
        
        if (data.statistics) {
            document.getElementById('totalCustomers').textContent = data.statistics.customers || 0;
            document.getElementById('totalOrders').textContent = data.statistics.orders || 0;
            document.getElementById('activeLeads').textContent = data.statistics.leads || 0;
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Recent Activity
function loadRecentActivity() {
    const activities = [
        {
            time: '2 minutes ago',
            event: 'New order from Sara Fathy Inc',
            amount: '$3,967.47'
        },
        {
            time: '15 minutes ago',
            event: 'Lead scored: Mohamed Adel Corp',
            amount: '8.2/10'
        },
        {
            time: '1 hour ago',
            event: 'Payment received from Omar Ali Co',
            amount: '$1,540.70'
        },
        {
            time: '3 hours ago',
            event: 'New customer registered: Mina Adel Systems',
            amount: ''
        }
    ];

    const activityList = document.getElementById('activityList');
    activityList.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-time">${activity.time}</div>
            <div class="activity-event">${activity.event}</div>
            <div class="activity-amount">${activity.amount}</div>
        </div>
    `).join('');
}

// Analytics
async function generateReport() {
    const reportSelect = document.getElementById('reportSelect');
    const reportType = reportSelect.value;
    
    showLoading();
    
    try {
        // Simulate different report types
        let reportData = '';
        
        switch(reportType) {
            case 'customers':
                const response = await fetch(`${API_BASE_URL}/customers`);
                const data = await response.json();
                reportData = `<h4>Top Customers Report</h4><pre>${data.data}</pre>`;
                break;
            case 'sales':
                reportData = `
                    <h4>Monthly Sales Trend</h4>
                    <canvas id="salesTrendChart" width="400" height="200"></canvas>
                `;
                break;
            case 'leads':
                const leadsResponse = await fetch(`${API_BASE_URL}/leads`);
                const leadsData = await leadsResponse.json();
                reportData = `<h4>Lead Analysis</h4><pre>${leadsData.data}</pre>`;
                break;
            default:
                reportData = '<p>Report type not implemented yet.</p>';
        }
        
        document.getElementById('analyticsDisplay').innerHTML = reportData;
        
        // If sales chart, initialize it
        if (reportType === 'sales') {
            setTimeout(() => {
                const ctx = document.getElementById('salesTrendChart');
                if (ctx) {
                    new Chart(ctx.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                            datasets: [{
                                label: 'Sales',
                                data: [45000, 52000, 48000, 61000, 55000, 67000],
                                backgroundColor: '#667eea'
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
            }, 100);
        }
        
    } catch (error) {
        document.getElementById('analyticsDisplay').innerHTML = `
            <p class="text-danger">Error generating report: ${error.message}</p>
        `;
    } finally {
        hideLoading();
    }
}

// Add event listener for generate report button
document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generateReport');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateReport);
    }
});

// Utility functions
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Initialize agent description on load
document.addEventListener('DOMContentLoaded', updateAgentDescription);

// Periodic health check
setInterval(checkApiHealth, 30000); // Check every 30 seconds

// Debug function to check elements
function debugElements() {
    console.log('Chat elements check:', {
        chatInput: !!document.getElementById('chatInput'),
        sendBtn: !!document.getElementById('sendBtn'),
        chatMessages: !!document.getElementById('chatMessages'),
        agentSelect: !!document.getElementById('agentSelect')
    });
}

// Call debug on load
document.addEventListener('DOMContentLoaded', debugElements);
