document.addEventListener("DOMContentLoaded", () => {
  // Recipe image upload functionality
  const recipeImageInput = document.getElementById("recipeImage")
  const recipeImagePreview = document.getElementById("recipeImagePreview")
  const imagePreview = document.getElementById("imagePreview")
  const uploadOverlayBtn = document.getElementById("uploadOverlayBtn")
  const changeImageBtn = document.getElementById("changeImageBtn")
  const removeImageBtn = document.getElementById("removeImageBtn")
  const previewIcon = document.querySelector(".preview-icon")
  const previewText = document.querySelector(".preview-text")

  // Character counters
  const descriptionTextarea = document.getElementById("description")
  const descCharCount = document.getElementById("descCharCount")

  // Tag selection
  const tagCheckboxes = document.querySelectorAll('input[name="tags"]')
  const selectedTagsDiv = document.getElementById("selectedTags")
  const tagsList = document.getElementById("tagsList")

  // Form submission
  const recipeForm = document.getElementById("recipeForm")
  const submitBtn = document.getElementById("submitBtn")

  // Recipe image upload handlers
  function handleImageUpload() {
    recipeImageInput.click()
  }

  function handleImageChange(event) {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        recipeImagePreview.src = e.target.result
        recipeImagePreview.style.display = "block"
        imagePreview.classList.add("has-image")

        if (previewIcon) previewIcon.style.display = "none"
        if (previewText) previewText.style.display = "none"

        changeImageBtn.textContent = "Change Photo"
        removeImageBtn.style.display = "inline-flex"
      }
      reader.readAsDataURL(file)
    }
  }

  function removeRecipeImage() {
    recipeImageInput.value = ""
    recipeImagePreview.style.display = "none"
    recipeImagePreview.src = ""
    imagePreview.classList.remove("has-image")

    if (previewIcon) previewIcon.style.display = "block"
    if (previewText) previewText.style.display = "block"

    changeImageBtn.textContent = "Upload Photo"
    removeImageBtn.style.display = "none"
  }

  // Character counter for description
  function updateDescCharCount() {
    const count = descriptionTextarea.value.length
    descCharCount.textContent = count

    if (count > 450) {
      descCharCount.style.color = "#dc2626"
    } else if (count > 400) {
      descCharCount.style.color = "#f59e0b"
    } else {
      descCharCount.style.color = "#6b7280"
    }
  }

  // Tag selection handler
  function updateSelectedTags() {
    const selected = Array.from(tagCheckboxes)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => {
        const label = document.querySelector(`label[for="${checkbox.id}"]`)
        const icon = label.querySelector("i").outerHTML
        const text = label.textContent.trim()
        return { value: checkbox.value, text, icon }
      })

    if (selected.length > 0) {
      selectedTagsDiv.style.display = "block"
      tagsList.innerHTML = selected.map((tag) => `<span class="selected-tag">${tag.icon} ${tag.text}</span>`).join("")
    } else {
      selectedTagsDiv.style.display = "none"
    }
  }

  // Form validation
  function validateForm() {
    const title = document.getElementById("title").value.trim()
    const description = document.getElementById("description").value.trim()
    const ingredients = document.getElementById("ingredients").value.trim()
    const instructions = document.getElementById("instructions").value.trim()

    if (!title || !description || !ingredients || !instructions) {
      alert("Please fill in all required fields.")
      return false
    }

    if (title.length < 3) {
      alert("Recipe title must be at least 3 characters long.")
      return false
    }

    if (description.length < 10) {
      alert("Recipe description must be at least 10 characters long.")
      return false
    }

    return true
  }

  // Form submission handler
  function handleFormSubmit(event) {
    event.preventDefault()

    if (!validateForm()) {
      return
    }

    // Show loading state
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sharing Recipe...'
    submitBtn.classList.add("loading")

    // Simulate form submission delay
    setTimeout(() => {
      // Actually submit the form
      recipeForm.submit()
    }, 1000)
  }

  // Auto-resize textareas
  function autoResizeTextarea(textarea) {
    textarea.style.height = "auto"
    textarea.style.height = textarea.scrollHeight + "px"
  }

  // Event listeners
  imagePreview.addEventListener("click", handleImageUpload)
  uploadOverlayBtn.addEventListener("click", handleImageUpload)
  changeImageBtn.addEventListener("click", handleImageUpload)
  removeImageBtn.addEventListener("click", removeRecipeImage)
  recipeImageInput.addEventListener("change", handleImageChange)

  descriptionTextarea.addEventListener("input", updateDescCharCount)

  tagCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateSelectedTags)
  })

  recipeForm.addEventListener("submit", handleFormSubmit)

  // Auto-resize textareas on input
  const textareas = document.querySelectorAll("textarea")
  textareas.forEach((textarea) => {
    textarea.addEventListener("input", () => autoResizeTextarea(textarea))
    // Initial resize
    autoResizeTextarea(textarea)
  })

  // Initialize
  updateDescCharCount()
  updateSelectedTags()

  // Add smooth scrolling for form navigation
  const cards = document.querySelectorAll(".card")
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`
  })
})
