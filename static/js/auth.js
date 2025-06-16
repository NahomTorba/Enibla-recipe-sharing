document.addEventListener("DOMContentLoaded", () => {
  // Form elements
  const signupForm = document.getElementById("signupForm")
  const submitBtn = document.getElementById("submitBtn")

  // Password elements
  const password1 = document.getElementById("password1")
  const password2 = document.getElementById("password2")
  const togglePassword1 = document.getElementById("togglePassword1")
  const togglePassword2 = document.getElementById("togglePassword2")
  const strengthFill = document.getElementById("strengthFill")
  const strengthText = document.getElementById("strengthText")
  const passwordMatch = document.getElementById("passwordMatch")

  // Form validation
  const firstNameInput = document.getElementById("first_name")
  const lastNameInput = document.getElementById("last_name")
  const usernameInput = document.getElementById("username")
  const emailInput = document.getElementById("email")
  const termsCheckbox = document.getElementById("terms")

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

    if (password.length >= 8) score++
    if (password.match(/[a-z]/)) score++
    if (password.match(/[A-Z]/)) score++
    if (password.match(/[0-9]/)) score++
    if (password.match(/[^a-zA-Z0-9]/)) score++

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

  // Real-time validation
  function validateField(input, validationFn) {
    const isValid = validationFn(input.value)
    if (isValid) {
      input.classList.remove("error")
      input.classList.add("success")
    } else {
      input.classList.remove("success")
      input.classList.add("error")
    }
    return isValid
  }

  // Validation functions
  const validations = {
    firstName: (value) => value.trim().length >= 2,
    lastName: (value) => value.trim().length >= 2,
    username: (value) => value.trim().length >= 3 && /^[a-zA-Z0-9_]+$/.test(value),
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    password: (value) => value.length >= 8,
    passwordMatch: () => password1.value === password2.value && password2.value.length > 0,
  }

  // Form submission
  function handleFormSubmit(event) {
    event.preventDefault()

    // Validate all fields
    const isFirstNameValid = validateField(firstNameInput, validations.firstName)
    const isLastNameValid = validateField(lastNameInput, validations.lastName)
    const isUsernameValid = validateField(usernameInput, validations.username)
    const isEmailValid = validateField(emailInput, validations.email)
    const isPasswordValid = validateField(password1, validations.password)
    const isPasswordMatchValid = validateField(password2, validations.passwordMatch)
    const isTermsAccepted = termsCheckbox.checked

    if (!isTermsAccepted) {
      alert("Please accept the Terms of Service and Privacy Policy to continue.")
      return
    }

    if (
      !isFirstNameValid ||
      !isLastNameValid ||
      !isUsernameValid ||
      !isEmailValid ||
      !isPasswordValid ||
      !isPasswordMatchValid
    ) {
      alert("Please correct the errors in the form before submitting.")
      return
    }

    // Show loading state
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...'
    submitBtn.classList.add("loading")

    // Submit the form
    setTimeout(() => {
      signupForm.submit()
    }, 1000)
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
      validateField(password1, validations.password)
      if (password2.value) {
        checkPasswordMatch()
      }
    })
  }

  if (password2) {
    password2.addEventListener("input", () => {
      checkPasswordMatch()
      validateField(password2, validations.passwordMatch)
    })
  }

  // Real-time validation for other fields
  if (firstNameInput) {
    firstNameInput.addEventListener("blur", () => {
      validateField(firstNameInput, validations.firstName)
    })
  }

  if (lastNameInput) {
    lastNameInput.addEventListener("blur", () => {
      validateField(lastNameInput, validations.lastName)
    })
  }

  if (usernameInput) {
    usernameInput.addEventListener("blur", () => {
      validateField(usernameInput, validations.username)
    })
  }

  if (emailInput) {
    emailInput.addEventListener("blur", () => {
      validateField(emailInput, validations.email)
    })
  }

  if (signupForm) {
    signupForm.addEventListener("submit", handleFormSubmit)
  }

  // Initialize password strength
  if (password1) {
    checkPasswordStrength(password1.value)
  }
})
