document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("editRecipeForm")
    const saveBtn = document.getElementById("saveChangesBtn")
    const fileInput = document.querySelector('input[type="file"]')
    const currentImage = document.getElementById("currentImage")
  
    // Form validation
    function validateForm() {
      let isValid = true
      const requiredFields = form.querySelectorAll("[required]")
  
      requiredFields.forEach((field) => {
        const errorDiv = field.parentNode.querySelector(".field-error")
        if (errorDiv) {
          errorDiv.remove()
        }
  
        if (!field.value.trim()) {
          isValid = false
          showFieldError(field, "This field is required.")
        }
      })
  
      return isValid
    }
  
    // Show field error
    function showFieldError(field, message) {
      const errorDiv = document.createElement("div")
      errorDiv.className = "field-error"
      errorDiv.textContent = message
      field.parentNode.appendChild(errorDiv)
    }
  
    // Handle form submission
    form.addEventListener("submit", (e) => {
      // Add loading state to save button
      saveBtn.classList.add("loading")
      saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving Changes...'
  
      // Validate form
      if (!validateForm()) {
        e.preventDefault()
        saveBtn.classList.remove("loading")
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes'
  
        // Show error message
        showAlert("Please fill in all required fields.", "error")
        return
      }
  
      // Show success message (will be replaced by Django messages)
      showAlert("Saving your recipe changes...", "info")
    })
  
    // Handle image preview
    if (fileInput) {
      fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0]
        if (file) {
          const reader = new FileReader()
          reader.onload = (e) => {
            if (currentImage) {
              currentImage.src = e.target.result
            } else {
              // Create new image preview if none exists
              const imageContainer = document.querySelector(".current-image")
              if (!imageContainer) {
                const newImageContainer = document.createElement("div")
                newImageContainer.className = "current-image"
                newImageContainer.innerHTML = `
                                  <img src="${e.target.result}" alt="New recipe image" id="currentImage">
                                  <p class="image-label">New Image Preview</p>
                              `
                document
                  .querySelector(".image-upload-container")
                  .insertBefore(newImageContainer, document.querySelector(".file-input-wrapper"))
              }
            }
          }
          reader.readAsDataURL(file)
        }
      })
    }
  
    // Auto-resize textareas
    const textareas = document.querySelectorAll("textarea")
    textareas.forEach((textarea) => {
      textarea.addEventListener("input", function () {
        this.style.height = "auto"
        this.style.height = this.scrollHeight + "px"
      })
  
      // Initial resize
      textarea.style.height = textarea.scrollHeight + "px"
    })
  
    // Show alert function
    function showAlert(message, type) {
      // Remove existing alerts
      const existingAlerts = document.querySelectorAll(".alert")
      existingAlerts.forEach((alert) => alert.remove())
  
      const alertDiv = document.createElement("div")
      alertDiv.className = `alert alert-${type}`
  
      const icon =
        type === "error"
          ? "fas fa-exclamation-triangle"
          : type === "success"
            ? "fas fa-check-circle"
            : "fas fa-info-circle"
  
      alertDiv.innerHTML = `
              <i class="${icon}"></i>
              <span>${message}</span>
          `
  
      form.insertBefore(alertDiv, form.firstChild)
  
      // Auto-remove after 5 seconds for info messages
      if (type === "info") {
        setTimeout(() => {
          alertDiv.remove()
        }, 5000)
      }
    }
  
    // Confirm navigation away from unsaved changes
    let formChanged = false
    const formInputs = form.querySelectorAll("input, textarea, select")
  
    formInputs.forEach((input) => {
      input.addEventListener("change", () => {
        formChanged = true
      })
    })
  
    window.addEventListener("beforeunload", (e) => {
      if (formChanged && !form.submitted) {
        e.preventDefault()
        e.returnValue = "You have unsaved changes. Are you sure you want to leave?"
        return e.returnValue
      }
    })
  
    // Mark form as submitted when save button is clicked
    form.addEventListener("submit", () => {
      form.submitted = true
    })
  
    // Add smooth scrolling to form errors
    function scrollToFirstError() {
      const firstError = document.querySelector(".field-error")
      if (firstError) {
        firstError.scrollIntoView({
          behavior: "smooth",
          block: "center",
        })
      }
    }
  
    // Character counter for text fields
    const textInputs = document.querySelectorAll('input[type="text"], textarea')
    textInputs.forEach((input) => {
      if (input.hasAttribute("maxlength")) {
        const maxLength = input.getAttribute("maxlength")
        const counter = document.createElement("div")
        counter.className = "char-counter"
        counter.style.cssText = "font-size: 0.8rem; color: #666; text-align: right; margin-top: 5px;"
  
        function updateCounter() {
          const remaining = maxLength - input.value.length
          counter.textContent = `${input.value.length}/${maxLength} characters`
          counter.style.color = remaining < 20 ? "#e74c3c" : "#666"
        }
  
        input.addEventListener("input", updateCounter)
        input.parentNode.appendChild(counter)
        updateCounter()
      }
    })
  })
  