// Recipe Detail JavaScript Functionality for Text-based Model
class RecipeDetail {
  constructor() {
    this.timer = null
    this.timerSeconds = 0
    this.isTimerRunning = false

    this.init()
  }

  init() {
    this.setupEventListeners()
    this.setupStarRatings()
    this.setupScrollToTop()
    this.parseAndSetupIngredients()
    this.parseAndSetupInstructions()
    this.loadSavedProgress()
  }

  setupEventListeners() {
    // Share functionality
    const shareBtn = document.getElementById("shareBtn")
    const shareModal = document.getElementById("shareModal")
    const closeModal = document.getElementById("closeModal")

    if (shareBtn) {
      shareBtn.addEventListener("click", () => this.openShareModal())
    }

    if (closeModal) {
      closeModal.addEventListener("click", () => this.closeShareModal())
    }

    if (shareModal) {
      shareModal.addEventListener("click", (e) => {
        if (e.target === shareModal) this.closeShareModal()
      })
    }

    // Share buttons
    document.querySelectorAll(".share-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => this.shareRecipe(e.target.dataset.platform))
    })

    // Copy link
    const copyLinkBtn = document.getElementById("copyLink")
    if (copyLinkBtn) {
      copyLinkBtn.addEventListener("click", () => this.copyRecipeLink())
    }

    // Save recipe
    const saveBtn = document.getElementById("saveBtn")
    if (saveBtn) {
      saveBtn.addEventListener("click", () => this.saveRecipe())
    }

    // Timer functionality
    const timerBtn = document.getElementById("timerBtn")
    const startTimer = document.getElementById("startTimer")
    const pauseTimer = document.getElementById("pauseTimer")
    const resetTimer = document.getElementById("resetTimer")

    if (timerBtn) {
      timerBtn.addEventListener("click", () => this.toggleTimer())
    }

    if (startTimer) {
      startTimer.addEventListener("click", () => this.startTimer())
    }

    if (pauseTimer) {
      pauseTimer.addEventListener("click", () => this.pauseTimer())
    }

    if (resetTimer) {
      resetTimer.addEventListener("click", () => this.resetTimer())
    }

    // Fullscreen image
    const fullscreenBtn = document.getElementById("fullscreenBtn")
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener("click", () => this.toggleFullscreenImage())
    }

    // Review form
    const reviewForm = document.getElementById("reviewForm")
    if (reviewForm) {
      reviewForm.addEventListener("submit", (e) => this.submitReview(e))
    }
  }

  parseAndSetupIngredients() {
    const ingredientsContent = document.querySelector(".ingredients-content")
    const ingredientsList = document.getElementById("ingredientsList")

    if (!ingredientsContent || !ingredientsList) return

    const ingredientsText = ingredientsContent.textContent.trim()
    const ingredients = ingredientsText.split("\n").filter((line) => line.trim())

    let checklistHTML = ""
    ingredients.forEach((ingredient, index) => {
      const cleanIngredient = ingredient.trim().replace(/^[-•*]\s*/, "") // Remove bullet points
      if (cleanIngredient) {
        checklistHTML += `
          <div class="ingredient-item">
            <input type="checkbox" class="ingredient-checkbox" id="ingredient-${index}" onchange="recipeDetail.toggleIngredient(this)">
            <label for="ingredient-${index}" class="ingredient-text">${cleanIngredient}</label>
          </div>
        `
      }
    })

    ingredientsList.innerHTML = checklistHTML
  }

  parseAndSetupInstructions() {
    const instructionsContent = document.querySelector(".instructions-content")
    const instructionsList = document.getElementById("instructionsList")

    if (!instructionsContent || !instructionsList) return

    const instructionsText = instructionsContent.textContent.trim()
    const instructions = instructionsText.split("\n").filter((line) => line.trim())

    let checklistHTML = ""
    instructions.forEach((instruction, index) => {
      const cleanInstruction = instruction.trim().replace(/^\d+\.\s*/, "") // Remove numbering
      if (cleanInstruction) {
        checklistHTML += `
          <div class="instruction-item" data-step="${index + 1}">
            <div class="instruction-number">${index + 1}</div>
            <div class="instruction-content">
              <input type="checkbox" class="instruction-checkbox" id="instruction-${index}" onchange="recipeDetail.toggleInstruction(this)">
              <label for="instruction-${index}" class="instruction-text">${cleanInstruction}</label>
            </div>
          </div>
        `
      }
    })

    instructionsList.innerHTML = checklistHTML
  }

  setupStarRatings() {
    // Display ratings
    document.querySelectorAll(".stars").forEach((starsContainer) => {
      const rating = Number.parseFloat(starsContainer.dataset.rating) || 0
      const stars = starsContainer.querySelectorAll("i")

      stars.forEach((star, index) => {
        if (index < Math.floor(rating)) {
          star.classList.add("active")
        } else if (index < rating) {
          star.classList.add("half-active")
        }
      })
    })

    // Interactive rating input
    const starRating = document.getElementById("starRating")
    if (starRating) {
      const stars = starRating.querySelectorAll("i")
      const ratingInput = document.getElementById("ratingInput")

      stars.forEach((star, index) => {
        star.addEventListener("click", () => {
          const rating = index + 1
          ratingInput.value = rating

          stars.forEach((s, i) => {
            s.classList.toggle("active", i < rating)
          })
        })

        star.addEventListener("mouseenter", () => {
          stars.forEach((s, i) => {
            s.style.color = i <= index ? "#ffc107" : "#ddd"
          })
        })
      })

      starRating.addEventListener("mouseleave", () => {
        const currentRating = Number.parseInt(ratingInput.value) || 0
        stars.forEach((s, i) => {
          s.style.color = i < currentRating ? "#ffc107" : "#ddd"
        })
      })
    }
  }

  setupScrollToTop() {
    const scrollBtn = document.getElementById("scrollToTop")

    if (scrollBtn) {
      window.addEventListener("scroll", () => {
        if (window.pageYOffset > 300) {
          scrollBtn.classList.add("visible")
        } else {
          scrollBtn.classList.remove("visible")
        }
      })

      scrollBtn.addEventListener("click", () => {
        window.scrollTo({
          top: 0,
          behavior: "smooth",
        })
      })
    }
  }

  // Share functionality
  openShareModal() {
    const modal = document.getElementById("shareModal")
    if (modal) {
      modal.classList.add("show")
      document.body.style.overflow = "hidden"
    }
  }

  closeShareModal() {
    const modal = document.getElementById("shareModal")
    if (modal) {
      modal.classList.remove("show")
      document.body.style.overflow = ""
    }
  }

  shareRecipe(platform) {
    const url = encodeURIComponent(window.location.href)
    const title = encodeURIComponent(document.title)
    const description = encodeURIComponent(document.querySelector('meta[name="description"]')?.content || "")
    const image = encodeURIComponent(document.querySelector('meta[property="og:image"]')?.content || "")

    let shareUrl = ""

    switch (platform) {
      case "facebook":
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`
        break
      case "twitter":
        shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`
        break
      case "pinterest":
        shareUrl = `https://pinterest.com/pin/create/button/?url=${url}&media=${image}&description=${title}`
        break
      case "whatsapp":
        shareUrl = `https://wa.me/?text=${title}%20${url}`
        break
    }

    if (shareUrl) {
      window.open(shareUrl, "_blank", "width=600,height=400")
    }
  }

  async copyRecipeLink() {
    const shareUrl = document.getElementById("shareUrl")
    const copyBtn = document.getElementById("copyLink")

    try {
      await navigator.clipboard.writeText(shareUrl.value)
      copyBtn.textContent = "Copied!"
      copyBtn.style.background = "#28a745"

      setTimeout(() => {
        copyBtn.textContent = "Copy"
        copyBtn.style.background = ""
      }, 2000)
    } catch (err) {
      // Fallback for older browsers
      shareUrl.select()
      document.execCommand("copy")
      copyBtn.textContent = "Copied!"
    }
  }

  // Ingredient and instruction tracking
  toggleIngredient(checkbox) {
    const ingredientId = checkbox.id
    const isChecked = checkbox.checked

    // Save to localStorage
    const checkedIngredients = JSON.parse(localStorage.getItem("checkedIngredients") || "{}")
    const recipeId = this.getRecipeId()

    if (!checkedIngredients[recipeId]) {
      checkedIngredients[recipeId] = []
    }

    if (isChecked) {
      if (!checkedIngredients[recipeId].includes(ingredientId)) {
        checkedIngredients[recipeId].push(ingredientId)
      }
    } else {
      checkedIngredients[recipeId] = checkedIngredients[recipeId].filter((id) => id !== ingredientId)
    }

    localStorage.setItem("checkedIngredients", JSON.stringify(checkedIngredients))
  }

  toggleInstruction(checkbox) {
    const instructionId = checkbox.id
    const isChecked = checkbox.checked
    const instructionItem = checkbox.closest(".instruction-item")

    // Toggle completed class
    instructionItem.classList.toggle("completed", isChecked)

    // Save to localStorage
    const completedSteps = JSON.parse(localStorage.getItem("completedSteps") || "{}")
    const recipeId = this.getRecipeId()

    if (!completedSteps[recipeId]) {
      completedSteps[recipeId] = []
    }

    if (isChecked) {
      if (!completedSteps[recipeId].includes(instructionId)) {
        completedSteps[recipeId].push(instructionId)
      }
    } else {
      completedSteps[recipeId] = completedSteps[recipeId].filter((id) => id !== instructionId)
    }

    localStorage.setItem("completedSteps", JSON.stringify(completedSteps))
  }

  // Timer functionality
  toggleTimer() {
    const timerDiv = document.getElementById("cookingTimer")
    if (timerDiv) {
      timerDiv.style.display = timerDiv.style.display === "none" ? "block" : "none"
    }
  }

  startTimer() {
    if (!this.isTimerRunning) {
      this.isTimerRunning = true
      this.timer = setInterval(() => {
        this.timerSeconds++
        this.updateTimerDisplay()
      }, 1000)
    }
  }

  pauseTimer() {
    if (this.isTimerRunning) {
      this.isTimerRunning = false
      clearInterval(this.timer)
    }
  }

  resetTimer() {
    this.isTimerRunning = false
    clearInterval(this.timer)
    this.timerSeconds = 0
    this.updateTimerDisplay()
  }

  updateTimerDisplay() {
    const display = document.getElementById("timerDisplay")
    if (display) {
      const minutes = Math.floor(this.timerSeconds / 60)
      const seconds = this.timerSeconds % 60
      display.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
    }
  }

  // Save recipe
  async saveRecipe() {
    const recipeId = this.getRecipeId()
    const saveBtn = document.getElementById("saveBtn")

    try {
      const response = await fetch(`/api/recipes/${recipeId}/save/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": this.getCSRFToken(),
          "Content-Type": "application/json",
        },
      })

      if (response.ok) {
        const data = await response.json()
        saveBtn.innerHTML = data.saved
          ? '<i class="fas fa-bookmark"></i> Saved'
          : '<i class="fas fa-bookmark"></i> Save'

        this.showNotification(data.saved ? "Recipe saved!" : "Recipe removed from saved")
      }
    } catch (error) {
      console.error("Error saving recipe:", error)
      this.showNotification("Error saving recipe", "error")
    }
  }

  // Fullscreen image
  toggleFullscreenImage() {
    const image = document.getElementById("recipeImage")
    if (image) {
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        image.requestFullscreen()
      }
    }
  }

  // Review submission
  async submitReview(e) {
    e.preventDefault()
    const form = e.target
    const formData = new FormData(form)

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": this.getCSRFToken(),
        },
      })

      if (response.ok) {
        this.showNotification("Review submitted successfully!")
        form.reset()
        document.getElementById("ratingInput").value = ""
        document.querySelectorAll("#starRating i").forEach((star) => {
          star.classList.remove("active")
        })

        // Reload reviews section
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        this.showNotification("Error submitting review", "error")
      }
    } catch (error) {
      console.error("Error submitting review:", error)
      this.showNotification("Error submitting review", "error")
    }
  }

  // Utility functions
  loadSavedProgress() {
    const recipeId = this.getRecipeId()

    // Load checked ingredients
    const checkedIngredients = JSON.parse(localStorage.getItem("checkedIngredients") || "{}")
    if (checkedIngredients[recipeId]) {
      checkedIngredients[recipeId].forEach((ingredientId) => {
        const checkbox = document.getElementById(ingredientId)
        if (checkbox) {
          checkbox.checked = true
        }
      })
    }

    // Load completed steps
    const completedSteps = JSON.parse(localStorage.getItem("completedSteps") || "{}")
    if (completedSteps[recipeId]) {
      completedSteps[recipeId].forEach((stepId) => {
        const checkbox = document.getElementById(stepId)
        if (checkbox) {
          checkbox.checked = true
          const instructionItem = checkbox.closest(".instruction-item")
          if (instructionItem) {
            instructionItem.classList.add("completed")
          }
        }
      })
    }
  }

  getRecipeId() {
    return window.location.pathname.split("/").filter(Boolean).pop()
  }

  getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value || ""
  }

  showNotification(message, type = "success") {
    const notification = document.createElement("div")
    notification.className = `notification notification-${type}`
    notification.textContent = message

    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === "error" ? "#dc3545" : "#28a745"};
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 3000;
            animation: slideIn 0.3s ease;
        `

    document.body.appendChild(notification)

    setTimeout(() => {
      notification.remove()
    }, 3000)
  }
}

// Initialize when DOM is loaded
let recipeDetail
document.addEventListener("DOMContentLoaded", () => {
  recipeDetail = new RecipeDetail()
})

// Add CSS animation for notifications
const style = document.createElement("style")
style.textContent = `
    @keyframes slideIn {
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
