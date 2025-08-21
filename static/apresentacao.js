let currentReview = 0;
const reviews = document.querySelectorAll('.review');
const dotsContainer = document.querySelector('.dots-container');

function createDots() {
    reviews.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        dot.addEventListener('click', () => {
            currentReview = i;
            showReview(currentReview);
        });
        dotsContainer.appendChild(dot);
    });
}

function updateDots() {
    const dots = document.querySelectorAll('.dot');
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === currentReview);
    });
}

function showReview(index) {
    reviews.forEach((review, i) => {
        review.classList.remove('active');
        if (i === index) {
            review.classList.add('active');
        }
    });
    updateDots();
}

function changeReview(n) {
    currentReview += n;
    if (currentReview >= reviews.length) {
        currentReview = 0;
    }
    if (currentReview < 0) {
        currentReview = reviews.length - 1;
    }
    showReview(currentReview);
}

createDots();
showReview(currentReview);
