document.addEventListener("DOMContentLoaded", () => {
  // Profile picture upload functionality
  const profileImageInput = document.getElementById("profileImage")
  const profileImagePreview = document.getElementById("profileImagePreview")
  const avatarPreview = document.getElementById("avatarPreview")
  const uploadBtn = document.getElementById("uploadBtn")
  const changePhotoBtn = document.getElementById("changePhotoBtn")
  const removePhotoBtn = document.getElementById("removePhotoBtn")
  const firstNameInput = document.getElementById("firstName")
  const avatarIcon = document.querySelector(".avatar-icon")

  // Bio character counter
  const bioTextarea = document.getElementById("bio")
  const charCount = document.getElementById("charCount")

  // Cuisine selection
  const cuisineCheckboxes = document.querySelectorAll('input[name="favorite_cuisines"]')
  const selectedCuisinesDiv = document.getElementById("selectedCuisines")
  const cuisineTags = document.getElementById("cuisineTags")

  // Form submission
  const profileForm = document.getElementById("profileForm")
  const submitBtn = document.getElementById("submitBtn")

  // Profile picture upload handlers
  function handleFileUpload() {
    profileImageInput.click()
  }

  function handleFileChange(event) {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        profileImagePreview.src = e.target.result
        profileImagePreview.style.display = "block"
        if (avatarIcon) {
          avatarIcon.style.display = "none"
        }
        changePhotoBtn.textContent = "Change Photo"
        removePhotoBtn.style.display = "inline-flex"
      }
      reader.readAsDataURL(file)
    }
  }

  function removeProfileImage() {
    profileImageInput.value = ""
    profileImagePreview.style.display = "none"
    profileImagePreview.src = ""
    if (avatarIcon) {
      avatarIcon.style.display = "block"
    }
    changePhotoBtn.textContent = "Upload Photo"
    removePhotoBtn.style.display = "none"
    updateAvatarInitial()
  }

  function updateAvatarInitial() {
    const firstName = firstNameInput.value.trim()
    if (firstName && avatarIcon) {
      avatarIcon.textContent = firstName.charAt(0).toUpperCase()
      avatarIcon.className = "avatar-initial"
    } else if (avatarIcon) {
      avatarIcon.innerHTML = '<i class="fas fa-camera"></i>'
      avatarIcon.className = "avatar-icon"
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
  }

  // Cuisine selection handler
  function updateSelectedCuisines() {
    const selected = Array.from(cuisineCheckboxes)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value)

    if (selected.length > 0) {
      selectedCuisinesDiv.style.display = "block"
      cuisineTags.innerHTML = selected.map((cuisine) => `<span class="cuisine-tag">${cuisine}</span>`).join("")
    } else {
      selectedCuisinesDiv.style.display = "none"
    }
  }

  // Form submission handler
  function handleFormSubmit(event) {
    event.preventDefault()

    // Show loading state
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Profile...'
    submitBtn.classList.add("loading")

    // Simulate form submission (replace with actual form submission)
    setTimeout(() => {
      // Reset button state
      submitBtn.disabled = false
      submitBtn.innerHTML = '<i class="fas fa-save"></i> Create Profile'
      submitBtn.classList.remove("loading")

      // Actually submit the form
      profileForm.submit()
    }, 2000)
  }

  // Event listeners
  uploadBtn.addEventListener("click", handleFileUpload)
  changePhotoBtn.addEventListener("click", handleFileUpload)
  removePhotoBtn.addEventListener("click", removeProfileImage)
  profileImageInput.addEventListener("change", handleFileChange)
  firstNameInput.addEventListener("input", updateAvatarInitial)
  bioTextarea.addEventListener("input", updateCharCount)
  cuisineCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateSelectedCuisines)
  })
  profileForm.addEventListener("submit", handleFormSubmit)

  // Initialize
  updateCharCount()
  updateSelectedCuisines()
  updateAvatarInitial()
})
