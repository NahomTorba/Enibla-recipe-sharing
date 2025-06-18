document.addEventListener("DOMContentLoaded", () => {
  // Form elements
  const editProfileForm = document.getElementById("editProfileForm")
  const submitBtn = document.getElementById("submitBtn")
  const saveIndicator = document.getElementById("saveIndicator")

  // Profile picture elements
  const profileImageInput = document.getElementById("profileImage")
  const profileImagePreview = document.getElementById("profileImagePreview")
  const avatarPreview = document.getElementById("avatarPreview")
  const uploadBtn = document.getElementById("uploadBtn")
  const changePhotoBtn = document.getElementById("changePhotoBtn")
  const removePhotoBtn = document.getElementById("removePhotoBtn")
  const removeImageCheckbox = document.getElementById("removeImageCheckbox")
  const avatarInitial = document.getElementById("avatarInitial")
  const avatarIcon = document.getElementById("avatarIcon")

  // Form inputs
  const firstNameInput = document.getElementById("first_name")
  const lastNameInput = document.getElementById("last_name")
  const usernameInput = document.getElementById("username")
  const emailInput = document.getElementById("email")
  const bioTextarea = document.getElementById("bio")
  const charCount = document.getElementById("charCount")

  // Cuisine selection
  const cuisineCheckboxes = document.querySelectorAll('input[name="favorite_cuisines"]')
  const selectedCuisinesDiv = document.getElementById("selectedCuisines")
  const cuisineTags = document.getElementById("cuisineTags")

  // Preview elements
  const previewImage = document.getElementById("previewImage")
  const previewAvatar = document.getElementById("previewAvatar")
  const previewInitial = document.getElementById("previewInitial")
  const previewName = document.getElementById("previewName")
  const previewUsername = document.getElementById("previewUsername")
  const previewBio = document.getElementById("previewBio")
  const previewCuisines = document.getElementById("previewCuisines")

  // Profile picture upload handlers
  function handleFileUpload() {
    profileImageInput.click()
  }

  function handleFileChange(event) {
    const file = event.target.files[0]
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert("File size must be less than 5MB")
        return
      }

      // Validate file type
      if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file")
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        profileImagePreview.src = e.target.result
        profileImagePreview.style.display = "block"

        // Hide initial/icon
        if (avatarInitial) avatarInitial.style.display = "none"
        if (avatarIcon) avatarIcon.style.display = "none"

        // Update button text and show remove button
        changePhotoBtn.textContent = "Change Photo"
        if (removePhotoBtn) {
          removePhotoBtn.style.display = "inline-flex"
        }

        // Uncheck remove image checkbox
        if (removeImageCheckbox) {
          removeImageCheckbox.checked = false
        }

        // Update preview
        updatePreviewImage(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  function removeProfileImage() {
    profileImageInput.value = ""
    profileImagePreview.style.display = "none"
    profileImagePreview.src = ""

    // Show initial/icon
    if (avatarInitial) avatarInitial.style.display = "block"
    if (avatarIcon) avatarIcon.style.display = "block"

    // Update button text and hide remove button
    changePhotoBtn.textContent = "Upload Photo"
    if (removePhotoBtn) {
      removePhotoBtn.style.display = "none"
    }

    // Check remove image checkbox if it exists
    if (removeImageCheckbox) {
      removeImageCheckbox.checked = true
    }

    // Update preview
    updatePreviewAvatar()
  }

  function updateAvatarInitial() {
    const firstName = firstNameInput.value.trim()
    if (firstName && avatarInitial) {
      avatarInitial.textContent = firstName.charAt(0).toUpperCase()
    }
    if (firstName && previewInitial) {
      previewInitial.textContent = firstName.charAt(0).toUpperCase()
    }
  }

  // Bio character counter
  function updateCharCount() {
    const count = bioTextarea.value.length
    charCount.textContent = count

    if (count > 450) {
      charCount.style.color = "#dc2626"
    } else if (count > 400) {
      charCount.style.color = "#f59e0b"
    } else {
      charCount.style.color = "#6b7280"
    }

    // Update preview
    if (previewBio) {
      previewBio.textContent = bioTextarea.value || "No bio provided"
    }
  }

  // Cuisine selection handler
  function updateSelectedCuisines() {
    const selected = Array.from(cuisineCheckboxes)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value)

    if (selected.length > 0) {
      selectedCuisinesDiv.style.display = "block"
      cuisineTags.innerHTML = selected.map((cuisine) => `<span class="cuisine-tag">${cuisine}</span>`).join("")

      // Update preview
      if (previewCuisines) {
        previewCuisines.innerHTML = selected
          .map((cuisine) => `<span class="preview-cuisine-tag">${cuisine}</span>`)
          .join("")
      }
    } else {
      selectedCuisinesDiv.style.display = "none"
      if (previewCuisines) {
        previewCuisines.innerHTML = ""
      }
    }
  }

  // Preview update functions
  function updatePreviewImage(src) {
    if (previewImage) {
      previewImage.src = src
      previewImage.style.display = "block"
    }
    if (previewAvatar) {
      previewAvatar.style.display = "none"
    }
  }

  function updatePreviewAvatar() {
    if (previewImage) {
      previewImage.style.display = "none"
    }
    if (previewAvatar) {
      previewAvatar.style.display = "flex"
    }
  }

  function updatePreviewName() {
    const firstName = firstNameInput.value.trim()
    const lastName = lastNameInput.value.trim()
    const fullName = [firstName, lastName].filter(Boolean).join(" ")

    if (previewName) {
      previewName.textContent = fullName || usernameInput.value || "Your Name"
    }
  }

  function updatePreviewUsername() {
    if (previewUsername) {
      previewUsername.textContent = `@${usernameInput.value || "username"}`
    }
  }

  // Form validation
  function validateForm() {
    let isValid = true
    const errors = []

    // Validate required fields
    if (!firstNameInput.value.trim()) {
      errors.push("First name is required")
      isValid = false
    }

    if (!lastNameInput.value.trim()) {
      errors.push("Last name is required")
      isValid = false
    }

    if (!usernameInput.value.trim()) {
      errors.push("Username is required")
      isValid = false
    }

    if (!emailInput.value.trim()) {
      errors.push("Email is required")
      isValid = false
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (emailInput.value && !emailRegex.test(emailInput.value)) {
      errors.push("Please enter a valid email address")
      isValid = false
    }

    // Validate username format
    const usernameRegex = /^[a-zA-Z0-9_]+$/
    if (usernameInput.value && !usernameRegex.test(usernameInput.value)) {
      errors.push("Username can only contain letters, numbers, and underscores")
      isValid = false
    }

    if (!isValid) {
      alert("Please fix the following errors:\n" + errors.join("\n"))
    }

    return isValid
  }

  // Form submission handler
  function handleFormSubmit(event) {
    event.preventDefault()

    if (!validateForm()) {
      return
    }

    // Show loading state
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving Changes...'
    submitBtn.classList.add("loading")

    // Simulate form submission delay
    setTimeout(() => {
      // Actually submit the form
      editProfileForm.submit()
    }, 1000)
  }

  // Auto-save functionality (optional)
  let autoSaveTimeout
  function autoSave() {
    clearTimeout(autoSaveTimeout)
    autoSaveTimeout = setTimeout(() => {
      // Show save indicator
      saveIndicator.classList.add("show")
      setTimeout(() => {
        saveIndicator.classList.remove("show")
      }, 3000)
    }, 2000)
  }

  // Event listeners
  if (uploadBtn) uploadBtn.addEventListener("click", handleFileUpload)
  if (changePhotoBtn) changePhotoBtn.addEventListener("click", handleFileUpload)
  if (removePhotoBtn) removePhotoBtn.addEventListener("click", removeProfileImage)
  if (profileImageInput) profileImageInput.addEventListener("change", handleFileChange)

  if (firstNameInput) {
    firstNameInput.addEventListener("input", () => {
      updateAvatarInitial()
      updatePreviewName()
      autoSave()
    })
  }

  if (lastNameInput) {
    lastNameInput.addEventListener("input", () => {
      updatePreviewName()
      autoSave()
    })
  }

  if (usernameInput) {
    usernameInput.addEventListener("input", () => {
      updatePreviewUsername()
      autoSave()
    })
  }

  if (emailInput) {
    emailInput.addEventListener("input", autoSave)
  }

  if (bioTextarea) {
    bioTextarea.addEventListener("input", () => {
      updateCharCount()
      autoSave()
    })
  }

  cuisineCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      updateSelectedCuisines()
      autoSave()
    })
  })

  if (editProfileForm) {
    editProfileForm.addEventListener("submit", handleFormSubmit)
  }

  // Initialize with existing data
  function initializeForm() {
    updateCharCount()
    updateSelectedCuisines()
    updateAvatarInitial()
    updatePreviewName()
    updatePreviewUsername()

    // Initialize bio preview
    if (bioTextarea && previewBio) {
      const bioText = bioTextarea.value.trim()
      if (bioText) {
        previewBio.textContent = bioText
        previewBio.parentElement.style.display = "block"
      } else {
        previewBio.textContent = "No bio provided"
        previewBio.parentElement.style.display = "none"
      }
    }

    // Initialize cuisine preview
    updateSelectedCuisines()

    // Set initial form state
    hasUnsavedChanges = false
  }

  // Initialize profile image state
  function initializeProfileImage() {
    const hasExistingImage =
      profileImagePreview && profileImagePreview.src && profileImagePreview.style.display !== "none"

    if (hasExistingImage) {
      changePhotoBtn.textContent = "Change Photo"
      if (removePhotoBtn) {
        removePhotoBtn.style.display = "inline-flex"
      }
      if (avatarInitial) avatarInitial.style.display = "none"
      if (avatarIcon) avatarIcon.style.display = "none"
    } else {
      changePhotoBtn.textContent = "Upload Photo"
      if (removePhotoBtn) {
        removePhotoBtn.style.display = "none"
      }
    }
  }

  // Initialize form with existing data
  initializeForm()
  initializeProfileImage()

  // Smooth scrolling for form navigation
  const cards = document.querySelectorAll(".card")
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`
  })

  // Enhanced form interactions
  const formInputs = document.querySelectorAll("input, textarea")
  formInputs.forEach((input) => {
    input.addEventListener("focus", () => {
      input.parentElement.classList.add("focused")
    })

    input.addEventListener("blur", () => {
      input.parentElement.classList.remove("focused")
    })
  })

  // Cuisine selection enhancements
  cuisineCheckboxes.forEach((checkbox) => {
    const label = checkbox.nextElementSibling
    if (label) {
      label.addEventListener("mouseenter", () => {
        if (!checkbox.checked) {
          label.style.transform = "translateY(-2px)"
        }
      })

      label.addEventListener("mouseleave", () => {
        if (!checkbox.checked) {
          label.style.transform = "translateY(0)"
        }
      })
    }
  })

  // Keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    // Ctrl/Cmd + S to save
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault()
      if (editProfileForm) {
        editProfileForm.dispatchEvent(new Event("submit"))
      }
    }

    // Escape to cancel (go back to profile)
    if (e.key === "Escape") {
      const cancelBtn = document.querySelector('a[href*="my_profile"]')
      if (cancelBtn) {
        window.location.href = cancelBtn.href
      }
    }
  })

  // Unsaved changes warning
  let hasUnsavedChanges = false
  const originalFormData = new FormData(editProfileForm)

  formInputs.forEach((input) => {
    input.addEventListener("input", () => {
      hasUnsavedChanges = true
    })
  })

  window.addEventListener("beforeunload", (e) => {
    if (hasUnsavedChanges) {
      e.preventDefault()
      e.returnValue = "You have unsaved changes. Are you sure you want to leave?"
    }
  })

  // Mark as saved when form is submitted
  editProfileForm.addEventListener("submit", () => {
    hasUnsavedChanges = false
  })
})
