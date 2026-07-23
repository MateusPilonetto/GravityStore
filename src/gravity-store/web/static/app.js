document.addEventListener("DOMContentLoaded", () => {
  const search = document.querySelector("#search");

  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      search?.focus();
    }
  });

  document.querySelectorAll("[data-app-icon] img").forEach((image) => {
    image.addEventListener("error", () => image.classList.add("is-broken"), { once: true });
  });
});
