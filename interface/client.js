document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    // Refresh stats every 30 seconds if logged in
    setInterval(() => {
        const token = localStorage.getItem('authToken');
        if (token) {
            showProfile(token);
        }
    }, 30000);
});

function toggleForms() {
    document.getElementById('loginForm').classList.toggle('hidden');
    document.getElementById('registerForm').classList.toggle('hidden');
}

function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        showProfile(token);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password')
            })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('authToken', data.token);
            showProfile(data.token);
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (error) {
        alert('Login failed. Please try again.');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                purpose: formData.get('purpose')
            })
        });

        const data = await response.json();
        if (response.ok) {
            alert('Registration successful! Please login.');
            toggleForms();
        } else {
            alert(data.error || 'Registration failed');
        }
    } catch (error) {
        alert('Registration failed. Please try again.');
    }
}

async function showProfile(token) {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('profileSection').classList.remove('hidden');
    document.getElementById('tokenDisplay').value = token;

    try {
        console.log('Fetching stats with token:', token); // Debug log
        const response = await fetch('/user/stats', {
            method: 'GET',
            headers: {
                'Authorization': token,
                'Accept': 'application/json'
            }
        });

        console.log('Response status:', response.status); // Debug log

        if (response.ok) {
            const stats = await response.json();
            console.log('Received stats:', stats); // Debug log

            // Update stats display
            document.getElementById('totalComparisons').textContent = stats.total_comparisons || '0';
            document.getElementById('successfulComparisons').textContent = stats.successful || '0';
            document.getElementById('unsuccessfulComparisons').textContent = stats.unsuccessful || '0';

            const successRate = stats.total_comparisons > 0
                ? ((stats.successful / stats.total_comparisons) * 100).toFixed(1)
                : '0.0';
            document.getElementById('successRate').textContent = `${successRate}%`;

            // Update activity list
            const activityList = document.getElementById('activityList');
            if (stats.recent_activity && stats.recent_activity.length > 0) {
                activityList.innerHTML = stats.recent_activity
                    .map(activity => `
                        <div class="activity-item">
                            <span>${new Date(activity.timestamp).toLocaleString()}</span>
                            <span class="result ${activity.match_result ? 'success' : 'failure'}">
                                ${activity.match_result ? 'Match' : 'No Match'} 
                                (${(activity.confidence || 0).toFixed(1)}%)
                            </span>
                        </div>
                    `)
                    .join('');
            } else {
                activityList.innerHTML = '<p>No recent activity</p>';
            }
        } else {
            const error = await response.json();
            console.error('Stats error:', error);
            alert(`Failed to load statistics: ${error.error}`);
        }
    } catch (error) {
        console.error('Stats fetch error:', error);
        alert('Network error while loading statistics');
    }
}

function copyToken() {
    const tokenInput = document.getElementById('tokenDisplay');
    tokenInput.select();
    document.execCommand('copy');
    alert('Token copied to clipboard!');
}

function logout() {
    localStorage.removeItem('authToken');
    document.getElementById('profileSection').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
}

// Event Listeners
document.getElementById('login').addEventListener('submit', handleLogin);
document.getElementById('register').addEventListener('submit', handleRegister);