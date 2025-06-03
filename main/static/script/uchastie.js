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

document.addEventListener("DOMContentLoaded", function () {
  const formContainer = document.getElementById("formContainer");

  // Делегирование событий для всех форм
  document.body.addEventListener("change", function (event) {
    const fileInput = event.target.closest('.file-upload input[type="file"]');
    if (fileInput) {
      const dropArea = fileInput.closest(".file-upload");
      handleFileInputChange(dropArea, fileInput.files[0]);
    }
  });

  document.body.addEventListener("click", function (event) {
    const removeFileBtn = event.target.closest(".remove-file-btn");
    if (removeFileBtn) {
      const dropArea = removeFileBtn.closest(".file-upload");
      handleRemoveFile(dropArea);
    }
  });

  document.body.addEventListener("dragover", function (event) {
    const dropArea = event.target.closest(".file-upload");
    if (dropArea) {
      event.preventDefault();
      dropArea.style.borderColor = "#df70bc";
    }
  });

  document.body.addEventListener("dragleave", function (event) {
    const dropArea = event.target.closest(".file-upload");
    if (dropArea) {
      dropArea.style.borderColor = "rgba(255, 255, 255, 0.3)";
    }
  });

  document.body.addEventListener("drop", function (event) {
    const dropArea = event.target.closest(".file-upload");
    if (dropArea) {
      event.preventDefault();
      dropArea.style.borderColor = "rgba(255, 255, 255, 0.3)";

      const files = event.dataTransfer.files;
      if (files.length > 0) {
        const fileInput = dropArea.querySelector('input[type="file"]');
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(files[0]);
        fileInput.files = dataTransfer.files;
        handleFileInputChange(dropArea, files[0]);
      }
    }
  });

  // Функция для обработки изменения input[type="file"]
  function handleFileInputChange(dropArea, file) {
    const filePreview = dropArea.querySelector(".file-preview");
    const fileNameElement = filePreview?.querySelector(".file-name");
    const defaultContent = dropArea.querySelectorAll("h4, .upload-btn, h5");

    if (file) {
      fileNameElement.textContent = file.name;
      filePreview.classList.remove("hidden");

      defaultContent.forEach((element) => {
        element.style.display = "none";
      });
    } else {
      fileNameElement.textContent = "";
      filePreview.classList.add("hidden");

      defaultContent.forEach((element) => {
        element.style.display = "";
      });
    }
  }

  // Функция для удаления файла
  function handleRemoveFile(dropArea) {
    const filePreview = dropArea.querySelector(".file-preview");
    const fileNameElement = filePreview?.querySelector(".file-name");
    const fileInput = dropArea.querySelector('input[type="file"]');
    const defaultContent = dropArea.querySelectorAll("h4, .upload-btn, h5");

    fileNameElement.textContent = "";
    filePreview.classList.add("hidden");

    defaultContent.forEach((element) => {
      element.style.display = "";
    });

    fileInput.value = "";
  }
  function attachEventListenersToForms() {
    const forms = document.querySelectorAll(".big-forma");

    forms.forEach((form) => {
      const nameInput = form.querySelector(
        'input[placeholder="Фамилия Имя Отчество"]'
      );
      const title = form.querySelector(".topform h2");

      if (nameInput && title) {
        // Проставляем начальное значение, если оно есть
        if (nameInput.value.trim() !== "") {
          title.textContent = nameInput.value.trim();
        }

        // Добавляем обработчик события input
        nameInput.addEventListener("input", function () {
          title.textContent =
            nameInput.value.trim() || "Информация об участнике";
        });
      }
    });
  }
  attachEventListenersToForms();
  // Обработчик для кнопки "Добавить форму"
  const addFormBtn = document.querySelector(".add-form-btn");
  let formCounter = 5;

  function initializeQuestionIcons() {
    const questionIcons = document.querySelectorAll(".questionSvg");

    if (questionIcons.length === 0) {
      console.error("Элементы .questionSvg не найдены в DOM.");
      return;
    }

    questionIcons.forEach((icon) => {
      const tooltip = icon.nextElementSibling;

      if (!tooltip || !tooltip.classList.contains("tooltip-custom")) {
        console.error(
          "Соседний элемент .tooltip-custom не найден для иконки:",
          icon
        );
        return;
      }

      const isTouchDevice = () =>
        "ontouchstart" in window || navigator.maxTouchPoints > 0;

      if (isTouchDevice()) {
        icon.addEventListener("touchstart", function (e) {
          e.stopPropagation();
          tooltip.classList.toggle("show-tooltip");
        });

        document.addEventListener("touchstart", function (e) {
          if (!e.target.closest(".questionSvg")) {
            tooltip.classList.remove("show-tooltip");
          }
        });
      } else {
        icon.addEventListener("mouseenter", function () {
          tooltip.classList.add("show-tooltip");
        });

        icon.addEventListener("mouseleave", function () {
          tooltip.classList.remove("show-tooltip");
        });
      }
    });
  }

  // Инициализация обработчиков при загрузке страницы
  initializeQuestionIcons();

  addFormBtn.addEventListener("click", function (e) {
    e.preventDefault();
    const newForm = document.createElement("div");
    newForm.classList.add("big-forma");
    const fileId = `fileInput${formCounter}`;
    formCounter++;
    newForm.innerHTML = `
      <div class="row">
            <div class="topform">
              <h2 style="margin-bottom: 0;">Информация об участнике</h2>
              <img src="/static/img/arrowForSelect.svg" alt="">
            </div>
            <div class="form-content">
              <div class="row">
                <div class="col-lg-8">
                  <div class="row">
                    <div class="col-md-6">

                      <input type="text" placeholder="Фамилия Имя Отчество" required name="fio" />
                    </div>
                    <div class="col-md-6 col-sm-12">
                      <input type="text" placeholder="Город страна" required name="city" />
                      
                    </div>
                    <div class="col-md-6 col-sm-12">
                      <div class="row align-items-center" style="--bs-gutter-x: 8px">
                        <div class="col-11">
                          <select name="category_participant" required>
                            <option value="" disabled selected>Категория участника</option>
                            <option value="junior">Юниор</option>
                            <option value="master">Мастер</option>
                            <option value="top-master">Топ-Мастер</option>
                            <option value="instructor">Инструктор</option>
                          </select>
                        </div>
                        <div class="col-1 position-relative">
                          <img src="/static/img/question.svg" alt="" class="questionSvg" />
                          <!-- Tooltip -->
                          <div class="tooltip-custom">
                            <p>Юниор: опыт менее 3 лет</p>
                            <p>Мастер: опыт от 3 до 5 лет</p>
                            <p>Топ-Мастер: опыт более 5 лет</p>
                            <p>Инструктор: в этой категории участвуют инструкторы вне зависимости от стажа работы</p>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <input type="text" placeholder="ФИО тренера (если есть)" name="fio_trainer" />
                    </div>

                    <div class="col-md-6 col-sm-6 input-margin-top" style="margin-top: 30px">
                      <input type="text" placeholder="Телефон" pattern="\+?[0-9\s\-()]{10,}" required name="phone" />
                    </div>
                    <div class="col-md-6 col-sm-6 input-margin-top" style="margin-top: 30px">
                      <input type="email" placeholder="Почта" required name="email" />
                    </div>
                    <div class="col-md-6">
                      <input type="text" placeholder="Ссылка на профиль ВК" name="vk" />
                    </div>
                    <div class="col-md-6">
                      <input type="text" placeholder="Ссылка на профиль Telegram" name="telegram" />
                    </div>
                    <div class="col-md-6">
                      <input type="text" placeholder="Почтовый адрес" required name="address" />
                    </div>
                    <div class="col-ld-6 col-12">
                      <input type="text" placeholder="Адрес ближайшего СДЭК" required name="address_sdek" />
                    </div>
                    <div class="col-12">
                      <textarea name="bio" id="" required
                        placeholder="Вкратце расскажите о своих достижениях и регалиях"></textarea>
                    </div>
                    <div class="col-md-6 kolvo">
                      <h3>Количество подаваемых работ</h3>
                    </div>
                    <div class="col-md-6"></div>
                    <div class="col-md-6">
                      <input type="text" placeholder="Количество работ" class="raboti" required name="count_work" />
                    </div>
                    <div class="col-lg-6">
                      <div class="nomin">
                        <p>1 номинация</p>
                        <h5>6000 ₽</h5>
                      </div>
                      <div class="lin"></div>
                      <div class="nomin">
                        <p>каждая следующая номинация</p>
                        <h5>5500 ₽</h5>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-lg-4 rightside">
                  <div class="file-upload">
                    <h4>Личное фото</h4>
                    <input type="file" id="${fileId}" hidden name="photo" required />
                    <label for="${fileId}" class="upload-btn">Выбрать</label>
                    <h5>или перетащите файлы сюда</h5>
                    <!-- Контейнер для отображения загруженного файла -->
                    <div class="file-preview hidden">
                      <img src="/static/img/file-icon.png" alt="File Icon" class="file-icon" />
                      <span class="file-name"></span>
                      <!-- Кнопка "крестик" -->
                      <button class="remove-file-btn">×</button>
                    </div>
                  </div>
                  <ul>
                    <li>Вокруг вашего силуэта должен быть воздух</li>
                    <li>Задний фон не имеет значения</li>
                    <li>Ваш взгляд направлен в камеру</li>
                    <li>Фотография должна быть в хорошем качестве</li>
                  </ul>
                  <p>
                    Ваши личные фото будут использоваться для оформления визитки участника в соц.сетях чемпионата и на сайте
                  </p>
                </div>
              </div>
            </div>
          </div>
    `;

    // Добавляем новую форму в контейнер
    formContainer.appendChild(newForm);

    // Присоединяем обработчики событий к новой форме
    attachEventListeners(newForm);
    initializeQuestionIcons();
  });

  // Функция для присоединения обработчиков событий к новым формам
  function attachEventListeners(form) {
    const toggleBtn = form.querySelector(".topform img");
    const formContent = form.querySelector(".form-content");
    const nameInput = form.querySelector(
      'input[placeholder="Фамилия Имя Отчество"]'
    );
    const title = form.querySelector(".topform h2");

    toggleBtn.addEventListener("click", function () {
      formContent.classList.toggle("hidden");
      toggleBtn.classList.toggle("rotated");
    });

    nameInput.addEventListener("input", function () {
      title.textContent = nameInput.value.trim() || "Информация об участнике";
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const payButton = document.querySelector(".oplata-button");

  // Добавляем обработчик события на кнопку "К оплате"
  payButton.addEventListener("click", function (e) {
    e.preventDefault(); // Предотвращаем стандартное поведение кнопки

    // Находим все формы участников
    const participantForms = document.querySelectorAll(
      ".big-forma .form-content"
    );

    // Счетчик заполненных форм
    let validParticipantsCount = 0;

    // Проверяем каждую форму на заполненность
    participantForms.forEach((form) => {
      const nameInput = form.querySelector(
        'input[placeholder="Фамилия Имя Отчество"]'
      );
      const workCountInput = form.querySelector(".raboti");

      // Проверяем, что ФИО и количество работ заполнены
      if (
        nameInput &&
        nameInput.value.trim() !== "" &&
        workCountInput &&
        parseInt(workCountInput.value) > 0
      ) {
        validParticipantsCount++;
      }
    });

    // Проверяем минимальное количество участников
    if (validParticipantsCount < 3) {
      alert("Для продолжения необходимо добавить минимум 3 участников.");
    } else {
      // Если условие выполнено, можно продолжить (например, отправить форму или перейти к следующему шагу)
      alert("Условие выполнено! Переход к оплате...");
      // Здесь можно добавить код для перехода к следующему шагу или отправки формы
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const radioButtons = document.querySelectorAll('input[name="participant"]');
  const individualForm = document.getElementById("individual-form");
  const teamLeaderForm = document.getElementById("team-leader-form");

  radioButtons.forEach((radio) => {
    radio.addEventListener("change", function () {
      if (this.value === "individual") {
        individualForm.classList.remove("hidden");
        teamLeaderForm.classList.add("hidden");
      } else {
        individualForm.classList.add("hidden");
        teamLeaderForm.classList.remove("hidden");
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const rabotiInput = document.querySelector(".raboti");
  const totalPriceElement = document.querySelector(".texta h5");
  const paymentButton = document.querySelector(".nizhyaya-button button");

  function updateTotalPrice() {
    let count = parseInt(rabotiInput.value, 10);

    if (isNaN(count) || count < 1) {
      totalPriceElement.textContent = "0 ₽";
      paymentButton.disabled = true;
      paymentButton.classList.add("disabled");
      return;
    }

    let totalPrice = 6000 + (count - 1) * 5500;
    totalPriceElement.textContent = totalPrice.toLocaleString("ru-RU") + " ₽";
    paymentButton.disabled = false;
    paymentButton.classList.remove("disabled");
  }

  rabotiInput.addEventListener("input", function (event) {
    // Разрешаем ввод только цифр
    this.value = this.value.replace(/[^0-9]/g, "");

    // Убираем ведущий ноль
    if (this.value.startsWith("0")) {
      this.value = this.value.replace(/^0+/, "");
    }

    updateTotalPrice();
  });

  updateTotalPrice();
});

function calculateTotal() {
  let totalPrice = 0;
  let discount = 0;
  let participants = document.querySelectorAll(".form-content");

  // Track how many participants have a valid work count
  let validParticipantCount = 0;

  participants.forEach((participant) => {
    let workInput = participant.querySelector(".raboti");
    let workCount = parseInt(workInput?.value) || 0;

    // Only count participants who have a valid work count
    if (workCount > 0) {
      let participantPrice = 6000 + (workCount - 1) * 5500;
      totalPrice += participantPrice;
      validParticipantCount++;
    }
  });

  // Discount is based on valid participants only
  discount = validParticipantCount * 1000;
  let finalPrice = totalPrice - discount;

  // Update the prices in the DOM
  document.querySelector(".prices h4").textContent =
    totalPrice > 0 ? totalPrice.toLocaleString() + " ₽" : "0 ₽";
  document.querySelector(".prices p").textContent =
    finalPrice > 0 ? finalPrice.toLocaleString() + " ₽" : "0 ₽";

  // Update the span with the number of valid participants for discount
  document.querySelector(".sale span").textContent = validParticipantCount;
}

document.addEventListener("input", function (event) {
  if (event.target.classList.contains("raboti")) {
    calculateTotal();
  }
});

// Prevent entering a number starting with 0 and only allow digits
document.addEventListener("input", function (event) {
  if (event.target.classList.contains("raboti")) {
    let value = event.target.value;
    // Remove leading zeros
    if (value && value[0] === "0") {
      event.target.value = value.replace(/^0+/, "");
    }

    // Allow only digits
    if (!/^\d+$/.test(event.target.value) && event.target.value !== "") {
      event.target.value = event.target.value.replace(/[^0-9]/g, "");
    }

    calculateTotal();
  }
});

document.addEventListener("DOMContentLoaded", calculateTotal);

// Обработчик нажатия на кнопку "К оплате"

// document.addEventListener("DOMContentLoaded", function () {
//   const questionIcons = document.querySelectorAll(".questionSvg");

//   if (questionIcons.length === 0) {
//     console.error("Элементы .questionSvg не найдены в DOM.");
//     return;
//   }

//   questionIcons.forEach((icon) => {
//     const tooltip = icon.nextElementSibling;

//     if (!tooltip || !tooltip.classList.contains("tooltip-custom")) {
//       console.error(
//         "Соседний элемент .tooltip-custom не найден для иконки:",
//         icon
//       );
//       return;
//     }

//     const isTouchDevice = () =>
//       "ontouchstart" in window || navigator.maxTouchPoints > 0;

//     if (isTouchDevice()) {
//       icon.addEventListener("touchstart", function (e) {
//         e.stopPropagation();
//         tooltip.classList.toggle("show-tooltip");
//       });

//       document.addEventListener("touchstart", function (e) {
//         if (!e.target.closest(".questionSvg")) {
//           tooltip.classList.remove("show-tooltip");
//         }
//       });
//     } else {
//       icon.addEventListener("mouseenter", function () {
//         tooltip.classList.add("show-tooltip");
//       });

//       icon.addEventListener("mouseleave", function () {
//         tooltip.classList.remove("show-tooltip");
//       });
//     }
//   });
// });
