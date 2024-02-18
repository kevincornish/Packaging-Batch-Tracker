;(function () {
    const modal = new bootstrap.Modal(document.getElementById("modal"))
  
    htmx.on("htmx:afterSwap", (e) => {
      if (e.detail.target.id == "dialog") {
        modal.show()
      }
    })
  
    htmx.on("htmx:beforeSwap", (e) => {
      if (e.detail.target.id == "dialog" && !e.detail.xhr.response) {
        modal.hide()
        window.location.reload()
        e.detail.shouldSwap = false
      }
    })
  
    htmx.on("hidden.bs.modal", () => {
      document.getElementById("dialog").innerHTML = ""
    })
  })()
  
  ;(function () {
  const toastElement = document.getElementById("toast")
  const toastBody = document.getElementById("toast-body")
  const toast = new bootstrap.Toast(toastElement, { delay: 2000 })

  htmx.on("showMessage", (e) => {
    toastBody.innerText = e.detail.value
    toast.show()
  })
})()
