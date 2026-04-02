const isLembrarMarcado = "{{ session.permanent }}";

window.addEventListener("pagehide", function () {
  if (isLembrarMarcado !== "True") {
    fetch("/silent_logout", {
      method: "POST",
      keepalive: true,
    });
  }
});
