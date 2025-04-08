document.addEventListener("DOMContentLoaded", function () {
  const menuItems = document.querySelectorAll(".menu_item1");
  const menuToggle = document.getElementById("menu__toggle");

  menuItems.forEach(function (menuItem) {
    menuItem.addEventListener("click", function () {
      menuToggle.checked = !menuToggle.checked;
    });
  });
});
