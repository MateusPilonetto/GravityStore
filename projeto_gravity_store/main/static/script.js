// =========================================
// 1. MENU INTERATIVO DO USUÁRIO
// =========================================
const botao = document.getElementById("usuario");
const menu = document.getElementById("discovered");

if (botao && menu) {
  botao.addEventListener("click", (evento) => {
    evento.stopPropagation(); 

    if (menu.style.display === "block") {
      menu.style.display = "none";
    } else {
      
      menu.style.display = "block";
    }
  });


  document.addEventListener("click", function (evento) {
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
