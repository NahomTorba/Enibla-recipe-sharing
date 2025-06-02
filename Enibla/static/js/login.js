document.addEventListener("DOMContentLoaded", () => {
  // Form elements
  const loginForm = document.getElementById("loginForm")
  const submitBtn = document.getElementById("submitBtn")
  const usernameInput = document.getElementById("username")
  const passwordInput = document.getElementById("password")
  const togglePassword = document.getElementById("togglePassword")

  // Password toggle functionality
  function togglePasswordVisibility() {
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password"
    passwordInput.setAttribute("type", type)

    const icon = togglePassword.querySelector("i")
    if (type === "password") {
      icon.classList.remove("fa-eye-slash")
      icon.classList.add("fa-eye")
    } else {
      icon.classList.remove("fa-eye")
      icon.classList.add("fa-eye-slash")
    }
  }

  // Form validation
  function validateForm() {
    let isValid = true

    // Username validation
    if (!usernameInput.value.trim()) {
      usernameInput.classList.add("error")
      isValid = false
    } else {
      usernameInput.classList.remove("error")
    }

    // Password validation
    if (!passwordInput.value) {
      passwordInput.classList.add("error")
      isValid = false
    } else {
      passwordInput.classList.remove("error")
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
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging In...'
    submitBtn.classList.add("loading")
  }

  // Event listeners
  if (togglePassword) {
    togglePassword.addEventListener("click", togglePasswordVisibility)
  }

  if (loginForm) {
    loginForm.addEventListener("submit", handleFormSubmit)
  }

  // Input validation on blur
  if (usernameInput) {
    usernameInput.addEventListener("blur", () => {
      if (!usernameInput.value.trim()) {
        usernameInput.classList.add("error")
      } else {
        usernameInput.classList.remove("error")
      }
    })
  }

  if (passwordInput) {
    passwordInput.addEventListener("blur", () => {
      if (!passwordInput.value) {
        passwordInput.classList.add("error")
      } else {
        passwordInput.classList.remove("error")
      }
    })
  }

  // Clear error state on input
  if (usernameInput) {
    usernameInput.addEventListener("input", () => {
      usernameInput.classList.remove("error")
    })
  }

  if (passwordInput) {
    passwordInput.addEventListener("input", () => {
      passwordInput.classList.remove("error")
    })
  }
})
