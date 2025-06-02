document.addEventListener("DOMContentLoaded", () => {
  const passwordResetConfirmForm = document.getElementById("passwordResetConfirmForm")
  const submitBtn = document.getElementById("submitBtn")
  const password1 = document.getElementById("new_password1")
  const password2 = document.getElementById("new_password2")
  const togglePassword1 = document.getElementById("togglePassword1")
  const togglePassword2 = document.getElementById("togglePassword2")
  const strengthFill = document.getElementById("strengthFill")
  const strengthText = document.getElementById("strengthText")
  const passwordMatch = document.getElementById("passwordMatch")

  // Password requirements elements
  const reqLength = document.getElementById("req-length")
  const reqLowercase = document.getElementById("req-lowercase")
  const reqUppercase = document.getElementById("req-uppercase")
  const reqNumber = document.getElementById("req-number")
  const reqSpecial = document.getElementById("req-special")

  // Password toggle functionality
  function togglePasswordVisibility(passwordInput, toggleButton) {
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password"
    passwordInput.setAttribute("type", type)

    const icon = toggleButton.querySelector("i")
    if (type === "password") {
      icon.classList.remove("fa-eye-slash")
      icon.classList.add("fa-eye")
    } else {
      icon.classList.remove("fa-eye")
      icon.classList.add("fa-eye-slash")
    }
  }

  // Password strength checker
  function checkPasswordStrength(password) {
    let score = 0
    let feedback = "Password strength"

    // Check requirements
    const hasLength = password.length >= 8
    const hasLowercase = /[a-z]/.test(password)
    const hasUppercase = /[A-Z]/.test(password)
    const hasNumber = /[0-9]/.test(password)
    const hasSpecial = /[^a-zA-Z0-9]/.test(password)

    // Update requirement indicators
    updateRequirement(reqLength, hasLength)
    updateRequirement(reqLowercase, hasLowercase)
    updateRequirement(reqUppercase, hasUppercase)
    updateRequirement(reqNumber, hasNumber)
    updateRequirement(reqSpecial, hasSpecial)

    // Calculate score
    if (hasLength) score++
    if (hasLowercase) score++
    if (hasUppercase) score++
    if (hasNumber) score++
    if (hasSpecial) score++

    // Remove all strength classes
    strengthFill.className = "strength-fill"
    strengthText.className = "strength-text"

    if (password.length === 0) {
      feedback = "Password strength"
    } else if (score <= 2) {
      strengthFill.classList.add("weak")
      strengthText.classList.add("weak")
      feedback = "Weak password"
    } else if (score === 3) {
      strengthFill.classList.add("fair")
      strengthText.classList.add("fair")
      feedback = "Fair password"
    } else if (score === 4) {
      strengthFill.classList.add("good")
      strengthText.classList.add("good")
      feedback = "Good password"
    } else if (score === 5) {
      strengthFill.classList.add("strong")
      strengthText.classList.add("strong")
      feedback = "Strong password"
    }

    strengthText.textContent = feedback
    return score
  }

  // Update requirement indicator
  function updateRequirement(element, isValid) {
    const icon = element.querySelector("i")
    if (isValid) {
      element.classList.add("valid")
      icon.className = "fas fa-check"
    } else {
      element.classList.remove("valid")
      icon.className = "fas fa-times"
    }
  }

  // Password match checker
  function checkPasswordMatch() {
    const pass1 = password1.value
    const pass2 = password2.value

    if (pass2.length === 0) {
      passwordMatch.style.display = "none"
      return
    }

    passwordMatch.style.display = "flex"

    if (pass1 === pass2) {
      passwordMatch.classList.remove("no-match")
      passwordMatch.querySelector("span").textContent = "Passwords match"
      passwordMatch.querySelector("i").className = "fas fa-check-circle"
    } else {
      passwordMatch.classList.add("no-match")
      passwordMatch.querySelector("span").textContent = "Passwords don't match"
      passwordMatch.querySelector("i").className = "fas fa-times-circle"
    }
  }

  // Form validation
  function validateForm() {
    const pass1 = password1.value
    const pass2 = password2.value
    const strength = checkPasswordStrength(pass1)

    if (strength < 3) {
      alert("Please choose a stronger password that meets all requirements.")
      return false
    }

    if (pass1 !== pass2) {
      alert("Passwords don't match. Please make sure both passwords are identical.")
      return false
    }

    return true
  }

  // Form submission
  function handleFormSubmit(event) {
    if (!validateForm()) {
      event.preventDefault()
      return
    }

    // Show loading state
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resetting Password...'
    submitBtn.classList.add("loading")
  }

  // Event listeners
  if (togglePassword1) {
    togglePassword1.addEventListener("click", () => {
      togglePasswordVisibility(password1, togglePassword1)
    })
  }

  if (togglePassword2) {
    togglePassword2.addEventListener("click", () => {
      togglePasswordVisibility(password2, togglePassword2)
    })
  }

  if (password1) {
    password1.addEventListener("input", (e) => {
      checkPasswordStrength(e.target.value)
      if (password2.value) {
        checkPasswordMatch()
      }
    })
  }

  if (password2) {
    password2.addEventListener("input", () => {
      checkPasswordMatch()
    })
  }

  if (passwordResetConfirmForm) {
    passwordResetConfirmForm.addEventListener("submit", handleFormSubmit)
  }

  // Initialize
  if (password1) {
    checkPasswordStrength(password1.value)
  }
})
