document.addEventListener("DOMContentLoaded", function () {
  const formContainers = document.querySelectorAll(".form-container");
  const nextButtons = document.querySelectorAll(".next");
  const backButtons = document.querySelectorAll(".backButton");

  let currentStep = 0;

  // Функция для отображения нужного контейнера
  function showStep(step) {
    formContainers.forEach((container, index) => {
      container.style.display = index === step ? "block" : "none";
    });
  }

  // Обработчик кнопки "Далее"
  nextButtons.forEach((button, index) => {
    button.addEventListener("click", function () {
      if (currentStep < formContainers.length - 1) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  // Обработчик кнопки "Назад"
  backButtons.forEach((button, index) => {
    button.addEventListener("click", function () {
      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  // Изначально показываем только первый контейнер
  showStep(currentStep);
});

function equalizePacketsHeight() {
  let packets = document.querySelectorAll(".packet");
  let maxHeight = 0;

  // Сбрасываем высоту, чтобы вычислить максимальную
  packets.forEach((packet) => {
    packet.style.height = "auto";
    maxHeight = Math.max(maxHeight, packet.offsetHeight);
  });

  // Устанавливаем максимальную высоту
  packets.forEach((packet) => {
    packet.style.height = maxHeight + "px";
  });
}

// Функция для проверки ширины окна
function isScreenWidthGreaterThan576() {
  return window.innerWidth > 576;
}

// Вызываем функции только если ширина экрана больше 576px
window.addEventListener("load", () => {
  if (isScreenWidthGreaterThan576()) {
    equalizePacketsHeight();
    positionPriobrButtons();
  }
});

window.addEventListener("resize", () => {
  if (isScreenWidthGreaterThan576()) {
    equalizePacketsHeight();
    positionPriobrButtons();
  }
});

function positionPriobrButtons() {
  let packets = document.querySelectorAll(".packet");

  packets.forEach((packet) => {
    let priobrButton = packet.querySelector(".priobr");

    if (priobrButton) {
      priobrButton.style.position = "absolute";
      priobrButton.style.left = "25px"; // Отступ от левого края
      priobrButton.style.bottom = "32px"; // Отступ от нижнего края

      // Проверяем, чтобы от контента сверху был минимум 30px
      let packetHeight = packet.offsetHeight;
      let buttonTop =
        priobrButton.getBoundingClientRect().top -
        packet.getBoundingClientRect().top;

      if (buttonTop < 30) {
        priobrButton.style.marginTop = "30px";
      }
    }
  });
}
document.addEventListener("DOMContentLoaded", function () {
  const dropAreas = document.querySelectorAll(".file-upload");

  dropAreas.forEach((dropArea) => {
    // Находим элементы внутри текущего dropArea
    const fileInput = dropArea.querySelector('input[type="file"]');
    const filePreview = dropArea.querySelector(".file-preview");
    const fileNameElement = filePreview?.querySelector(".file-name");
    const removeFileBtn = filePreview?.querySelector(".remove-file-btn");
    const defaultContent = dropArea.querySelectorAll("h4, .upload-btn, h5");

    // Проверяем, что необходимые элементы существуют
    if (!filePreview || !fileNameElement || !removeFileBtn) {
      console.error(
        "Не найдены необходимые элементы для file-upload",
        dropArea
      );
      return;
    }

    // Функция для обновления предпросмотра файла
    function updateFilePreview(file) {
      if (file) {
        fileNameElement.textContent = file.name; // Отображаем имя файла
        filePreview.classList.remove("hidden"); // Показываем контейнер

        // Скрываем элементы по умолчанию
        defaultContent.forEach((element) => {
          element.style.display = "none";
        });
      } else {
        fileNameElement.textContent = ""; // Очищаем имя файла
        filePreview.classList.add("hidden"); // Скрываем контейнер

        // Показываем элементы по умолчанию
        defaultContent.forEach((element) => {
          element.style.display = "";
        });

        // Очищаем значение input
        fileInput.value = "";
      }
    }

    // Обработка выбора файла через input
    fileInput.addEventListener("change", function () {
      const file = this.files[0]; // Получаем выбранный файл
      updateFilePreview(file);
    });

    // Обработка нажатия на кнопку "крестик"
    removeFileBtn.addEventListener("click", function (e) {
      e.preventDefault();
      updateFilePreview(null); // Убираем файл
    });

    // Обработка перетаскивания файла
    dropArea.addEventListener("dragover", (event) => {
      event.preventDefault();
      dropArea.style.borderColor = "#df70bc";
    });

    dropArea.addEventListener("dragleave", () => {
      dropArea.style.borderColor = "rgba(255, 255, 255, 0.3)";
    });

    dropArea.addEventListener("drop", (event) => {
      event.preventDefault();
      dropArea.style.borderColor = "rgba(255, 255, 255, 0.3)";

      const files = event.dataTransfer.files;
      if (files.length > 0) {
        const dataTransfer = new DataTransfer(); // Создаем новый объект DataTransfer
        dataTransfer.items.add(files[0]); // Добавляем файл
        fileInput.files = dataTransfer.files; // Присваиваем файлы инпуту
        updateFilePreview(files[0]); // Обновляем предпросмотр
      }
    });
  });
});
