// Menu Interativo

const botao = document.getElementById("usuario");
const menu = document.getElementById("discovered");

// Escuta o clique ESQUERDO apenas no botão
botao.addEventListener("click", function (evento) {
  // IMPORTANTE: Isso impede que o clique "vaze" para o resto da página.
  // Sem isso, o clique bateria no botão e depois bateria no documento inteiro,
  // ativando aquela função de fechar o menu que fizemos antes!
  evento.stopPropagation();

  if (menu.style.display === "block") {
    menu.style.display = "none";
  } else {
    // Pega as coordenadas do mouse (igual fizemos no botão direito)
    const mouseX = evento.pageX;
    const mouseY = evento.pageY;

    // Move o menu para o local do clique
    menu.style.left = mouseX + "px";
    menu.style.top = mouseY + "px";

    // Mostra o menu
    menu.style.display = "block";
    elemento.style.transition = "opacity 4s ease-in-out"; // 2 segundos
    elemento.style.opacity = "0"; // A transição ocorrerá lentamente
  }
});

// O código para fechar o menu clicando fora continua o mesmo:
document.addEventListener("click", function (evento) {
  if (evento.target !== menu) {
    menu.style.display = "none";
    elemento.style.transition = "opacity 4s ease-in-out"; // 2 segundos
    elemento.style.opacity = "0"; // A transição ocorrerá lentamente
  }
});
