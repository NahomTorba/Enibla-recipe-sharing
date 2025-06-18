document.addEventListener("DOMContentLoaded", () => {
    // Image upload functionality
    const imagePreview = document.getElementById("imagePreview")
    const recipeImage = document.getElementById("recipeImage")
    const recipeImagePreview = document.getElementById("recipeImagePreview")
    const changeImageBtn = document.getElementById("changeImageBtn")
    const removeImageBtn = document.getElementById("removeImageBtn")
    const uploadOverlayBtn = document.getElementById("uploadOverlayBtn")
  
    // Character counter for description
    const descriptionTextarea = document.getElementById("description")
    const descCharCount = document.getElementById("descCharCount")
  
    // Tags functionality
    const tagCheckboxes = document.querySelectorAll('input[name="tags"]')
    const selectedTagsDiv = document.getElementById("selectedTags")
    const tagsList = document.getElementById("tagsList")
  
    // Form submission
    const form = document.getElementById("recipeForm")
    const submitBtn = document.getElementById("submitBtn")
  
    // Image upload handlers
    function handleImageUpload() {
      recipeImage.click()
    }
  
    changeImageBtn.addEventListener("click", handleImageUpload)
    uploadOverlayBtn.addEventListener("click", handleImageUpload)
    imagePreview.addEventListener("click", (e) => {
      if (!imagePreview.classList.contains("has-image")) {
        handleImageUpload()
      }
    })
  
    recipeImage.addEventListener("change", (e) => {
      const file = e.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          recipeImagePreview.src = e.target.result
          recipeImagePreview.style.display = "block"
          imagePreview.classList.add("has-image")
  
          // Hide the preview text and icon
          const previewIcon = imagePreview.querySelector(".preview-icon")
          const previewText = imagePreview.querySelector(".preview-text")
          if (previewIcon) previewIcon.style.display = "none"
          if (previewText) previewText.style.display = "none"
  
          // Update button text and show remove button
          changeImageBtn.textContent = "Change Photo"
          removeImageBtn.style.display = "inline-flex"
        }
        reader.readAsDataURL(file)
      }
    })
  
    removeImageBtn.addEventListener("click", () => {
      recipeImage.value = ""
      recipeImagePreview.style.display = "none"
      imagePreview.classList.remove("has-image")
  
      // Show the preview text and icon
      const previewIcon = imagePreview.querySelector(".preview-icon")
      const previewText = imagePreview.querySelector(".preview-text")
      if (previewIcon) previewIcon.style.display = "block"
      if (previewText) previewText.style.display = "block"
  
      // Update button text and hide remove button
      changeImageBtn.textContent = "Upload Photo"
      removeImageBtn.style.display = "none"
    })
  
    // Character counter for description
    function updateCharCount() {
      const count = descriptionTextarea.value.length
      descCharCount.textContent = count
  
      if (count > 450) {
        descCharCount.style.color = "#ef4444"
      } else if (count > 400) {
        descCharCount.style.color = "#f59e0b"
      } else {
        descCharCount.style.color = "#6b7280"
      }
    }
  
    descriptionTextarea.addEventListener("input", updateCharCount)
  
    // Tags functionality
    function updateSelectedTags() {
      const selectedTags = Array.from(tagCheckboxes)
        .filter((checkbox) => checkbox.checked)
        .map((checkbox) => {
          const label = document.querySelector(`label[for="${checkbox.id}"]`)
          return label.textContent.trim()
        })
  
      if (selectedTags.length > 0) {
        selectedTagsDiv.style.display = "block"
        tagsList.innerHTML = selectedTags
          .map(
            (tag) => `
                  <span class="selected-tag">
                      <i class="fas fa-tag"></i>
                      ${tag}
                  </span>
              `,
          )
          .join("")
      } else {
        selectedTagsDiv.style.display = "none"
      }
    }
  
    tagCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener("change", updateSelectedTags)
    })
  
    // Form submission with loading state
    form.addEventListener("submit", (e) => {
      // Add loading state
      submitBtn.classList.add("loading")
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving Changes...'
      submitBtn.disabled = true
  
      // Basic validation
      const title = document.getElementById("title").value.trim()
      const description = document.getElementById("description").value.trim()
      const ingredients = document.getElementById("ingredients").value.trim()
      const instructions = document.getElementById("instructions").value.trim()
  
      if (!title || !description || !ingredients || !instructions) {
        e.preventDefault()
        alert("Please fill in all required fields.")
  
        // Remove loading state
        submitBtn.classList.remove("loading")
        submitBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes'
        submitBtn.disabled = false
        return
      }
  
      // Show success message
      const successMessage = document.createElement("div")
      successMessage.className = "alert alert-info"
      successMessage.innerHTML = '<i class="fas fa-info-circle"></i> Saving your recipe changes...'
      form.insertBefore(successMessage, form.firstChild)
    })
  
    // Auto-resize textareas
    function autoResize(textarea) {
      textarea.style.height = "auto"
      textarea.style.height = textarea.scrollHeight + "px"
    }
  
    const textareas = document.querySelectorAll("textarea")
    textareas.forEach((textarea) => {
      // Initial resize
      autoResize(textarea)
  
      // Resize on input
      textarea.addEventListener("input", function () {
        autoResize(this)
      })
    })
  
    // Warn user about unsaved changes
    let formChanged = false
    const formInputs = form.querySelectorAll("input, textarea")
  
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
  
    form.addEventListener("submit", () => {
      form.submitted = true
    })
  
    // Initialize character count
    updateCharCount()
  })
  