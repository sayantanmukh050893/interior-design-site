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

// Know Better Form Handler
const knowBetterForm = document.getElementById('knowBetterForm');
const API_BASE_URL = window.location.origin; // Dynamically use the same domain as the frontend

console.log(`[Interior Design] API Base URL: ${API_BASE_URL}`);

if (knowBetterForm) {
    knowBetterForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('[Interior Design] Form submitted');
        
        // Get form data
        const formData = new FormData(knowBetterForm);
        const clientData = {
            name: formData.get('name'),
            email: formData.get('email'),
            about: formData.get('about'),
            preferred_colors: formData.get('preferred_colors'),
            likes: formData.get('likes'),
            dislikes: formData.get('dislikes'),
            hobbies: formData.get('hobbies'),
            requirements: formData.get('requirements'),
            additional_comments: formData.get('additional_comments')
        };
        
        const roomImage = formData.get('room_image');
        
        console.log('[Interior Design] Client Data:', clientData);
        console.log('[Interior Design] Room Image:', roomImage ? `${roomImage.name} (${roomImage.size} bytes)` : 'No image');
        
        if (!roomImage || roomImage.size === 0) {
            console.warn('[Interior Design] No room image provided');
            showNotification('Please upload a room image', 'error');
            return;
        }
        
        try {
            // Step 1: Generate prompt
            showNotification('Generating your design brief...', 'info');
            
            console.log(`[Interior Design] Sending POST to ${API_BASE_URL}/generate-prompt`);
            console.log('[Interior Design] Request payload:', clientData);
            
            const promptResponse = await fetch(`${API_BASE_URL}/generate-prompt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(clientData)
            });
            
            console.log(`[Interior Design] Response Status: ${promptResponse.status}`);
            console.log('[Interior Design] Response Headers:', {
                'Content-Type': promptResponse.headers.get('Content-Type'),
                'Access-Control-Allow-Origin': promptResponse.headers.get('Access-Control-Allow-Origin')
            });
            
            if (!promptResponse.ok) {
                const errorText = await promptResponse.text();
                console.error(`[Interior Design] API Error (${promptResponse.status}):`, errorText);
                throw new Error(`Failed to generate prompt: ${promptResponse.status} ${promptResponse.statusText}`);
            }
            
            const promptData = await promptResponse.json();
            console.log('[Interior Design] Prompt Data received:', promptData);
            
            displayPromptResult(promptData.prompt, clientData, roomImage, promptData.theme_info);
            
            showNotification('Design brief generated! Ready to transform your room.', 'success');
            
        } catch (error) {
            console.error('[Interior Design] Error:', error);
            console.error('[Interior Design] Error Stack:', error.stack);
            showNotification(`Error generating design brief: ${error.message}`, 'error');
        }
    });
}

// Prompt Builder Function (local version for backup)
function buildDesignerPrompt(data) {
    return `You are a senior interior designer.

Client Information:
Name: ${data.name}
About: ${data.about}

Client Preferences:
Colors: ${data.preferred_colors}
Likes: ${data.likes}
Dislikes: ${data.dislikes}
Hobbies: ${data.hobbies}
Requirements: ${data.requirements}

Additional Comments: ${data.additional_comments || 'None'}

Create:

- Theme recommendation based on preferences
- Mood board concept description
- Specific design elements to incorporate
- Design suggestions for their space transformation`;
}

// Display Prompt Result with Image Transformation
function displayPromptResult(prompt, clientData, roomImage, themeInfo) {
    const promptResult = document.getElementById('promptResult');
    const promptContent = document.getElementById('promptContent');
    
    // Convert uploaded image to base64
    const reader = new FileReader();
    reader.onload = function(e) {
        const originalImageBase64 = e.target.result;
        
        promptContent.innerHTML = `
            <div id="briefSection" style="margin-bottom: 2rem; display: none;">
                <h4>Your Personalized Design Brief</h4>
                <pre style="background: var(--bg-light); padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.9rem;">${prompt}</pre>
            </div>
            
            <hr style="margin: 2rem 0; border: none; border-top: 1px solid #ddd; display: none;">
            
            <div id="imageLikeSliderContainer" style="margin-top: 2rem;">
                <h4 style="text-align: center; margin-bottom: 1.5rem;">AI Room Transformation Preview</h4>
                
                <div class="image-comparison-slider" id="imageComparisonSlider">
                    <div class="img-wrapper-before">
                        <img id="imageOriginal" src="${originalImageBase64}" alt="Original room">
                        <span class="label label-before">Original</span>
                    </div>
                    <div class="img-wrapper-after">
                        <img id="imageTransformed" src="${originalImageBase64}" alt="Transformed room">
                        <span class="label label-after">Transformed</span>
                    </div>
                    <input type="range" min="0" max="100" value="50" class="slider-handle" id="sliderHandle" aria-label="Comparison slider">
                </div>
                
                <div id="generationProgress" style="display: none; margin-top: 2rem; text-align: center;">
                    <div style="position: relative; width: 120px; height: 120px; margin: 0 auto 2rem;">
                        <!-- Outer spinning ring -->
                        <div style="position: absolute; width: 100%; height: 100%; border: 4px solid rgba(201, 168, 106, 0.2); border-radius: 50%; animation: spin 3s linear infinite;"></div>
                        <!-- Middle spinning ring (reverse) -->
                        <div style="position: absolute; width: 85%; height: 85%; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 3px solid rgba(201, 168, 106, 0.4); border-radius: 50%; animation: spin-reverse 2s linear infinite;"></div>
                        <!-- Inner spinning ring -->
                        <div style="position: absolute; width: 70%; height: 70%; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 3px solid #C9A86A; border-radius: 50%; border-top-color: transparent; border-right-color: transparent; animation: spin 1.5s linear infinite;"></div>
                        <!-- Center dot -->
                        <div style="position: absolute; width: 20px; height: 20px; background: #C9A86A; border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); box-shadow: 0 0 20px rgba(201, 168, 106, 0.5);"></div>
                    </div>
                    <p id="loadingText" style="margin-bottom: 1rem; font-size: 1rem; color: var(--secondary-color); font-weight: 600; height: 1.5rem;">Generating your transformation...</p>
                    <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 1rem;">This may take a few minutes</p>
                    <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 1.5rem;">
                        <div style="width: 8px; height: 8px; background: #C9A86A; border-radius: 50%; opacity: 0.4; animation: bounce 1.2s ease-in-out infinite;"></div>
                        <div style="width: 8px; height: 8px; background: #C9A86A; border-radius: 50%; opacity: 0.6; animation: bounce 1.2s ease-in-out infinite 0.2s;"></div>
                        <div style="width: 8px; height: 8px; background: #C9A86A; border-radius: 50%; opacity: 0.8; animation: bounce 1.2s ease-in-out infinite 0.4s;"></div>
                    </div>
                </div>
                
                <div id="sliderButtonContainer" style="display: flex; gap: 1rem; margin-top: 1.5rem; justify-content: center;">
                    <button type="button" id="transformBtn" class="btn btn-primary">Generate Transformation</button>
                    <button type="button" id="downloadComparison" class="btn btn-secondary" style="display: none;">Download Comparison</button>
                </div>
            </div>
        `;
        
        promptResult.style.display = 'block';
        
        // Close button handler
        const closeBtn = promptResult.querySelector('.close-prompt');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                promptResult.style.display = 'none';
            });
        }
        
        // Image comparison slider handler
        // Left = original (0%), Right = transformed (100%)
        const sliderHandle = document.getElementById('sliderHandle');
        const imgWrapper = document.querySelector('.img-wrapper-after');
        
        if (sliderHandle) {
            sliderHandle.addEventListener('input', function(e) {
                const value = e.target.value;
                // Slider position determines transformed image width
                // 0 = all original visible, 100 = all transformed visible
                imgWrapper.style.width = value + '%';
                // Update the slider thumb position
                sliderHandle.style.left = value + '%';
            });
            // Initialize slider position
            sliderHandle.style.left = '50%';
        }
        
        // Transform button handler
        const transformBtn = document.getElementById('transformBtn');
        transformBtn.addEventListener('click', async () => {
            await transformRoomImage(roomImage, clientData, themeInfo, originalImageBase64);
        });
    };
    reader.readAsDataURL(roomImage);
}

// Transform Room Image
async function transformRoomImage(imageFile, clientData, themeInfo, originalImageBase64) {
    try {
        console.log('[Interior Design] Starting image transformation...');
        
        const transformBtn = document.getElementById('transformBtn');
        const generationProgress = document.getElementById('generationProgress');
        const imageTransformed = document.getElementById('imageTransformed');
        const sliderHandle = document.getElementById('sliderHandle');
        const downloadBtn = document.getElementById('downloadComparison');
        
        transformBtn.disabled = true;
        generationProgress.style.display = 'block';
        
        // Start cycling loading messages
        const messages = [
            'Generating your transformation...',
            'Analyzing your space...',
            'Applying design elements...',
            'Enhancing colors and textures...',
            'Finalizing your vision...',
            'Almost there...'
        ];
        let messageIndex = 0;
        const loadingText = document.getElementById('loadingText');
        const messageInterval = setInterval(() => {
            messageIndex = (messageIndex + 1) % messages.length;
            if (loadingText) {
                loadingText.textContent = messages[messageIndex];
            }
        }, 3000);
        
        // Store interval ID to clear later
        generationProgress.dataset.messageInterval = messageInterval;
        
        // Prepare form data
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('client_data', JSON.stringify(clientData));
        formData.append('theme_info', JSON.stringify(themeInfo || {}));
        
        console.log(`[Interior Design] POSTing to ${API_BASE_URL}/transform`);
        
        // Call transformation API
        const response = await fetch(`${API_BASE_URL}/transform`, {
            method: 'POST',
            body: formData
        });
        
        console.log(`[Interior Design] Transform Response Status: ${response.status}`);
        
        if (!response.ok) {
            const errorData = await response.text();
            console.error(`[Interior Design] Transform Error (${response.status}):`, errorData);
            throw new Error(`Transformation failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('[Interior Design] Transform result received');
        
        // Update the transformed image in the slider
        if (result.image_base64) {
            imageTransformed.src = `data:image/png;base64,${result.image_base64}`;
            
            // Reset slider to middle position
            sliderHandle.value = 50;
            const imgWrapper = document.querySelector('.img-wrapper-after');
            if (imgWrapper) {
                imgWrapper.style.width = '50%';
                sliderHandle.style.left = '50%';
            }
            
            // Enable slider interaction
            sliderHandle.disabled = false;
            sliderHandle.style.opacity = '1';
            sliderHandle.style.cursor = 'pointer';
            
            // Re-attach slider listener
            sliderHandle.oninput = function(e) {
                const value = e.target.value;
                imgWrapper.style.width = value + '%';
                sliderHandle.style.left = value + '%';
            };
            
            // Show download button
            downloadBtn.style.display = 'inline-block';
            
            // Setup download functionality
            downloadBtn.onclick = () => {
                downloadComparisonImage(
                    originalImageBase64.split(',')[1],
                    result.image_base64,
                    clientData.name
                );
            };
            
            showNotification('Your room has been transformed successfully! Drag the slider to compare.', 'success');
        }
        
        // Clear the message cycling interval
        if (generationProgress.dataset.messageInterval) {
            clearInterval(parseInt(generationProgress.dataset.messageInterval));
        }
        generationProgress.style.display = 'none';
        transformBtn.disabled = false;
        transformBtn.textContent = 'Regenerate Transformation';
        
    } catch (error) {
        console.error('[Interior Design] Transformation Error:', error);
        console.error('[Interior Design] Error Stack:', error.stack);
        showNotification(`Error transforming room: ${error.message}`, 'error');
        
        const transformBtn = document.getElementById('transformBtn');
        const generationProgress = document.getElementById('generationProgress');
        
        // Clear the message cycling interval
        if (generationProgress.dataset.messageInterval) {
            clearInterval(parseInt(generationProgress.dataset.messageInterval));
        }
        generationProgress.style.display = 'none';
        transformBtn.disabled = false;
    }
}

// Download comparison image
function downloadComparisonImage(originalBase64, transformedBase64, clientName) {
    try {
        // Create canvas for side-by-side comparison
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Create images
        const origImg = new Image();
        const transImg = new Image();
        
        origImg.onload = function() {
            transImg.onload = function() {
                const width = origImg.width + transImg.width;
                const height = Math.max(origImg.height, transImg.height);
                
                canvas.width = width;
                canvas.height = height;
                
                // Draw images side by side
                ctx.drawImage(origImg, 0, 0);
                ctx.drawImage(transImg, origImg.width, 0);
                
                // Add labels
                ctx.fillStyle = '#C9A86A';
                ctx.font = 'bold 20px Arial';
                ctx.fillText('Original', 10, 30);
                ctx.fillText('Transformed', origImg.width + 10, 30);
                
                // Download
                const link = document.createElement('a');
                link.href = canvas.toDataURL('image/png');
                link.download = `${clientName}-room-transformation.png`;
                link.click();
                
                showNotification('Comparison image downloaded!', 'success');
            };
            transImg.src = `data:image/png;base64,${transformedBase64}`;
        };
        origImg.src = `data:image/jpeg;base64,${originalBase64}`;
        
    } catch (error) {
        console.error('Download error:', error);
        showNotification('Could not download comparison image', 'error');
    }
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
    const grid = document.getElementById('testimonialGrid');
    const cards = document.querySelectorAll('.testimonial-card');
    if (!grid || cards.length === 0) return;
    let current = 0;

    // position cards in a row using the container's width for precise alignment
    function updatePositions() {
        const width = grid.clientWidth;
        cards.forEach((card, i) => {
            card.style.transform = `translateX(${(i - current) * width}px)`;
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
