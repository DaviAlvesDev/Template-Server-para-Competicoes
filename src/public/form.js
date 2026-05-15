const uploadForm = document.querySelector('#uploadForm')
const statusMessage = document.querySelector('#status-message')
const btnEnviar = document.querySelector('#btn-enviar')

async function handleSubmit(event) {
    // Impede o recarregamento da página
    event.preventDefault()

    // Coleta os dados do formulário
    const formData = new FormData(uploadForm)
    
    // Feedback visual de carregamento
    btnEnviar.disabled = true
    btnEnviar.innerText = "ENVIANDO..."
    statusMessage.innerText = "⏳ Processando sua submissão..."
    statusMessage.style.color = "var(--text-color)"

    try {
        // Envia os dados para o servidor Flask
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        })

        const result = await response.json()

        if (response.ok) {
            // Sucesso!
            statusMessage.innerText = `✅ ${result.mensagem}`
            statusMessage.style.color = "#34a853" // Verde sucesso
            uploadForm.reset() // Limpa o formulário para o próximo envio
        } else {
            // Erro retornado pelo servidor (ex: problema inválido)
            statusMessage.innerText = `❌ Erro: ${result.erro}`
            statusMessage.style.color = "#ea4335" // Vermelho erro
        }

    } catch (error) {
        // Erro de rede (ex: servidor offline ou IP errado)
        statusMessage.innerText = "❌ Falha na conexão com o servidor"
        statusMessage.style.color = "#ea4335"
        console.error("Erro no upload:", error)
    } finally {
        // Restaura o botão após o processo
        btnEnviar.disabled = false
        btnEnviar.innerText = "ENVIAR PARA DAVIZERA"
    }
}

// Escuta o evento de submit do formulário
uploadForm.addEventListener('submit', handleSubmit)