// Mobile Menu Toggle
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const navMenu = document.querySelector('.nav-menu');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileMenuToggle.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a link
const navLinks = document.querySelectorAll('.nav-menu a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.padding = '0.5rem 0';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.padding = '1rem 0';
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
    }
    
    lastScroll = currentScroll;
});

// Contact Form Handling
const contactForm = document.getElementById('contactForm');

// if (contactForm) {
//     contactForm.addEventListener('submit', function(e) {
//         e.preventDefault();
        
//         // Get form data
//         const formData = new FormData(contactForm);
//         const data = Object.fromEntries(formData);
        
//         // Show success message (in production, this would send to a server)
//         showNotification('Thank you for your inquiry! We will get back to you within 24 hours.', 'success');
        
//         // Reset form
//         contactForm.reset();
        
//         // In production, you would send this data to your backend:
//         // fetch('/api/contact', {
//         //     method: 'POST',
//         //     headers: { 'Content-Type': 'application/json' },
//         //     body: JSON.stringify(data)
//         // });
        
//         console.log('Form submitted:', data);
//     });
// }

if (contactForm) {
    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(contactForm);
        
        try {
            const response = await fetch('https://formspree.io/f/mzdaeenj', {
                method: 'POST',
                body: formData,
                headers: { 
                    'Accept': 'application/json'
                }
            });
            
            if (response.ok) {
                showNotification('Thank you! We will contact you soon.', 'success');
                contactForm.reset();
            } else {
                showNotification('Error sending message. Please try again.', 'error');
            }
        } catch (error) {
            showNotification('Error sending message. Please try again.', 'error');
        }
    });
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification if any
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <p>${message}</p>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#C9A86A' : '#2C2C2C'};
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .notification-content p {
            margin: 0;
            flex: 1;
        }
        .notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background 0.2s;
        }
        .notification-close:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(notification);
    
    // Close button
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Add fade-in animation to sections
const sections = document.querySelectorAll('section');
sections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(section);
});

// Gallery image modal (simple lightbox effect)
const galleryItems = document.querySelectorAll('.gallery-item');
galleryItems.forEach(item => {
    item.addEventListener('click', function() {
        const img = this.querySelector('img');
        if (img) {
            createLightbox(img.src, img.alt);
        }
    });
});

function createLightbox(src, alt) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <button class="lightbox-close">&times;</button>
            <img src="${src}" alt="${alt}">
        </div>
    `;
    
    lightbox.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.95);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        animation: fadeIn 0.3s ease-out;
    `;
    
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .lightbox-content {
            position: relative;
            max-width: 90%;
            max-height: 90%;
        }
        .lightbox-content img {
            max-width: 100%;
            max-height: 85vh;
            object-fit: contain;
            border-radius: 8px;
        }
        .lightbox-close {
            position: absolute;
            top: -50px;
            right: 0;
            background: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            color: #2C2C2C;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
        }
        .lightbox-close:hover {
            transform: scale(1.1);
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(lightbox);
    document.body.style.overflow = 'hidden';
    
    const closeBtn = lightbox.querySelector('.lightbox-close');
    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    function closeLightbox() {
        lightbox.style.animation = 'fadeIn 0.3s ease-out reverse';
        setTimeout(() => {
            lightbox.remove();
            document.body.style.overflow = '';
        }, 300);
    }
    
    // Close on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLightbox();
        }
    });
}

// Service card hover effect enhancement
const serviceCards = document.querySelectorAll('.service-card');
serviceCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.borderColor = '#C9A86A';
    });
    card.addEventListener('mouseleave', function() {
        this.style.borderColor = '#E8E8E8';
    });
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Elegance Interiors website loaded successfully');
    
    // Add loading animation
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease-in';
        document.body.style.opacity = '1';
    }, 100);
});

// ================================
// Testimonials configuration
// ================================

// You can reconfigure names, reviews, ratings (1-5), and images below.
const testimonials = [
    {
        name: 'Ananya Roy',
        review: 'Working with Mukh Interiors was a dream. They understood my style instantly and transformed my living room into a warm, inviting space.',
        rating: 5,
        image: 'https://randomuser.me/api/portraits/women/68.jpg'
    },
    {
        name: 'Rohan Singh',
        review: 'The attention to detail and professionalism was outstanding. Highly recommend for anyone needing a modern makeover.',
        rating: 4,
        image: 'https://randomuser.me/api/portraits/men/45.jpg'
    }
];

function renderTestimonials() {
    const grid = document.getElementById('testimonialGrid');
    if (!grid) return;
    grid.innerHTML = '';
    testimonials.forEach((t, idx) => {
        const card = document.createElement('div');
        card.className = 'testimonial-card';
        card.dataset.index = idx;
        card.innerHTML = `
            <img src="${t.image}" alt="${t.name}">
            <p class="review">"${t.review}"</p>
            <p class="customer-name">${t.name}</p>
            <p class="rating">${'★'.repeat(t.rating)}${'☆'.repeat(5 - t.rating)}</p>
        `;
        grid.appendChild(card);
    });
}

function startTestimonialCarousel() {
    const cards = document.querySelectorAll('.testimonial-card');
    if (cards.length === 0) return;
    let current = 0;

    // position cards in a row and set initial transform
    function updatePositions() {
        cards.forEach((card, i) => {
            card.style.transform = `translateX(${(i - current) * 100}%)`;
        });
    }

    updatePositions();

    // recalc positions when the window width changes so cards stay aligned
    window.addEventListener('resize', updatePositions);

    setInterval(() => {
        current = (current + 1) % cards.length;
        updatePositions();
    }, 5000);
}

// ensure testimonials render and carousel starts after DOM is ready
// (this listener is separate from the earlier one that handles page load logging)
document.addEventListener('DOMContentLoaded', () => {
    renderTestimonials();
    startTestimonialCarousel();
});
