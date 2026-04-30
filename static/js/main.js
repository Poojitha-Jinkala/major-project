document.addEventListener('DOMContentLoaded', () => {

    // --- Mobile Navbar Toggle ---
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    
    if (navToggle && navLinks) {
      navToggle.addEventListener('click', () => {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        navLinks.style.flexDirection = 'column';
        navLinks.style.position = 'absolute';
        navLinks.style.top = '60px';
        navLinks.style.left = '0';
        navLinks.style.width = '100%';
        navLinks.style.background = 'rgba(15, 23, 42, 0.95)';
        navLinks.style.padding = '20px';
      });
    }
  
    // --- Auto-dismiss alerts after 5 seconds ---
    const alerts = document.querySelectorAll('.alert:not(.alert-error)');
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }, 5000);
    });
  
    // --- Animated Number Counters ---
    const counters = document.querySelectorAll('.stat-number');
    counters.forEach(counter => {
      const target = +counter.getAttribute('data-count');
      const duration = 2000;
      const step = target / (duration / 16); // 60fps
      
      let current = 0;
      const updateCounter = () => {
        current += step;
        if (current < target) {
          counter.innerText = Math.ceil(current);
          requestAnimationFrame(updateCounter);
        } else {
          counter.innerText = target;
        }
      };
      
      if (target > 0) updateCounter();
    });
  
    // --- Countdown Timer Logic ---
    const timers = document.querySelectorAll('.countdown-timer');
    
    function updateTimers() {
      timers.forEach(timer => {
        const endString = timer.getAttribute('data-end');
        if (!endString) return;
        
        const endTime = new Date(endString).getTime();
        const now = new Date().getTime();
        const distance = endTime - now;
  
        if (distance < 0) {
          timer.innerHTML = "Voting Closed";
          timer.style.color = "var(--danger)";
          return;
        }
  
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
  
        timer.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
      });
    }
  
    if (timers.length > 0) {
      updateTimers();
      setInterval(updateTimers, 1000);
    }
  
    // --- Register Form Loader ---
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
      registerForm.addEventListener('submit', function(e) {
        // Simple client-side validation
        const pwd1 = document.getElementById('id_password1').value;
        const pwd2 = document.getElementById('id_password2').value;
        
        if (pwd1 !== pwd2) {
          e.preventDefault();
          alert("Passwords do not match!");
          return;
        }
  
        const btn = document.getElementById('registerBtn');
        btn.querySelector('.btn-text').classList.add('hidden');
        btn.querySelector('.btn-loader').classList.remove('hidden');
        btn.disabled = true;
      });
    }
  
    // --- Particle Background Effect (Hero Section) ---
    const particles = document.getElementById('particles');
    if (particles) {
      for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = Math.random() * 5 + 'px';
        particle.style.height = particle.style.width;
        particle.style.background = 'rgba(255,255,255,0.1)';
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animation = `float ${Math.random() * 10 + 5}s linear infinite`;
        particles.appendChild(particle);
      }
    }
  });
