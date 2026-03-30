// Enhanced main.js with interactive features

// Mobile Menu Toggle
function toggleMenu() {
  const links = document.querySelector('.nav-links');
  if (links) {
    links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
  }
}

// Add hamburger menu for mobile
document.addEventListener('DOMContentLoaded', function() {
  // Create mobile menu button
  const navbar = document.querySelector('.navbar');
  if (navbar && window.innerWidth <= 768) {
    const hamburger = document.createElement('button');
    hamburger.id = 'hamburger';
    hamburger.innerHTML = '☰';
    hamburger.style.cssText = 'background: none; border: none; font-size: 1.5rem; color: var(--gray-700); cursor: pointer; display: none;';
    
    if (window.innerWidth <= 768) {
      hamburger.style.display = 'block';
      navbar.insertBefore(hamburger, navbar.firstChild);
    }
    
    hamburger.addEventListener('click', toggleMenu);
  }

  // Form validation and enhancement
  enhanceForm();
  
  // Add loading states to buttons
  enhanceButtons();
  
  // Character counter for textareas
  addCharacterCounter();
  
  // File upload preview
  enhanceFileUpload();
  
  // Smooth scrolling
  enableSmoothScroll();
  
  // Add word highlighting feature
  addWordHighlight();
  
  // Initialize tooltips
  initTooltips();
});

// Form Enhancement
function enhanceForm() {
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const button = form.querySelector('button[type="submit"]');
      if (button) {
        button.disabled = true;
        const originalText = button.textContent;
        button.innerHTML = '<span class="loading"></span> Processing...';
        
        // Re-enable after 5 seconds if still on page
        setTimeout(() => {
          button.disabled = false;
          button.textContent = originalText;
        }, 5000);
      }
    });

    // Real-time validation
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    inputs.forEach(input => {
      input.addEventListener('blur', function() {
        validateInput(this);
      });
    });
  });
}

// Input Validation
function validateInput(input) {
  if (input.value.trim() === '') {
    input.style.borderColor = 'var(--danger)';
    showError(input, 'This field is required');
  } else if (input.type === 'email' && !isValidEmail(input.value)) {
    input.style.borderColor = 'var(--danger)';
    showError(input, 'Please enter a valid email');
  } else {
    input.style.borderColor = 'var(--success)';
    removeError(input);
  }
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showError(input, message) {
  removeError(input);
  const error = document.createElement('small');
  error.className = 'error-message';
  error.style.cssText = 'color: var(--danger); font-size: 0.85rem; margin-top: 0.25rem; display: block;';
  error.textContent = message;
  input.parentNode.appendChild(error);
}

function removeError(input) {
  const error = input.parentNode.querySelector('.error-message');
  if (error) error.remove();
}

// Button Enhancement
function enhanceButtons() {
  const buttons = document.querySelectorAll('.btn-primary, .btn-secondary, .btn-danger');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-3px)';
    });
    button.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
}

// Character Counter
function addCharacterCounter() {
  const textareas = document.querySelectorAll('textarea');
  textareas.forEach(textarea => {
    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.style.cssText = 'text-align: right; color: var(--gray-500); font-size: 0.85rem; margin-top: 0.25rem;';
    textarea.parentNode.appendChild(counter);
    
    function updateCounter() {
      const count = textarea.value.length;
      const maxLength = textarea.getAttribute('maxlength') || 5000;
      counter.textContent = `${count} / ${maxLength} characters`;
      
      if (count > maxLength * 0.9) {
        counter.style.color = 'var(--warning)';
      } else {
        counter.style.color = 'var(--gray-500)';
      }
    }
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
  });
}

// File Upload Enhancement
function enhanceFileUpload() {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        // Remove previous preview
        const oldPreview = input.parentNode.querySelector('.file-preview');
        if (oldPreview) oldPreview.remove();
        
        // Create preview
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        preview.style.cssText = 'margin-top: 1rem; padding: 1rem; background: var(--gray-50); border-radius: 8px; display: flex; align-items: center; gap: 1rem;';
        
        if (file.type.startsWith('image/')) {
          const img = document.createElement('img');
          img.style.cssText = 'max-width: 100px; max-height: 100px; border-radius: 8px; object-fit: cover;';
          img.src = URL.createObjectURL(file);
          preview.appendChild(img);
        }
        
        const info = document.createElement('div');
        info.innerHTML = `
          <div style="font-weight: 600; color: var(--gray-700);">${file.name}</div>
          <div style="font-size: 0.85rem; color: var(--gray-500);">${(file.size / 1024).toFixed(2)} KB</div>
        `;
        preview.appendChild(info);
        
        input.parentNode.appendChild(preview);
      }
    });
  });
}

// Smooth Scrolling
function enableSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
}

// Word Highlighting (for result pages)
function addWordHighlight() {
  const resultBoxes = document.querySelectorAll('.result-box p');
  resultBoxes.forEach(box => {
    box.addEventListener('dblclick', function(e) {
      const selection = window.getSelection();
      const word = selection.toString().trim();
      
      if (word && word.split(' ').length === 1) {
        // Fetch synonyms
        fetchSynonyms(word, e.pageX, e.pageY);
      }
    });
  });
}

// Fetch Synonyms
function fetchSynonyms(word, x, y) {
  fetch(`/synonym?word=${encodeURIComponent(word)}`)
    .then(response => response.json())
    .then(data => {
      if (data.synonyms && data.synonyms.length > 0) {
        showSynonymPopup(word, data.synonyms, x, y);
      }
    })
    .catch(error => console.error('Error fetching synonyms:', error));
}

// Show Synonym Popup
function showSynonymPopup(word, synonyms, x, y) {
  // Remove existing popup
  const existingPopup = document.querySelector('.synonym-popup');
  if (existingPopup) existingPopup.remove();
  
  const popup = document.createElement('div');
  popup.className = 'synonym-popup';
  popup.style.cssText = `
    position: absolute;
    left: ${x}px;
    top: ${y}px;
    background: white;
    padding: 1rem;
    border-radius: 12px;
    box-shadow: var(--shadow-xl);
    z-index: 1000;
    min-width: 200px;
    max-width: 300px;
    animation: fadeInUp 0.3s ease-out;
  `;
  
  popup.innerHTML = `
    <div style="font-weight: 600; color: var(--primary); margin-bottom: 0.5rem;">
      Synonyms for "${word}"
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
      ${synonyms.map(syn => `
        <span style="
          background: var(--gray-100);
          padding: 0.25rem 0.75rem;
          border-radius: 6px;
          font-size: 0.9rem;
          color: var(--gray-700);
          cursor: pointer;
          transition: var(--transition);
        " onmouseover="this.style.background='var(--primary)'; this.style.color='white';" 
           onmouseout="this.style.background='var(--gray-100)'; this.style.color='var(--gray-700)';">
          ${syn}
        </span>
      `).join('')}
    </div>
    <button onclick="this.parentElement.remove()" style="
      margin-top: 0.75rem;
      padding: 0.5rem 1rem;
      background: var(--gray-100);
      border: none;
      border-radius: 6px;
      cursor: pointer;
      width: 100%;
      font-weight: 600;
      color: var(--gray-700);
    ">Close</button>
  `;
  
  document.body.appendChild(popup);
  
  // Auto-close after 10 seconds
  setTimeout(() => popup.remove(), 10000);
}

// Initialize Tooltips
function initTooltips() {
  const elements = document.querySelectorAll('[data-tooltip]');
  elements.forEach(el => {
    el.addEventListener('mouseenter', function(e) {
      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip';
      tooltip.textContent = this.getAttribute('data-tooltip');
      tooltip.style.cssText = `
        position: absolute;
        background: var(--dark);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
      `;
      
      document.body.appendChild(tooltip);
      
      const rect = this.getBoundingClientRect();
      tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
      tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
      
      this._tooltip = tooltip;
    });
    
    el.addEventListener('mouseleave', function() {
      if (this._tooltip) {
        this._tooltip.remove();
        this._tooltip = null;
      }
    });
  });
}

// Reading Progress Bar (for long content)
function addReadingProgress() {
  const progressBar = document.createElement('div');
  progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    z-index: 9999;
    transition: width 0.2s ease;
  `;
  document.body.appendChild(progressBar);
  
  window.addEventListener('scroll', function() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight - windowHeight;
    const scrolled = window.scrollY;
    const progress = (scrolled / documentHeight) * 100;
    progressBar.style.width = progress + '%';
  });
}

// Initialize reading progress on content pages
if (document.querySelector('.result-section, .practice-section')) {
  addReadingProgress();
}

// Text-to-Speech Control Enhancement
function enhanceAudioControls() {
  const audioElements = document.querySelectorAll('audio');
  audioElements.forEach(audio => {
    audio.style.cssText = 'width: 100%; max-width: 600px; margin: 2rem auto; display: block;';
  });
}

enhanceAudioControls();

// Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
  // Ctrl/Cmd + Enter to submit forms
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    const form = document.querySelector('form');
    if (form) form.submit();
  }
  
  // Escape to close popups
  if (e.key === 'Escape') {
    document.querySelectorAll('.synonym-popup').forEach(popup => popup.remove());
  }
});

// Add notification system
function showNotification(message, type = 'success') {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? 'var(--success)' : 'var(--danger)'};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow-xl);
    z-index: 10000;
    animation: slideInRight 0.3s ease-out;
  `;
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(400px); opacity: 0; }
  }
`;
document.head.appendChild(style);