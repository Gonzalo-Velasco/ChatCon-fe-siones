import os
from flask import Flask
from flask_socketio import SocketIO, send
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

import threading
import requests
import eventlet

# CONFIGURACION TELEGRAM
tokenTelegram = "tu toquen aqui"
chatID = "tu ID aqui"

eventlet.monkey_patch()

# CREAR APP
app = Flask(__name__)

# CONFIGURAR SOCKETIO
socket = SocketIO(
    app,
    cors_allowed_origins="*"
)

# CREAR BOT TELEGRAM
botTelegram = ApplicationBuilder().token(
    tokenTelegram
).build()

# PAGINA PRINCIPAL
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>chat-para-Confesiones</title>
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
    :root {
      --login-green: #22c55e;
      --login-green-dark: #16a34a;
      --login-green-light: #dcfce7;
      --green: #4cbb6a;
      --bg: #e8edf5;
      --white: #ffffff;
      --gray-100: #f4f6fb;
      --gray-200: #e4e9f2;
      --gray-400: #9aa5b8;
      --gray-700: #3d4a5c;
      --text: #1c2333;
      --radius: 20px;
      --shadow: 0 8px 40px rgba(26,107,255,.13);
    }
 
    body {
      font-family: 'Nunito', sans-serif;
      background: var(--bg);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
 
    /* OVERLAY */
    .overlay {
      position: fixed; inset: 0;
      background: rgba(30,40,60,.35);
      backdrop-filter: blur(6px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      animation: fadeIn .3s ease;
    }
    .overlay.hidden { display: none; }
 
    @keyframes fadeIn  { from { opacity: 0 } to { opacity: 1 } }
    @keyframes slideUp { from { opacity: 0; transform: translateY(28px) scale(.97) } to { opacity: 1; transform: none } }
 
    /* MODAL LOGIN */
    .modal {
      background: var(--white);
      border-radius: var(--radius);
      padding: 40px 36px 36px;
      width: 360px;
      max-width: 94vw;
      box-shadow: var(--shadow);
      text-align: center;
      animation: slideUp .35s cubic-bezier(.22,1,.36,1);
    }
 
    .modal h1 { font-size: 1.55rem; font-weight: 800; color: var(--text); margin-bottom: 8px; }
    .modal p  { font-size: .93rem; color: var(--gray-400); line-height: 1.5; margin-bottom: 28px; }
 
    .input-wrap { position: relative; margin-bottom: 22px; }
    .input-wrap label {
      position: absolute;
      top: -10px; left: 14px;
      font-size: .78rem; font-weight: 700;
      color: var(--login-green);
      background: var(--white);
      padding: 0 5px;
    }
    .input-wrap input {
      width: 100%;
      border: 2px solid var(--login-green);
      border-radius: 12px;
      padding: 14px 16px;
      font-size: 1rem;
      font-family: 'Nunito', sans-serif;
      font-weight: 600;
      color: var(--text);
      background: transparent;
      outline: none;
      transition: border-color .2s, box-shadow .2s;
    }
    .input-wrap input:focus { box-shadow: 0 0 0 3px #22c55e22; }
 
    .btn-primary {
      width: 100%; padding: 15px;
      background: var(--login-green);
      color: #fff; border: none;
      border-radius: 14px;
      font-size: 1.02rem; font-weight: 800;
      font-family: 'Nunito', sans-serif;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center; gap: 10px;
      transition: background .2s, transform .1s;
    }
    .btn-primary:hover  { background: var(--login-green-dark); }
    .btn-primary:active { transform: scale(.98); }
    .btn-primary svg { width: 20px; height: 20px; fill: #fff; }
 
    /* CHAT APP */
    .chat-app {
      width: 560px; max-width: 96vw;
      background: var(--white);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      display: flex; flex-direction: column;
      overflow: hidden;
      height: 92vh; max-height: 700px;
      animation: slideUp .4s cubic-bezier(.22,1,.36,1);
    }
    .chat-app.hidden { display: none; }
 
    .chat-header {
      display: flex; align-items: center; gap: 14px;
      padding: 16px 20px;
      border-bottom: 1.5px solid var(--gray-200);
      background: var(--white);
    }
    .chat-header .av {
      width: 42px; height: 42px;
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: .95rem;
      color: #fff; flex-shrink: 0;
    }
    .chat-header-info { flex: 1; }
    .chat-header-info .room-name { font-weight: 800; font-size: 1rem; color: var(--text); }
    .chat-header-info .status {
      font-size: .8rem; color: var(--green);
      display: flex; align-items: center; gap: 5px; margin-top: 1px;
    }
    .status-dot {
      width: 7px; height: 7px;
      background: var(--green);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: .4 } }
 
    .header-actions { display: flex; gap: 6px; }
    .icon-btn {
      width: 36px; height: 36px;
      border-radius: 10px; border: none;
      background: var(--gray-100);
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      color: var(--gray-700);
      transition: background .15s;
      position: relative;
    }
    .icon-btn:hover { background: var(--gray-200); }
    .icon-btn svg { width: 17px; height: 17px; }
 
    .chat-messages {
      flex: 1; overflow-y: auto;
      padding: 20px 18px;
      display: flex; flex-direction: column; gap: 4px;
      background: var(--gray-100);
    }
    .chat-messages::-webkit-scrollbar { width: 5px; }
    .chat-messages::-webkit-scrollbar-thumb { background: var(--gray-200); border-radius: 10px; }
 
    .msg-system { text-align: center; font-size: .8rem; color: var(--gray-400); padding: 6px 0 10px; }
 
    .msg-row { display: flex; gap: 9px; align-items: flex-end; margin-bottom: 6px; }
    .msg-row.own { flex-direction: row-reverse; }
 
    .msg-av {
      width: 32px; height: 32px;
      border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-size: .7rem; font-weight: 800; color: #fff;
    }
 
    .msg-content { max-width: 72%; }
    .msg-name { font-size: .72rem; font-weight: 700; color: var(--gray-400); margin-bottom: 3px; padding-left: 2px; }
    .msg-row.own .msg-name { text-align: right; padding-right: 2px; }
 
    .msg-bubble {
      background: var(--white); color: var(--text);
      padding: 10px 14px;
      border-radius: 16px 16px 16px 4px;
      font-size: .93rem; line-height: 1.5;
      box-shadow: 0 2px 8px rgba(0,0,0,.06);
      word-break: break-word;
    }
    .msg-row.own .msg-bubble {
      background: var(--login-green); color: #fff;
      border-radius: 16px 16px 4px 16px;
    }
    .msg-time { font-size: .68rem; color: var(--gray-400); margin-top: 4px; padding: 0 2px; }
    .msg-row.own .msg-time { text-align: right; }
 
    .welcome-toast {
      position: fixed; bottom: 100px; left: 50%;
      transform: translateX(-50%);
      background: rgba(30,40,60,.85); color: #fff;
      padding: 10px 18px; border-radius: 24px;
      font-size: .88rem; font-weight: 600;
      display: flex; align-items: center; gap: 8px;
      backdrop-filter: blur(6px);
      animation: toastIn .4s ease, toastOut .4s ease 2.5s forwards;
      z-index: 200; white-space: nowrap;
    }
    .welcome-toast svg { width: 16px; height: 16px; fill: #7af0a0; }
    @keyframes toastIn  { from { opacity:0; transform: translateX(-50%) translateY(12px) } to { opacity:1; transform: translateX(-50%) translateY(0) } }
    @keyframes toastOut { from { opacity:1 } to { opacity:0; pointer-events:none } }
 
    .chat-input-area {
      padding: 14px 16px;
      border-top: 1.5px solid var(--gray-200);
      background: var(--white);
      display: flex; align-items: center; gap: 10px;
    }
    .chat-input {
      flex: 1;
      border: 1.5px solid var(--gray-200);
      border-radius: 24px;
      padding: 12px 18px;
      font-size: .93rem;
      font-family: 'Nunito', sans-serif;
      font-weight: 600; color: var(--text);
      background: var(--gray-100);
      outline: none;
      transition: border-color .2s;
    }
    .chat-input:focus { border-color: var(--login-green); background: var(--white); }
    .chat-input::placeholder { color: var(--gray-400); font-weight: 500; }
 
    .send-btn {
      width: 44px; height: 44px;
      border-radius: 50%;
      background: var(--login-green); border: none;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: background .2s, transform .1s; flex-shrink: 0;
    }
    .send-btn:hover  { background: var(--login-green-dark); }
    .send-btn:active { transform: scale(.93); }
    .send-btn svg { width: 20px; height: 20px; fill: #fff; margin-left: 2px; }
  </style>
</head>
<body>
 
<!-- OVERLAY LOGIN -->
<div class="overlay" id="overlay">
  <div class="modal">
    <h1>¡Bienvenido!</h1>
    <p>Ingresa tu nombre para comenzar a confesarte</p>
    <div class="input-wrap">
      <label for="usernameInput">Tu nombre de usuario</label>
      <input type="text" id="usernameInput" placeholder="" maxlength="30" autocomplete="off" />
    </div>
    <button class="btn-primary" id="enterBtn">
      Ingresar
    </button>
  </div>
</div>
 
<!-- CHAT APP -->
<div class="chat-app hidden" id="chatApp">
  <div class="chat-header">
    <div class="av" id="headerAvatar"></div>
    <div class="chat-header-info">
      <div class="room-name">Chat para Confesarse</div>
      <div class="status">
        <span class="status-dot"></span>
        Sincronizado 
      </div>
    </div>
    <div class="header-actions">
      <button class="icon-btn" id="darkBtn" title="Modo oscuro">
        <svg id="darkIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
      <button class="icon-btn" title="Salir" id="logoutBtn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>
  </div>
 
  <div class="chat-messages" id="chatMessages"></div>
 
  <div class="chat-input-area">
    <input class="chat-input" id="chatInput" type="text"
           placeholder="Escribe un mensaje..." maxlength="500" />
    <button class="send-btn" id="sendBtn">
      <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
    </button>
  </div>
</div>
 
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.5/socket.io.min.js"></script>
<script>
  var socket = io();
 
  const COLORS = ['#4cbb6a','#e06f5a','#a06bdb','#e0a020','#3ab4d8','#e05aa0','#22c49a'];
 
  let currentUser  = null;
  let userColor    = null;
  let darkMode     = false;
  const userColorMap = {};
 
  function getInitials(name) {
    return name.trim().split(/\s+/).map(w => w[0]).join('').toUpperCase().slice(0,2);
  }
 
  function colorForUser(name) {
    if (!userColorMap[name]) {
      userColorMap[name] = COLORS[Object.keys(userColorMap).length % COLORS.length];
    }
    return userColorMap[name];
  }
 
  function now() {
    return new Date().toLocaleTimeString('es', { hour:'2-digit', minute:'2-digit' });
  }
 
  // DOM
  const overlay       = document.getElementById('overlay');
  const usernameInput = document.getElementById('usernameInput');
  const enterBtn      = document.getElementById('enterBtn');
  const chatApp       = document.getElementById('chatApp');
  const headerAvatar  = document.getElementById('headerAvatar');
  const chatMessages  = document.getElementById('chatMessages');
  const chatInput     = document.getElementById('chatInput');
  const sendBtn       = document.getElementById('sendBtn');
  const logoutBtn     = document.getElementById('logoutBtn');
  const darkBtn       = document.getElementById('darkBtn');
  const darkIcon      = document.getElementById('darkIcon');
 
  usernameInput.addEventListener('keydown', e => { if (e.key === 'Enter') enterBtn.click(); });
 
  // Entrar
  enterBtn.addEventListener('click', () => {
    const name = usernameInput.value.trim();
    if (!name) { usernameInput.focus(); usernameInput.style.borderColor = '#ef4444'; return; }
    usernameInput.style.borderColor = '';
 
    currentUser = name;
    userColor   = colorForUser(name);
 
    headerAvatar.textContent  = getInitials(name);
    headerAvatar.style.background = userColor;
 
    overlay.classList.add('hidden');
    chatApp.classList.remove('hidden');
 
    socket.send('__join__' + name);
    showWelcomeToast(name);
    chatInput.focus();
  });
 
  // Enviar mensaje
  function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = '';
    socket.send(currentUser + ': ' + text);
  }
 
  sendBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });
 
  // Recibir mensajes
  socket.on('message', function(msg) {
    if (msg.startsWith('__join__')) {
      addSystemMessage(msg.replace('__join__', '') + ' se ha unido al chat');
      return;
    }
    if (msg.startsWith('__leave__')) {
      addSystemMessage(msg.replace('__leave__', '') + ' ha salido del chat');
      return;
    }
    const idx = msg.indexOf(': ');
    if (idx === -1) { addSystemMessage(msg); return; }
    const name  = msg.slice(0, idx);
    const text  = msg.slice(idx + 2);
    const own   = (name === currentUser);
    const color = colorForUser(name);
    addMessage({ name, color, text, own });
  });
 
  // Renders
  function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className   = 'msg-system';
    div.textContent = text;
    chatMessages.appendChild(div);
    scrollBottom();
  }
 
  function addMessage({ name, color, text, own }) {
    const row = document.createElement('div');
    row.className = 'msg-row' + (own ? ' own' : '');
 
    const av = document.createElement('div');
    av.className = 'msg-av';
    av.textContent = getInitials(name);
    av.style.background = color;
 
    const content = document.createElement('div');
    content.className = 'msg-content';
 
    const nameEl = document.createElement('div');
    nameEl.className   = 'msg-name';
    nameEl.textContent = own ? 'Tu' : name;
 
    const bubble = document.createElement('div');
    bubble.className   = 'msg-bubble';
    bubble.textContent = text;
 
    const time = document.createElement('div');
    time.className   = 'msg-time';
    time.textContent = now();
 
    content.appendChild(nameEl);
    content.appendChild(bubble);
    content.appendChild(time);
 
    if (own) { row.appendChild(content); row.appendChild(av); }
    else     { row.appendChild(av); row.appendChild(content); }
 
    chatMessages.appendChild(row);
    scrollBottom();
  }
 
  function scrollBottom() { chatMessages.scrollTop = chatMessages.scrollHeight; }
 
  // Toast
  function showWelcomeToast(name) {
    const toast = document.createElement('div');
    toast.className = 'welcome-toast';
    toast.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/></svg>Bienvenido, ' + name + '!';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3200);
  }
 
  // Logout
  logoutBtn.addEventListener('click', () => {
    if (!confirm('Salir del chat?')) return;
    socket.send('__leave__' + currentUser);
    setTimeout(() => {
      chatApp.classList.add('hidden');
      overlay.classList.remove('hidden');
      usernameInput.value = '';
      chatMessages.innerHTML = '';
      currentUser = null; userColor = null;
    }, 600);
  });
 
  // Modo oscuro
  darkBtn.addEventListener('click', () => {
    darkMode = !darkMode;
 
    if (darkMode) {
      darkIcon.innerHTML = [
        '<circle cx="12" cy="12" r="5"/>',
        '<line x1="12" y1="1"     x2="12" y2="3"/>',
        '<line x1="12" y1="21"    x2="12" y2="23"/>',
        '<line x1="4.22" y1="4.22"  x2="5.64" y2="5.64"/>',
        '<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>',
        '<line x1="1"  y1="12" x2="3"  y2="12"/>',
        '<line x1="21" y1="12" x2="23" y2="12"/>',
        '<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>',
        '<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>'
      ].join('');
      darkBtn.title = 'Modo claro';
 
      document.documentElement.style.setProperty('--bg',       '#121826');
      document.documentElement.style.setProperty('--white',    '#1c2639');
      document.documentElement.style.setProperty('--gray-100', '#16202e');
      document.documentElement.style.setProperty('--gray-200', '#28364f');
      document.documentElement.style.setProperty('--gray-400', '#6e849a');
      document.documentElement.style.setProperty('--text',     '#e4ecf7');
    } else {
      darkIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
      darkBtn.title = 'Modo oscuro';
 
      document.documentElement.style.setProperty('--bg',       '#e8edf5');
      document.documentElement.style.setProperty('--white',    '#ffffff');
      document.documentElement.style.setProperty('--gray-100', '#f4f6fb');
      document.documentElement.style.setProperty('--gray-200', '#e4e9f2');
      document.documentElement.style.setProperty('--gray-400', '#9aa5b8');
      document.documentElement.style.setProperty('--text',     '#1c2333');
    }
  });
</script>
</body>
</html>
"""

# MENSAJES DESDE WEB
@socket.on("message")
def recibirMensaje(mensaje):
    print("Mensaje WEB:", mensaje)
    
    # Mostrar a todos los clientes WEB (incluyendo al que lo envió)
    send(mensaje, broadcast=True)

    # Enviar a Telegram
    threading.Thread(
        target=enviarTelegram,
        args=(mensaje,)
    ).start()

# ENVIAR A TELEGRAM
def enviarTelegram(mensaje):
    url = f"https://api.telegram.org/bot{tokenTelegram}/sendMessage"
    data = {
        "chat_id": chatID,
        "text": f"{mensaje}"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error Telegram:", e)


# RECIBIR DESDE TELEGRAM
async def recibirTelegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.message.from_user.first_name
    mensaje = update.message.text
    texto = f"{usuario}: {mensaje}"
    
    print("Telegram:", texto)

    # SOLO enviar a WEB
    socket.emit(
        "telegram_message",
        texto
    )

# INICIAR BOT
def iniciarBot():
    botTelegram.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            recibirTelegram
        )
    )
    print("BOT TELEGRAM ACTIVO")
    botTelegram.run_polling()

# MAIN
if __name__ == "__main__":
    hiloBot = threading.Thread(target=iniciarBot)
    hiloBot.start()

    # CORREGIDO AQUÍ: Leer el puerto dinámico de Render
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Servidor iniciado en puerto {port}")
    socket.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False
    )