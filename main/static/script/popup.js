document.addEventListener("DOMContentLoaded", function () {
  const popupContainer = document.querySelector(".popup-container");

  // Функция для показа popup
  function showPopup() {
    popupContainer.classList.remove("hidden");
    popupContainer.classList.add("visible");
  }

  // Показать popup через 25 секунд
  setTimeout(showPopup, 1000);

  // Закрытие popup при клике на "крестик"
  const closeButton = document.querySelector(".iks");
  closeButton.addEventListener("click", function () {
    popupContainer.classList.remove("visible");
    popupContainer.classList.add("hidden");
  });

  // Закрытие popup при клике вне popup
  popupContainer.addEventListener("click", function (event) {
    if (event.target === popupContainer) {
      popupContainer.classList.remove("visible");
      popupContainer.classList.add("hidden");
    }
  });
});
