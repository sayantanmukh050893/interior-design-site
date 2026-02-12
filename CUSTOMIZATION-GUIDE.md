# 🎨 Quick Customization Guide

This guide helps you customize your website without technical knowledge. Each section tells you exactly what to change and where.

## 📝 Table of Contents
1. [Update Contact Information](#1-update-contact-information)
2. [Change Company Name](#2-change-company-name)
3. [Update Colors](#3-update-colors)
4. [Add Your Logo](#4-add-your-logo)
5. [Modify Services](#5-modify-services)
6. [Update Images](#6-update-images)
7. [Social Media Links](#7-social-media-links)
8. [Add WhatsApp Button](#8-add-whatsapp-button)

---

## 1. 📞 Update Contact Information

### What to Change
Your phone number, email, and address

### Where to Find It
**File:** `index.html`  
**Search for:** "Contact Information" (around line 560)

### How to Change

Find these lines and update with your information:

```html
<!-- PHONE NUMBER -->
<p>+91 XXXXX XXXXX</p>
↓ Change to ↓
<p>+91 98765 43210</p>

<!-- EMAIL -->
<p>info@eleganceinteriors.com</p>
↓ Change to ↓
<p>yourname@gmail.com</p>

<!-- ADDRESS -->
<p>Your City, India</p>
↓ Change to ↓
<p>123 Main Street, Mumbai, India</p>
```

**💡 Tip:** Use Ctrl+F (Windows) or Cmd+F (Mac) to search for text in the file.

---

## 2. 🏢 Change Company Name

### What to Change
Replace "Elegance Interiors" with your company name

### Where to Find It
**File:** `index.html`  
**Search for:** "Elegance Interiors" (appears multiple times)

### How to Change

**Method 1: Find and Replace All at Once**
1. Open `index.html` in a text editor (Notepad, TextEdit, VS Code)
2. Press Ctrl+H (Windows) or Cmd+Option+F (Mac)
3. Find: `Elegance Interiors`
4. Replace with: `Your Company Name`
5. Click "Replace All"

**Method 2: Manual Update**
Look for these specific locations:
- Line 8: Page title
- Line 35: Navigation logo
- Line 42: Hero section
- Line 650: Footer

---

## 3. 🎨 Update Colors

### What to Change
Main brand colors of the website

### Where to Find It
**File:** `styles.css`  
**Look at:** Very top of file (lines 8-13)

### How to Change

Find this section:
```css
:root {
    --primary-color: #C9A86A;      /* Main brand color (gold) */
    --primary-dark: #9D7E4D;       /* Darker shade */
    --secondary-color: #2C2C2C;    /* Dark gray for text */
}
```

**Common Color Codes:**
- Gold: `#C9A86A` (current)
- Navy Blue: `#1B3B6F`
- Forest Green: `#2D5016`
- Burgundy: `#800020`
- Teal: `#008080`
- Charcoal: `#36454F`

**💡 Tip:** Use [ColorPicker](https://www.google.com/search?q=color+picker) to find hex codes!

### Example Change
```css
/* Change from gold to navy blue */
--primary-color: #C9A86A;  ❌
--primary-color: #1B3B6F;  ✅

--primary-dark: #9D7E4D;   ❌
--primary-dark: #0F2847;   ✅
```

---

## 4. 🖼️ Add Your Logo

### What You Need
- Your logo file (PNG format recommended)
- Logo should be on transparent background
- Recommended size: 200-300px wide, 50-80px tall

### Where to Add It
**File:** `index.html`  
**Search for:** "nav-brand" (around line 35)

### How to Change

**Step 1:** Upload your logo file
- Place `logo.png` in the same folder as `index.html`

**Step 2:** Find this code:
```html
<div class="nav-brand">
    <h2>Elegance Interiors</h2>
</div>
```

**Step 3:** Replace with:
```html
<div class="nav-brand">
    <img src="logo.png" alt="Your Company Name" style="height: 50px;">
</div>
```

**💡 Tip:** Adjust `height: 50px` to make logo bigger or smaller.

---

## 5. 📋 Modify Services

### What to Change
Add, remove, or edit services you offer

### Where to Find It
**File:** `index.html`  
**Search for:** "Services Offered" (around line 180)

### How to Add a New Service

Find the services grid section and copy this template:

```html
<div class="service-card">
    <div class="service-icon">
        <!-- Icon SVG code here -->
    </div>
    <h3>Your New Service Name</h3>
    <p>Description of your service and what it includes.</p>
</div>
```

### How to Remove a Service

1. Find the service card you want to remove
2. Select from `<div class="service-card">` to its closing `</div>`
3. Delete the entire section

### How to Edit Service Text

Just change the text between the tags:
```html
<h3>Space Planning</h3>              <!-- Service name -->
<p>Optimize your layout...</p>       <!-- Service description -->
```

---

## 6. 📸 Update Images

### What to Change
Replace placeholder images with your own

### Where to Find It
**File:** `index.html`  
**Search for:** `https://images.unsplash.com`

### How to Change

**Option 1: Use Your Own Images**

1. Upload your image file to the same folder
2. Find the image code:
```html
<img src="https://images.unsplash.com/photo-..." alt="...">
```

3. Replace with:
```html
<img src="your-image.jpg" alt="Description">
```

**Option 2: Use Different Stock Photos**

Free stock photo websites:
- [Unsplash](https://unsplash.com) - Free high-quality images
- [Pexels](https://pexels.com) - Free stock photos
- [Pixabay](https://pixabay.com) - Free images

Steps:
1. Find an image you like
2. Get the image URL or download it
3. Replace the existing URL

**💡 Image Optimization Tips:**
- Keep images under 500KB for fast loading
- Use [TinyPNG](https://tinypng.com) to compress
- Recommended formats: JPG for photos, PNG for graphics

---

## 7. 📱 Social Media Links

### What to Change
Add your actual social media profile URLs

### Where to Find It
**File:** `index.html`  
**Search for:** "social-links" (around line 710)

### How to Change

Find these lines:
```html
<a href="#" aria-label="Facebook">       <!-- Facebook icon -->
<a href="#" aria-label="Instagram">      <!-- Instagram icon -->
<a href="#" aria-label="Pinterest">      <!-- Pinterest icon -->
```

Replace `href="#"` with your profile URLs:
```html
<a href="https://facebook.com/yourpage" aria-label="Facebook">
<a href="https://instagram.com/yourpage" aria-label="Instagram">
<a href="https://pinterest.com/yourpage" aria-label="Pinterest">
```

**💡 Tip:** If you don't have a social media account, delete that entire `<a>...</a>` section.

---

## 8. 💬 Add WhatsApp Button

### What You Need
Your WhatsApp Business number

### Where to Add It
**File:** `index.html`  
**Search for:** "Book a Consultation" (around line 55)

### How to Add

**Step 1:** Find the hero CTA section:
```html
<div class="hero-cta">
    <a href="#contact" class="btn btn-primary">Book a Consultation</a>
    <a href="#services" class="btn btn-secondary">Explore Services</a>
</div>
```

**Step 2:** Add WhatsApp button:
```html
<div class="hero-cta">
    <a href="#contact" class="btn btn-primary">Book a Consultation</a>
    <a href="https://wa.me/919876543210?text=Hi%2C%20I%27d%20like%20to%20inquire%20about%20interior%20design" 
       class="btn btn-secondary" target="_blank">
       WhatsApp Us
    </a>
    <a href="#services" class="btn btn-secondary">Explore Services</a>
</div>
```

**💡 Format your number:**
- Remove all spaces and special characters
- Add country code (91 for India)
- Example: +91 98765 43210 → 919876543210

---

## 🎯 Quick Reference Card

| What to Change | File | Search For | Line(s) |
|---------------|------|------------|---------|
| Phone/Email | index.html | "Contact Information" | ~560 |
| Company Name | index.html | "Elegance Interiors" | Multiple |
| Colors | styles.css | ":root {" | 8-13 |
| Logo | index.html | "nav-brand" | ~35 |
| Services | index.html | "Services Offered" | ~180 |
| Images | index.html | "unsplash.com" | Multiple |
| Social Media | index.html | "social-links" | ~710 |
| Hero Text | index.html | "hero-title" | ~55 |

---

## 🛠️ Tools You Need

### Text Editors (Choose One)
- **Notepad** (Windows) - Already installed
- **TextEdit** (Mac) - Already installed
- **VS Code** (All) - Download from code.visualstudio.com (recommended!)
- **Sublime Text** (All) - Download from sublimetext.com

### Image Editing (Optional)
- **Canva** - Create logos and graphics (canva.com)
- **GIMP** - Free Photoshop alternative
- **Paint.NET** (Windows) - Simple image editor

---

## ⚠️ Important Tips

### Before Making Changes
1. **ALWAYS keep a backup** of original files
2. Copy the entire folder before editing
3. Name backup: `interior-design-site-backup-2026-02-12`

### While Editing
1. Make ONE change at a time
2. Test after each change
3. Use "Find and Replace" carefully
4. Keep files organized

### After Changes
1. Save all files
2. Re-upload to your hosting (Netlify/Vercel)
3. Clear browser cache
4. Test on mobile and desktop
5. Check all links work

---

## 🆘 Undo Mistakes

### If Something Breaks
1. Don't panic!
2. Restore from your backup folder
3. Try the change again more carefully
4. Google the error message
5. Ask in platform support forums

### Common Mistakes & Fixes

**Problem:** Text appears on screen literally
```html
<!-- Wrong: -->
<p>Your Company Name</p>   <!-- Don't forget to change this! -->

<!-- Right: -->
<p>Your Company Name</p>
```

**Problem:** Broken layout
- **Cause:** Missing closing tag `</div>`
- **Fix:** Count opening and closing tags - they must match

**Problem:** Images not loading
- **Cause:** Wrong file path
- **Fix:** Make sure image is in same folder, check spelling

---

## 📞 Need More Help?

### Free Resources
- YouTube: Search "how to edit HTML"
- W3Schools: www.w3schools.com
- Stack Overflow: stackoverflow.com

### Community Support
- Netlify Community: community.netlify.com
- Web Dev Reddit: reddit.com/r/webdev

### Professional Help
- Hire on Fiverr (from ₹500)
- Local web developers
- Freelancers on Upwork

---

## ✅ Customization Checklist

Use this checklist to track your progress:

- [ ] Updated phone number
- [ ] Updated email address
- [ ] Updated office address
- [ ] Changed company name throughout site
- [ ] Added company logo
- [ ] Updated brand colors (if desired)
- [ ] Modified services list
- [ ] Added social media links
- [ ] Added WhatsApp button
- [ ] Replaced hero image
- [ ] Updated gallery images (when available)
- [ ] Tested all changes on live site
- [ ] Checked mobile responsiveness
- [ ] Verified all links work

---

**Remember:** Take your time and make changes one step at a time. You can't permanently break anything - you always have your backup! 🌟

Good luck customizing your website!
