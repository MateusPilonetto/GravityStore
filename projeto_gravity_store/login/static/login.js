const isLembrarMarcado = "{{ session.get('permanent', False) }}";

window.addEventListener("beforeunload", function (e) {
  if (isLembrarMarcado !== "True") {
    fetch("/logout", {
      method: "GET",
      keepalive: true,
    });
  }
});
