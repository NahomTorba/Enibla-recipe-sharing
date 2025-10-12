document.addEventListener("DOMContentLoaded", () => {
  // Initialize save recipe functionality
  initializeSaveRecipe()

  // Initialize scroll to top
  initializeScrollToTop()

  // Initialize modal functionality
  initializeModal()

  // Initialize mobile menu (from home.js)
  if (typeof initializeMobileMenu === "function") {
    initializeMobileMenu()
  }

  // Initialize star rating
  initializeStarRating()

  // Initialize ingredients checklist
  initializeIngredientsChecklist()

  // Initialize numbered directions
  initializeNumberedDirections()
})

function initializeSaveRecipe() {
  const saveBtn = document.getElementById("saveRecipeBtn")

  if (saveBtn) {
    // Check if recipe is already saved
    checkSaveStatus(saveBtn)

    saveBtn.addEventListener("click", () => {
      const recipeId = saveBtn.dataset.recipeId
      const isSaved = saveBtn.classList.contains("saved")

      if (isSaved) {
        unsaveRecipe(recipeId, saveBtn)
      } else {
        saveRecipe(recipeId, saveBtn)
      }
    })
  }
}

function checkSaveStatus(saveBtn) {
  const recipeId = saveBtn.dataset.recipeId

  fetch(`/review/api/check-saved-recipe/${recipeId}/`, {
    method: "GET",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.is_saved) {
        saveBtn.classList.add("saved")
        saveBtn.querySelector(".save-text").textContent = "Saved"
        saveBtn.querySelector("i").className = "fas fa-bookmark"
      }
    })
    .catch((error) => {
      console.log("Error checking save status:", error)
    })
}

function saveRecipe(recipeId, saveBtn) {
  // Disable button during request
  saveBtn.disabled = true

  fetch(`/review/api/save-recipe/${recipeId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Update button state
        saveBtn.classList.add("saved")
        saveBtn.querySelector(".save-text").textContent = "Saved"
        saveBtn.querySelector("i").className = "fas fa-bookmark"

        // Show success modal
        showModal("Recipe Saved!", "This recipe has been saved to your profile.")
      } else {
        showModal("Error", data.message || "Failed to save recipe. Please try again.")
      }
    })
    .catch((error) => {
      console.error("Error saving recipe:", error)
      showModal("Error", "Failed to save recipe. Please try again.")
    })
    .finally(() => {
      saveBtn.disabled = false
    })
}

function unsaveRecipe(recipeId, saveBtn) {
  // Disable button during request
  saveBtn.disabled = true

  fetch(`/review/api/unsave-recipe/${recipeId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Update button state
        saveBtn.classList.remove("saved")
        saveBtn.querySelector(".save-text").textContent = "Save Recipe"
        saveBtn.querySelector("i").className = "fas fa-bookmark"

        // Show success modal
        showModal("Recipe Removed", "This recipe has been removed from your saved recipes.")
      } else {
        showModal("Error", data.message || "Failed to remove recipe. Please try again.")
      }
    })
    .catch((error) => {
      console.error("Error removing recipe:", error)
      showModal("Error", "Failed to remove recipe. Please try again.")
    })
    .finally(() => {
      saveBtn.disabled = false
    })
}

function initializeModal() {
  const modal = document.getElementById("saveModal")
  const closeBtn = document.getElementById("closeModal")

  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      hideModal()
    })
  }

  // Close modal when clicking outside
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        hideModal()
      }
    })
  }

  // Close modal with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal && modal.classList.contains("show")) {
      hideModal()
    }
  })
}

function showModal(title, message) {
  const modal = document.getElementById("saveModal")
  const modalTitle = document.getElementById("modalTitle")
  const modalMessage = document.getElementById("modalMessage")

  if (modal && modalTitle && modalMessage) {
    modalTitle.textContent = title
    modalMessage.textContent = message
    modal.classList.add("show")

    // Auto-hide after 3 seconds for success messages
    if (title.includes("Saved") || title.includes("Removed")) {
      setTimeout(() => {
        hideModal()
      }, 5000)
    }
  }
}

function hideModal() {
  const modal = document.getElementById("saveModal")
  if (modal) {
    modal.classList.remove("show")
  }
}

function initializeScrollToTop() {
  const scrollToTopBtn = document.getElementById("scrollToTop")

  if (scrollToTopBtn) {
    // Show/hide scroll to top button
    window.addEventListener("scroll", () => {
      if (window.pageYOffset > 300) {
        scrollToTopBtn.classList.add("show")
      } else {
        scrollToTopBtn.classList.remove("show")
      }
    })

    // Scroll to top functionality
    scrollToTopBtn.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      })
    })
  }
}

// Helper function to get CSRF token
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

// Initialize star rating
function initializeStarRating() {
  const starRating = document.getElementById("starRating")
  const ratingInput = document.querySelector('input[name="rating"]')

  if (starRating && ratingInput) {
    const stars = starRating.querySelectorAll("i")

    // Set initial rating if editing existing review
    const existingRating = ratingInput.value
    if (existingRating) {
      updateStarDisplay(stars, Number.parseInt(existingRating))
    }

    stars.forEach((star, index) => {
      star.addEventListener("click", () => {
        const rating = index + 1
        ratingInput.value = rating
        updateStarDisplay(stars, rating)
      })

      star.addEventListener("mouseenter", () => {
        updateStarDisplay(stars, index + 1)
      })
    })

    starRating.addEventListener("mouseleave", () => {
      const currentRating = Number.parseInt(ratingInput.value) || 0
      updateStarDisplay(stars, currentRating)
    })
  }
}

function updateStarDisplay(stars, rating) {
  stars.forEach((star, index) => {
    if (index < rating) {
      star.classList.add("active")
    } else {
      star.classList.remove("active")
    }
  })
}

// Initialize ingredients checklist
function initializeIngredientsChecklist() {
  const ingredientsContent = document.querySelector(".ingredients-content")
  const checklistContainer = document.getElementById("ingredientsChecklist")

  if (ingredientsContent && checklistContainer) {
    const text = ingredientsContent.textContent || ingredientsContent.innerText
    const lines = text.split("\n").filter((line) => line.trim() !== "")

    checklistContainer.innerHTML = ""

    lines.forEach((line, index) => {
      if (line.trim()) {
        const checklistItem = document.createElement("div")
        checklistItem.className = "checklist-item"
        checklistItem.dataset.index = index

        const checkbox = document.createElement("div")
        checkbox.className = "checklist-checkbox"
        checkbox.innerHTML = '<i class="fas fa-check" style="display: none;"></i>'

        const textSpan = document.createElement("span")
        textSpan.className = "checklist-text"
        textSpan.textContent = line.trim()

        checklistItem.appendChild(checkbox)
        checklistItem.appendChild(textSpan)

        // Add click event
        checklistItem.addEventListener("click", () => {
          toggleChecklistItem(checklistItem, checkbox)
        })

        checklistContainer.appendChild(checklistItem)
      }
    })

    // Load saved state
    loadChecklistState()
  }
}

function toggleChecklistItem(item, checkbox) {
  const isCompleted = item.classList.contains("completed")
  const checkIcon = checkbox.querySelector("i")

  if (isCompleted) {
    // Uncheck
    item.classList.remove("completed")
    checkbox.classList.remove("checked")
    checkIcon.style.display = "none"
  } else {
    // Check
    item.classList.add("completed")
    checkbox.classList.add("checked")
    checkIcon.style.display = "block"

    // Add completion animation
    item.style.transform = "scale(0.98)"
    setTimeout(() => {
      item.style.transform = "scale(1)"
    }, 150)
  }

  // Save state to localStorage
  saveChecklistState()
}

function saveChecklistState() {
  const recipeId = window.location.pathname.split("/").pop()
  const state = []

  const checklistItems = document.querySelectorAll("#ingredientsChecklist .checklist-item")
  checklistItems.forEach((item, index) => {
    state[index] = item.classList.contains("completed")
  })

  localStorage.setItem(`recipe_${recipeId}_checklist`, JSON.stringify(state))
}

function loadChecklistState() {
  const recipeId = window.location.pathname.split("/").pop()
  const savedState = localStorage.getItem(`recipe_${recipeId}_checklist`)

  if (savedState) {
    const state = JSON.parse(savedState)
    const checklistItems = document.querySelectorAll("#ingredientsChecklist .checklist-item")

    checklistItems.forEach((item, index) => {
      if (state[index]) {
        const checkbox = item.querySelector(".checklist-checkbox")
        const checkIcon = checkbox.querySelector("i")

        item.classList.add("completed")
        checkbox.classList.add("checked")
        checkIcon.style.display = "block"
      }
    })
  }
}

// Initialize numbered directions
function initializeNumberedDirections() {
  const directionsContent = document.getElementById("directionsContent")

  if (directionsContent) {
    // Check if content is not already wrapped in p tags
    if (!directionsContent.querySelector('p')) {
      // Get the text content
      const text = directionsContent.textContent || directionsContent.innerText
      
      // Split by line breaks and filter out empty lines
      const lines = text.split('\n').filter(line => line.trim() !== '')
      
      // Wrap each non-empty line in a p tag
      directionsContent.innerHTML = lines.map(line => 
        `<p>${line.trim()}</p>`
      ).join('')
    }
    
    console.log("Numbered directions initialized")
  }
}
