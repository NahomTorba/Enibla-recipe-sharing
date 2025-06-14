document.addEventListener("DOMContentLoaded", () => {
  // Profile dropdown functionality
  const profileDropdown = document.getElementById("profileDropdown")
  const profileBtn = document.getElementById("profileBtn")
  const dropdownMenu = document.getElementById("dropdownMenu")

  if (profileBtn && dropdownMenu) {
    // Toggle dropdown
    profileBtn.addEventListener("click", (e) => {
      e.stopPropagation()
      profileDropdown.classList.toggle("active")
    })

    // Close dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (!profileDropdown.contains(e.target)) {
        profileDropdown.classList.remove("active")
      }
    })

    // Close dropdown when pressing escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        profileDropdown.classList.remove("active")
      }
    })
  }

  // Mobile menu functionality
  const mobileMenuBtn = document.getElementById("mobileMenuBtn")
  const navLinks = document.querySelector(".nav-links")

  if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener("click", () => {
      navLinks.classList.toggle("active")
    })
  }

  // Search form enhancements
  const searchInputs = document.querySelectorAll(".search-input, .hero-search-container input")

  searchInputs.forEach((input) => {
    // Add search suggestions (placeholder for future enhancement)
    input.addEventListener("focus", () => {
      input.style.transform = "scale(1.02)"
    })

    input.addEventListener("blur", () => {
      input.style.transform = "scale(1)"
    })
  })

  // Smooth scrolling for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]')

  anchorLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault()
      const target = document.querySelector(link.getAttribute("href"))
      if (target) {
        target.scrollIntoView({ behavior: "smooth" })
      }
    })
  })

  // Animation on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1"
        entry.target.style.transform = "translateY(0)"
      }
    })
  }, observerOptions)

  // Observe recipe cards and category cards
  const animatedElements = document.querySelectorAll(".recipe-card, .category-card, .stat-item")

  animatedElements.forEach((el, index) => {
    el.style.opacity = "0"
    el.style.transform = "translateY(20px)"
    el.style.transition = `all 0.6s ease ${index * 0.1}s`
    observer.observe(el)
  })

  // Stats counter animation
  const statNumbers = document.querySelectorAll(".stat-number")

  const countUp = (element, target) => {
    let current = 0
    const increment = target / 100
    const timer = setInterval(() => {
      current += increment
      if (current >= target) {
        current = target
        clearInterval(timer)
      }
      element.textContent = Math.floor(current)
    }, 20)
  }

  const statsObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !entry.target.classList.contains("counted")) {
          const target = Number.parseInt(entry.target.textContent) || 0
          if (target > 0) {
            countUp(entry.target, target)
            entry.target.classList.add("counted")
          }
        }
      })
    },
    { threshold: 0.5 },
  )

  statNumbers.forEach((stat) => {
    statsObserver.observe(stat)
  })

  // Enhanced search functionality
  const searchForms = document.querySelectorAll(".search-form, .hero-search-form")

  searchForms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const input = form.querySelector("input")
      if (!input.value.trim()) {
        e.preventDefault()
        input.focus()
        input.style.borderColor = "#f59e0b"
        setTimeout(() => {
          input.style.borderColor = ""
        }, 2000)
      }
    })
  })

  // Recipe card hover effects
  const recipeCards = document.querySelectorAll(".recipe-card")

  recipeCards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.boxShadow = "0 20px 40px rgba(234, 88, 12, 0.15)"
    })

    card.addEventListener("mouseleave", () => {
      card.style.boxShadow = ""
    })
  })

  // Category card interactions
  const categoryCards = document.querySelectorAll(".category-card")

  categoryCards.forEach((card) => {
    card.addEventListener("click", (e) => {
      // Add visual feedback
      card.style.transform = "scale(0.95)"
      setTimeout(() => {
        card.style.transform = ""
      }, 150)
    })
  })
})
