
import '../css/style.css';
import '../css/variables.css';
import { initChatbot } from './chatbot.js';

// Init Chatbot
initChatbot();

// Logic
const params = new URLSearchParams(window.location.search);
const idEl = document.getElementById('oid');
if (idEl) {
    idEl.innerText = params.get('orderId') || 'UNKNOWN';
}
