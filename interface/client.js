document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
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

function showProfile(token) {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('profileSection').classList.remove('hidden');
    document.getElementById('tokenDisplay').value = token;
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