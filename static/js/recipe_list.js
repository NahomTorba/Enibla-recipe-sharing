// Recipe List JavaScript functionality
document.addEventListener("DOMContentLoaded", () => {
  // Initialize recipe list functionality
  initializeRecipeList()
  initializeSearch()
  initializeFilters()
  initializePagination()
  initializeSaveButtons()
})

function initializeRecipeList() {
  const recipeCards = document.querySelectorAll(".recipe-card")

  // Add click handlers for recipe cards
  recipeCards.forEach((card) => {
    card.addEventListener("click", (e) => {
      // Don't trigger if clicking on action buttons or links
      if (e.target.closest(".action-btn") || e.target.tagName === "A") return

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

function initializeSearch() {
  const searchInput = document.getElementById("recipeSearch")
  if (searchInput) {
    const debouncedSearch = debounce(performSearch, 300)
    searchInput.addEventListener("input", debouncedSearch)
  }
}

function performSearch(event) {
  const query = event.target.value.toLowerCase()
  const recipeCards = document.querySelectorAll(".recipe-card")
  let visibleCount = 0

  recipeCards.forEach((card) => {
    const title = card.querySelector(".recipe-title a").textContent.toLowerCase()
    const description = card.querySelector(".recipe-description").textContent.toLowerCase()
    const tags = card.dataset.tags ? card.dataset.tags.toLowerCase() : ""

    if (title.includes(query) || description.includes(query) || tags.includes(query)) {
      card.style.display = "block"
      visibleCount++
    } else {
      card.style.display = "none"
    }
  })

  // Update recipe count
  updateRecipeCount(visibleCount)
}

function initializeFilters() {
  const filterButtons = document.querySelectorAll(".filter-btn")

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons
      filterButtons.forEach((btn) => btn.classList.remove("active"))

      // Add active class to clicked button
      button.classList.add("active")

      // Filter recipes
      const filter = button.dataset.filter
      filterRecipes(filter)
    })
  })
}

function filterRecipes(filter) {
  const recipeCards = document.querySelectorAll(".recipe-card")
  let visibleCount = 0

  recipeCards.forEach((card) => {
    const tags = card.dataset.tags ? card.dataset.tags.toLowerCase() : ""

    if (filter === "all" || tags.includes(filter)) {
      card.style.display = "block"
      visibleCount++
    } else {
      card.style.display = "none"
    }
  })

  // Update recipe count
  updateRecipeCount(visibleCount)
}

function updateRecipeCount(count) {
  const recipeCountElement = document.querySelector(".recipe-count")
  if (recipeCountElement) {
    const plural = count !== 1 ? "s" : ""
    recipeCountElement.innerHTML = `
            <i class="fas fa-utensils"></i>
            ${count} delicious recipe${plural} ${count === 0 ? "found" : "waiting for you"}
        `
  }
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

function initializeSaveButtons() {
  const saveButtons = document.querySelectorAll(".save-btn")

  saveButtons.forEach((button) => {
    button.addEventListener("click", async (e) => {
      e.stopPropagation()

      const recipeId = button.dataset.recipeId
      const icon = button.querySelector("i")

      try {
        const response = await fetch(`/review/api/save-recipe/${recipeId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json",
          },
        })

        const data = await response.json()

        if (data.success) {
          if (data.saved) {
            icon.classList.remove("far")
            icon.classList.add("fas")
            button.style.background = "#ff6b35"
            button.style.color = "white"
          } else {
            icon.classList.remove("fas")
            icon.classList.add("far")
            button.style.background = "rgba(255, 255, 255, 0.9)"
            button.style.color = "#ff6b35"
          }

          // Show success message
          showToast(data.message, "success")
        } else {
          showToast(data.message || "An error occurred", "error")
        }
      } catch (error) {
        console.error("Error:", error)
        showToast("An error occurred while saving the recipe", "error")
      }
    })
  })
}

function showLoadingState() {
  const loadingOverlay = document.getElementById("loadingOverlay")
  if (loadingOverlay) {
    loadingOverlay.style.display = "flex"
  }
}

function hideLoadingState() {
  const loadingOverlay = document.getElementById("loadingOverlay")
  if (loadingOverlay) {
    loadingOverlay.style.display = "none"
  }
}

function showToast(message, type = "info") {
  // Create toast element
  const toast = document.createElement("div")
  toast.className = `toast toast-${type}`
  toast.innerHTML = `
        <div class="toast-content">
            <i class="fas ${type === "success" ? "fa-check-circle" : "fa-exclamation-circle"}"></i>
            <span>${message}</span>
        </div>
    `

  // Add toast styles
  const style = document.createElement("style")
  style.textContent = `
        .toast {
            position: fixed;
            top: 100px;
            right: 20px;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            border-left: 4px solid #ff6b35;
        }
        
        .toast-success {
            border-left-color: #10b981;
        }
        
        .toast-error {
            border-left-color: #ef4444;
        }
        
        .toast-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .toast-success .toast-content i {
            color: #10b981;
        }
        
        .toast-error .toast-content i {
            color: #ef4444;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `

  document.head.appendChild(style)
  document.body.appendChild(toast)

  // Remove toast after 3 seconds
  setTimeout(() => {
    toast.remove()
    style.remove()
  }, 3000)
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

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Export functions for potential use in other scripts
window.RecipeList = {
  initializeRecipeList,
  initializeSearch,
  initializeFilters,
  showLoadingState,
  hideLoadingState,
  debounce,
}
