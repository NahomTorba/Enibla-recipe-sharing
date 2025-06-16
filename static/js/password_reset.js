document.addEventListener("DOMContentLoaded", () => {
  const passwordResetForm = document.getElementById("passwordResetForm")
  const submitBtn = document.getElementById("submitBtn")
  const emailInput = document.getElementById("email")

  // Email validation
  function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // Form validation
  function validateForm() {
    let isValid = true

    if (!emailInput.value.trim()) {
      emailInput.classList.add("error")
      isValid = false
    } else if (!validateEmail(emailInput.value)) {
      emailInput.classList.add("error")
      isValid = false
    } else {
      emailInput.classList.remove("error")
    }

    return isValid
  }

  // Form submission
  function handleFormSubmit(event) {
    if (!validateForm()) {
      event.preventDefault()
      return
    }

    // Show loading state
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...'
    submitBtn.classList.add("loading")
  }

  // Event listeners
  if (passwordResetForm) {
    passwordResetForm.addEventListener("submit", handleFormSubmit)
  }

  if (emailInput) {
    emailInput.addEventListener("blur", () => {
      if (!emailInput.value.trim() || !validateEmail(emailInput.value)) {
        emailInput.classList.add("error")
      } else {
        emailInput.classList.remove("error")
      }
    })

    emailInput.addEventListener("input", () => {
      emailInput.classList.remove("error")
    })
  }
})
