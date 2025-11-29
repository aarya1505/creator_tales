document.addEventListener('DOMContentLoaded', function() {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const navMenu = document.getElementById('navMenu');
  
  if (mobileMenuBtn && navMenu) {
      mobileMenuBtn.addEventListener('click', function() {
          navMenu.classList.toggle('active');
      });
  }
  
  document.addEventListener('click', function(e) {
      if (navMenu && mobileMenuBtn && !navMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
          navMenu.classList.remove('active');
      }
  });
  
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach(function(message) {
      setTimeout(function() {
          message.style.opacity = '0';
          message.style.transform = 'translateY(-10px)';
          setTimeout(function() {
              message.remove();
          }, 300);
      }, 5000);
  });
  
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  dropdownToggles.forEach(function(toggle) {
      toggle.addEventListener('click', function(e) {
          if (window.innerWidth <= 768) {
              e.preventDefault();
              const dropdown = this.closest('.nav-dropdown');
              dropdown.classList.toggle('open');
          }
      });
  });
  
  const forms = document.querySelectorAll('.tool-form');
  forms.forEach(function(form) {
      form.addEventListener('submit', function() {
          const submitBtn = form.querySelector('button[type="submit"]');
          if (submitBtn) {
              const originalText = submitBtn.innerHTML;
              submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
              submitBtn.disabled = true;
              
              setTimeout(function() {
                  submitBtn.innerHTML = originalText;
                  submitBtn.disabled = false;
              }, 30000);
          }
      });
  });
  
  const textareas = document.querySelectorAll('textarea');
  textareas.forEach(function(textarea) {
      textarea.addEventListener('input', function() {
          this.style.height = 'auto';
          this.style.height = (this.scrollHeight) + 'px';
      });
  });
});

function showNotification(message, type) {
  const existingNotifications = document.querySelectorAll('.notification');
  existingNotifications.forEach(n => n.remove());
  
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `<span>${message}</span>`;
  document.body.appendChild(notification);
  
  setTimeout(function() {
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(100%)';
      setTimeout(function() {
          notification.remove();
      }, 300);
  }, 3000);
}

function copyToClipboard(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
      const text = element.innerText || element.textContent;
      navigator.clipboard.writeText(text).then(function() {
          showNotification('Copied to clipboard!', 'success');
      }).catch(function() {
          const textArea = document.createElement('textarea');
          textArea.value = text;
          document.body.appendChild(textArea);
          textArea.select();
          document.execCommand('copy');
          document.body.removeChild(textArea);
          showNotification('Copied to clipboard!', 'success');
      });
  }
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(function() {
      showNotification('Copied to clipboard!', 'success');
  }).catch(function() {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      showNotification('Copied to clipboard!', 'success');
  });
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
      const later = () => {
          clearTimeout(timeout);
          func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
  };
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
          target.scrollIntoView({
              behavior: 'smooth'
          });
      }
  });
});

window.addEventListener('scroll', debounce(function() {
  const navbar = document.querySelector('.navbar');
  if (navbar) {
      if (window.scrollY > 50) {
          navbar.classList.add('scrolled');
      } else {
          navbar.classList.remove('scrolled');
      }
  }
}, 10));

function formatNumber(num) {
  if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

function animateValue(element, start, end, duration) {
  let startTimestamp = null;
  const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = Math.floor(progress * (end - start) + start);
      element.textContent = formatNumber(current);
      if (progress < 1) {
          window.requestAnimationFrame(step);
      }
  };
  window.requestAnimationFrame(step);
}

const observerOptions = {
  threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
      if (entry.isIntersecting) {
          entry.target.classList.add('visible');
      }
  });
}, observerOptions);

document.querySelectorAll('.feature-card, .action-card, .result-card').forEach(el => {
  observer.observe(el);
});