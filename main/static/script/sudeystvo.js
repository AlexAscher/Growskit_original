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
