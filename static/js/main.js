document.addEventListener('DOMContentLoaded', function() {
  // Handle expiration warnings
  const expirationWarnings = document.querySelectorAll('.expiration-warning');
  if (expirationWarnings.length > 0) {
    setTimeout(() => {
      expirationWarnings.forEach(warning => {
        warning.classList.add('fade-in');
      });
    }, 300);
  }
  
  // Recipe match percentage visual indicators
  const matchBars = document.querySelectorAll('.match-bar');
  matchBars.forEach(bar => {
    const percentage = parseFloat(bar.getAttribute('data-percentage'));
    const progressBar = bar.querySelector('.match-progress');
    
    setTimeout(() => {
      progressBar.style.width = `${percentage}%`;
      
      // Set color based on match percentage
      if (percentage >= 80) {
        progressBar.style.backgroundColor = 'var(--success)';
      } else if (percentage >= 50) {
        progressBar.style.backgroundColor = 'var(--sage-green)';
      } else if (percentage >= 30) {
        progressBar.style.backgroundColor = 'var(--warning)';
      } else {
        progressBar.style.backgroundColor = 'var(--terracotta)';
      }
    }, 100);
  });
  
  // Add ingredient form quantity validations
  const quantityInput = document.getElementById('quantity');
  if (quantityInput) {
    quantityInput.addEventListener('input', function() {
      if (parseFloat(this.value) <= 0) {
        this.setCustomValidity('Quantity must be greater than 0');
      } else {
        this.setCustomValidity('');
      }
    });
  }
  
  // Recipe search filters toggle
  const filterToggle = document.getElementById('filter-toggle');
  const filterForm = document.getElementById('filter-form');
  
  if (filterToggle && filterForm) {
    filterToggle.addEventListener('click', function() {
      if (filterForm.classList.contains('d-none')) {
        filterForm.classList.remove('d-none');
        filterForm.classList.add('slide-in-up');
        filterToggle.textContent = 'Hide Filters';
      } else {
        filterForm.classList.add('d-none');
        filterForm.classList.remove('slide-in-up');
        filterToggle.textContent = 'Show Filters';
      }
    });
  }
  
  // Recipe detail - Complete recipe modal
  const completeRecipeBtn = document.getElementById('complete-recipe-btn');
  const completeModal = document.getElementById('complete-modal');
  const closeModalBtn = document.getElementById('close-modal');
  
  if (completeRecipeBtn && completeModal) {
    completeRecipeBtn.addEventListener('click', function() {
      completeModal.style.display = 'flex';
      setTimeout(() => {
        completeModal.classList.add('modal-open');
      }, 10);
    });
    
    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', function() {
        completeModal.classList.remove('modal-open');
        setTimeout(() => {
          completeModal.style.display = 'none';
        }, 300);
      });
    }
    
    window.addEventListener('click', function(event) {
      if (event.target === completeModal) {
        completeModal.classList.remove('modal-open');
        setTimeout(() => {
          completeModal.style.display = 'none';
        }, 300);
      }
    });
  }
  
  // Meal Plan - Add recipe modal
  const addRecipeButtons = document.querySelectorAll('.add-recipe-btn');
  const mealPlanModal = document.getElementById('meal-plan-modal');
  const closeMealPlanModalBtn = document.getElementById('close-meal-plan-modal');
  
  if (addRecipeButtons.length > 0 && mealPlanModal) {
    addRecipeButtons.forEach(button => {
      button.addEventListener('click', function() {
        const day = this.getAttribute('data-day');
        const mealType = this.getAttribute('data-meal-type');
        
        document.getElementById('day_of_week').value = day;
        document.getElementById('meal_type').value = mealType;
        
        mealPlanModal.style.display = 'flex';
        setTimeout(() => {
          mealPlanModal.classList.add('modal-open');
        }, 10);
      });
    });
    
    if (closeMealPlanModalBtn) {
      closeMealPlanModalBtn.addEventListener('click', function() {
        mealPlanModal.classList.remove('modal-open');
        setTimeout(() => {
          mealPlanModal.style.display = 'none';
        }, 300);
      });
    }
    
    window.addEventListener('click', function(event) {
      if (event.target === mealPlanModal) {
        mealPlanModal.classList.remove('modal-open');
        setTimeout(() => {
          mealPlanModal.style.display = 'none';
        }, 300);
      }
    });
  }
  
  // Category filters for inventory
  const categoryFilters = document.querySelectorAll('.category-filter');
  const inventoryItems = document.querySelectorAll('.inventory-item');
  
  if (categoryFilters.length > 0 && inventoryItems.length > 0) {
    categoryFilters.forEach(filter => {
      filter.addEventListener('click', function() {
        const category = this.getAttribute('data-category');
        
        // Toggle active state
        categoryFilters.forEach(f => f.classList.remove('active'));
        this.classList.add('active');
        
        // Filter items
        if (category === 'all') {
          inventoryItems.forEach(item => {
            item.style.display = 'block';
          });
        } else {
          inventoryItems.forEach(item => {
            if (item.getAttribute('data-category') === category) {
              item.style.display = 'block';
            } else {
              item.style.display = 'none';
            }
          });
        }
      });
    });
  }
  
  // Mobile navigation toggle
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  
  if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener('click', function() {
      mobileMenu.classList.toggle('show');
      mobileMenuToggle.classList.toggle('open');
    });
  }
});

// Function to update recipe search results dynamically
function updateRecipeResults(recipes) {
  const resultsContainer = document.getElementById('recipe-results');
  
  if (!resultsContainer || !recipes) return;
  
  let html = '';
  
  if (recipes.length === 0) {
    html = '<p class="text-center">No recipes found matching your criteria.</p>';
  } else {
    recipes.forEach(recipe => {
      html += `
        <div class="recipe-card card">
          <img src="${recipe.image_url || 'https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg'}" alt="${recipe.name}" class="card-img">
          <div class="card-body">
            <h3 class="card-title">${recipe.name}</h3>
            <p class="card-text">${recipe.description}</p>
            <div class="recipe-meta">
              <span>${recipe.prep_time + recipe.cook_time} mins</span>
              <span>${recipe.difficulty}</span>
            </div>
            <div class="match-indicator">
              <div class="match-bar" data-percentage="${recipe.match_percentage || 0}">
                <div class="match-progress" style="width: 0%"></div>
              </div>
              <span class="match-text">${Math.round(recipe.match_percentage || 0)}%</span>
            </div>
            <div class="recipe-tags">
              ${recipe.tags.map(tag => `<span class="recipe-tag">${tag}</span>`).join('')}
            </div>
            <a href="/recipe/${recipe._id}" class="btn btn-primary mt-2">View Recipe</a>
          </div>
        </div>
      `;
    });
  }
  
  resultsContainer.innerHTML = html;
  
  // Initialize match bars after updating content
  const matchBars = document.querySelectorAll('.match-bar');
  matchBars.forEach(bar => {
    const percentage = parseFloat(bar.getAttribute('data-percentage'));
    const progressBar = bar.querySelector('.match-progress');
    
    setTimeout(() => {
      progressBar.style.width = `${percentage}%`;
      
      // Set color based on match percentage
      if (percentage >= 80) {
        progressBar.style.backgroundColor = 'var(--success)';
      } else if (percentage >= 50) {
        progressBar.style.backgroundColor = 'var(--sage-green)';
      } else if (percentage >= 30) {
        progressBar.style.backgroundColor = 'var(--warning)';
      } else {
        progressBar.style.backgroundColor = 'var(--terracotta)';
      }
    }, 100);
  });
}