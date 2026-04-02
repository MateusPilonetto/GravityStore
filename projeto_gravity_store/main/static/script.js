// =========================================
// 1. MENU INTERATIVO DO USUÁRIO
// =========================================
const botao = document.getElementById("usuario");
const menu = document.getElementById("discovered");

// SÓ ADICIONA O EVENTO SE O BOTÃO EXISTIR (ou seja, se estiver logado)
if (botao && menu) {
  botao.addEventListener("click", (evento) => {
    evento.stopPropagation(); // Impede que o clique feche o menu imediatamente

    if (menu.style.display === "block") {
      menu.style.display = "none";
    } else {
      // Pega as coordenadas do mouse
      const mouseX = evento.pageX;
      const mouseY = evento.pageY;

      // Move o menu para o local do clique e mostra
      menu.style.left = mouseX + "px";
      menu.style.top = mouseY + "px";
      menu.style.display = "block";
    }
  });

  // O código para fechar o menu clicando fora
  document.addEventListener("click", function (evento) {
    // Se clicar em qualquer lugar que não seja o menu, ele fecha
    if (evento.target !== menu && !menu.contains(evento.target)) {
      menu.style.display = "none";
    }
  });
}

// =========================================
// 2. MENU HAMBÚRGUER (MOBILE)
// =========================================
console.log("--- DEBUG: Procurando o menu hambúrguer ---");
const btnHamburguer = document.getElementById("btn-hamburguer");
const listaMenu = document.getElementById("lista-menu");

// Avisa se não encontrar os elementos
if (!btnHamburguer)
  console.error("ERRO: O id 'btn-hamburguer' não foi encontrado!");
if (!listaMenu) console.error("ERRO: O id 'lista-menu' não foi encontrado!");

if (btnHamburguer && listaMenu) {
  console.log("Sucesso: Botão e Menu hambúrguer encontrados!");

  btnHamburguer.addEventListener("click", function (event) {
    event.preventDefault();
    console.log("O BOTÃO HAMBÚRGUER FOI CLICADO!");
    listaMenu.classList.toggle("mostrar-menu");
  });
}
