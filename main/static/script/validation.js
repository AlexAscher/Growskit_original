document.addEventListener("DOMContentLoaded", function () {
  // Валидация для полей с placeholder="Телефон"
  const telephoneInputs = document.querySelectorAll(
    'input[placeholder="Телефон"]'
  );
  telephoneInputs.forEach((telephoneInput) => {
    telephoneInput.addEventListener("keydown", function (event) {
      const allowedKeys = /[0-9\s\-()+]/; // Разрешенные символы
      const key = event.key;

      // Разрешаем backspace, delete, стрелки и другие системные клавиши
      if (
        event.ctrlKey ||
        event.metaKey ||
        key === "Backspace" ||
        key === "Delete" ||
        key === "ArrowLeft" ||
        key === "ArrowRight" ||
        key === "ArrowUp" ||
        key === "ArrowDown" ||
        key === "Tab"
      ) {
        return;
      }

      // Запрещаем ввод недопустимых символов
      if (!allowedKeys.test(key)) {
        event.preventDefault();
      }
    });
  });

  // Валидация для полей с placeholder="Почта"
  const emailInputs = document.querySelectorAll('input[placeholder="Почта"]');
  emailInputs.forEach((emailInput) => {
    emailInput.addEventListener("keydown", function (event) {
      const allowedKeys = /[a-zA-Z0-9._%+-@]/; // Разрешенные символы для email
      const key = event.key;

      // Разрешаем backspace, delete, стрелки и другие системные клавиши
      if (
        event.ctrlKey ||
        event.metaKey ||
        key === "Backspace" ||
        key === "Delete" ||
        key === "ArrowLeft" ||
        key === "ArrowRight" ||
        key === "ArrowUp" ||
        key === "ArrowDown" ||
        key === "Tab"
      ) {
        return;
      }

      // Запрещаем ввод недопустимых символов
      if (!allowedKeys.test(key)) {
        event.preventDefault();
      }
    });

    // Добавляем проверку формата email при потере фокуса
    emailInput.addEventListener("blur", function () {
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/i;
      if (!emailRegex.test(emailInput.value)) {
        emailInput.setCustomValidity(
          "Введите корректный email (например, user@example.com)"
        );
      } else {
        emailInput.setCustomValidity(""); // Сброс ошибки
      }
    });

    // Проверка при отправке формы
    const form = emailInput.closest("form");
    if (form) {
      form.addEventListener("submit", function (event) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/i;
        if (!emailRegex.test(emailInput.value)) {
          emailInput.reportValidity(); // Показать сообщение об ошибке
          event.preventDefault(); // Предотвратить отправку формы
        }
      });
    }
  });
});
