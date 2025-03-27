// Product image preview functionality
document.addEventListener('DOMContentLoaded', function() {
    // File upload preview
    const setupFileUpload = (inputId, previewContainerId) => {
        const input = document.querySelector(`#${inputId} input[type="file"]`);
        const preview = document.querySelector(`#${inputId} .upload-placeholder`);
        
        if (input) {
            input.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.innerHTML = `
                            <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px;"/>
                            <p class="mt-2">Image selected</p>
                        `;
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
    };

    // Initialize file upload previews
    setupFileUpload('modelUpload');
    setupFileUpload('clothesUpload');

    // Product thumbnails click handler
    const thumbnails = document.querySelectorAll('.thumbnail');
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            const mainImage = document.querySelector('.main-image img');
            const thumbSrc = this.src;
            const mainSrc = mainImage.src;
            mainImage.src = thumbSrc;
            this.src = mainSrc;
        });
    });

    // Wishlist button toggle
    const wishButtons = document.querySelectorAll('.wish-btn');
    wishButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            icon.classList.toggle('far');
            icon.classList.toggle('fas');
            icon.classList.toggle('text-danger');
        });
    });

    // Size selector
    const sizeInputs = document.querySelectorAll('.size-option input');
    sizeInputs.forEach(input => {
        input.addEventListener('change', function() {
            sizeInputs.forEach(otherInput => {
                const label = otherInput.nextElementSibling;
                if (otherInput === this) {
                    label.classList.add('selected');
                } else {
                    label.classList.remove('selected');
                }
            });
        });
    });

    // Search functionality
    const searchForm = document.querySelector('form.d-flex');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input');
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
            }
        });
    }

    // Loading state for try-on form
    const tryOnForm = document.querySelector('.try-on-form');
    if (tryOnForm) {
        tryOnForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            submitBtn.disabled = true;
        });
    }

    // Price range filter
    const priceRange = document.querySelector('.price-range input[type="range"]');
    if (priceRange) {
        priceRange.addEventListener('input', function() {
            const value = this.value;
            const maxInput = document.querySelector('.price-inputs input[type="number"]:last-child');
            maxInput.value = value;
        });
    }

    // Filter toggle for mobile
    const filterToggle = document.querySelector('.filter-toggle');
    const filtersSection = document.querySelector('.filters-section');
    if (filterToggle && filtersSection) {
        filterToggle.addEventListener('click', function() {
            filtersSection.classList.toggle('show');
        });
    }
});
