// Recipe List JavaScript functionality
document.addEventListener("DOMContentLoaded", () => {
  // Initialize recipe list functionality
  initializeRecipeList()

  // Add smooth scrolling for pagination
  initializePagination()

  // Add loading states
  initializeLoadingStates()
})

function initializeRecipeList() {
  const recipeCards = document.querySelectorAll(".recipe-card")

  // Add click handlers for recipe cards
  recipeCards.forEach((card) => {
    card.addEventListener("click", (e) => {
      // Don't trigger if clicking on a link
      if (e.target.tagName === "A") return

      const link = card.querySelector(".recipe-title a")
      if (link) {
        window.location.href = link.href
      }
    })

    // Add keyboard navigation
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault()
        const link = card.querySelector(".recipe-title a")
        if (link) {
          window.location.href = link.href
        }
      }
    })

    // Make cards focusable
    card.setAttribute("tabindex", "0")
    card.setAttribute("role", "button")
    card.setAttribute("aria-label", `View recipe: ${card.querySelector(".recipe-title a").textContent}`)
  })
}

function initializePagination() {
  const paginationLinks = document.querySelectorAll(".pagination-link")

  paginationLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // Add loading state
      const currentPage = document.querySelector(".pagination-link.current")
      if (currentPage && this !== currentPage) {
        showLoadingState()
      }
    })
  })
}

function initializeLoadingStates() {
  // Add intersection observer for lazy loading images
  if ("IntersectionObserver" in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target
          if (img.dataset.src) {
            img.src = img.dataset.src
            img.removeAttribute("data-src")
            observer.unobserve(img)
          }
        }
      })
    })

    const lazyImages = document.querySelectorAll("img[data-src]")
    lazyImages.forEach((img) => imageObserver.observe(img))
  }
}

function showLoadingState() {
  // Create loading overlay
  const loadingOverlay = document.createElement("div")
  loadingOverlay.className = "loading-overlay"
  loadingOverlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Loading recipes...</p>
        </div>
    `

  // Add loading styles
  const style = document.createElement("style")
  style.textContent = `
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .loading-spinner {
            text-align: center;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `

  document.head.appendChild(style)
  document.body.appendChild(loadingOverlay)
}

// Utility functions
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Add search functionality (if needed in future)
function initializeSearch() {
  const searchInput = document.getElementById("recipe-search")
  if (searchInput) {
    const debouncedSearch = debounce(performSearch, 300)
    searchInput.addEventListener("input", debouncedSearch)
  }
}

function performSearch(event) {
  const query = event.target.value.toLowerCase()
  const recipeCards = document.querySelectorAll(".recipe-card")

  recipeCards.forEach((card) => {
    const title = card.querySelector(".recipe-title a").textContent.toLowerCase()
    const description = card.querySelector(".recipe-description").textContent.toLowerCase()

    if (title.includes(query) || description.includes(query)) {
      card.style.display = "block"
    } else {
      card.style.display = "none"
    }
  })
}

// Export functions for potential use in other scripts
window.RecipeList = {
  initializeRecipeList,
  initializePagination,
  showLoadingState,
  debounce,
}
