const chatArea = document.getElementById('chat-area');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const typingIndicator = document.getElementById('typing');
const resetBtn = document.getElementById('reset-btn');

// Función para reiniciar el chat
resetBtn.addEventListener('click', async () => {
    if (confirm('¿Querés empezar un chat nuevo? Se borrará la pantalla y la memoria.')) {
        chatArea.innerHTML = `
            <div class="message ai">
                ¡Hola! Soy el asistente de pf.hernanalvarez, puedo responder tu duda muy fácil. Decime en qué te puedo ayudar.
            </div>
        `;
        // Avisar al servidor que resetee la memoria
        try {
            await fetch('/reset', { method: 'POST' });
        } catch (e) {
            console.error("Error reseteando memoria", e);
        }
    }
});

function addMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(isUser ? 'user' : 'ai');
    
    // Convert markdown-like bold to HTML
    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    msgDiv.innerHTML = formattedText;
    
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;

    addMessage(query, true);
    userInput.value = '';
    typingIndicator.style.display = 'block';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: query }),
        });

        const data = await response.json();
        typingIndicator.style.display = 'none';
        
        if (data.error) {
            addMessage('**Error:** ' + data.error);
        } else {
            addMessage(data.response);
        }
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessage('**Error de conexión:** Asegúrate de que el servidor esté corriendo.');
        console.error(error);
    }
});

// Registrar Service Worker para PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Service Worker registrado'))
            .catch(err => console.log('Error al registrar SW', err));
    });
}
