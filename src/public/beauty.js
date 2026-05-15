const html = document.documentElement // Forma mais direta de pegar o <html>
const switchButton = document.querySelector('#switch button')

function alterar_tema() {
    // Alterna a classe 'light' no elemento <html>
    html.classList.toggle('light')
    
    // Opcional: Salvar a preferência do aluno (mesmo offline, o navegador guarda)
    const isLight = html.classList.contains('light')
    localStorage.setItem('theme', isLight ? 'light' : 'dark')
}

// Escuta o clique no botão do switch
switchButton.addEventListener('click', alterar_tema)

// Verifica se já existia um tema salvo ao carregar a página
const savedTheme = localStorage.getItem('theme')
if (savedTheme === 'dark') {
    html.classList.remove('light')
}