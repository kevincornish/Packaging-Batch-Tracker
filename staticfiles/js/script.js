document.addEventListener("DOMContentLoaded", function () {
  var prodCheckElements = document.querySelectorAll(".prod-check-status");
  prodCheckElements.forEach(function (elem) {
    if (elem.textContent === "Error") {
      elem.classList.add("text-danger");
    }
  });
});
