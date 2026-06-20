/* app.js — Sakinah chat UI. Vanilla JS, no framework, no build step. */

'use strict';

const STARTERS = [
  "I've been feeling really anxious lately",
  "I'm struggling with patience right now",
  "I feel like I've lost hope",
  "I feel so much guilt and need forgiveness",
];

/* ---- DOM refs ---- */
const welcomeScreen  = document.getElementById('screen-welcome');
const chatScreen     = document.getElementById('screen-chat');
const messagesEl     = document.getElementById('chat-messages');
const startersEl     = document.getElementById('starters');
const textarea       = document.getElementById('composer-textarea');
const sendBtn        = document.getElementById('btn-send');
const startBtn       = document.getElementById('btn-start');
const backBtn        = document.getElementById('btn-back');

/* ---- Screen transitions ---- */
function showChat() {
  welcomeScreen.classList.remove('screen--active');
  chatScreen.classList.add('screen--active');
  textarea.focus();
  appendBotText("Assalamu alaikum. I'm here with you, whenever you're ready. What's on your heart today?");
  renderStarters();
}

function showWelcome() {
  chatScreen.classList.remove('screen--active');
  welcomeScreen.classList.add('screen--active');
  messagesEl.innerHTML = '';
  startersEl.innerHTML = '';
}

startBtn.addEventListener('click', showChat);
backBtn.addEventListener('click', showWelcome);

/* ---- Conversation starters ---- */
function renderStarters() {
  startersEl.innerHTML = '';
  STARTERS.forEach((text) => {
    const chip = document.createElement('button');
    chip.className = 'starter-chip';
    chip.textContent = text;
    chip.addEventListener('click', () => {
      startersEl.innerHTML = '';
      sendMessage(text);
    });
    startersEl.appendChild(chip);
  });
}

/* ---- Composer ---- */
textarea.addEventListener('input', () => {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  const canSend = textarea.value.trim().length > 0;
  sendBtn.disabled = !canSend;
  sendBtn.classList.toggle('composer__send--active', canSend);
});

textarea.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) triggerSend();
  }
});

sendBtn.addEventListener('click', triggerSend);

function triggerSend() {
  const text = textarea.value.trim();
  if (!text) return;
  textarea.value = '';
  textarea.style.height = 'auto';
  sendBtn.disabled = true;
  sendBtn.classList.remove('composer__send--active');
  startersEl.innerHTML = '';
  sendMessage(text);
}

/* ---- Send & render pipeline ---- */
async function sendMessage(text) {
  appendUserBubble(text);
  scrollToBottom();

  const typingEl = appendTyping();
  scrollToBottom();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) throw new Error(`Server error ${res.status}`);
    const data = await res.json();

    typingEl.remove();

    if (data.is_crisis) {
      appendCrisis(data.response);
    } else {
      appendBotTurn(data.response, data.passage, data.outro);
      if (data.sources && data.sources.length > 0) {
        appendSources(data.sources);
      }
    }

    if (data.disclaimer) {
      appendDisclaimer(data.disclaimer);
    }

  } catch (err) {
    typingEl.remove();
    appendBotText("I'm having trouble connecting right now. Please try again in a moment.");
    console.error('Chat error:', err);
  }

  scrollToBottom();
}

/* ---- Render helpers ---- */

/* Bot avatar shown beside thread messages — the Sakinah logo mark. */
function makeBotAvatar() {
  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.setAttribute('aria-hidden', 'true');
  const img = document.createElement('img');
  img.className = 'msg-avatar__img';
  img.src = 'assets/logo-mark.png';
  img.alt = '';
  avatar.appendChild(img);
  return avatar;
}

function appendUserBubble(text) {
  const row = document.createElement('div');
  row.className = 'msg-row msg-row--user';
  const bubble = document.createElement('div');
  bubble.className = 'bubble bubble--user';
  bubble.textContent = text;
  row.appendChild(bubble);
  messagesEl.appendChild(row);
}

function appendBotText(text) {
  const row = document.createElement('div');
  row.className = 'msg-row msg-row--bot';

  const avatar = makeBotAvatar();

  const bubble = document.createElement('div');
  bubble.className = 'bubble bubble--bot';
  bubble.textContent = text;

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
}

/* A full bot reply: one avatar, then a vertical stack of
   intro bubble → verse card → outro bubble. */
function appendBotTurn(intro, passage, outro) {
  const row = document.createElement('div');
  row.className = 'msg-row msg-row--bot msg-row--turn';

  const avatar = makeBotAvatar();

  const stack = document.createElement('div');
  stack.className = 'bot-stack';

  if (intro) {
    const introBubble = document.createElement('div');
    introBubble.className = 'bubble bubble--bot';
    introBubble.textContent = intro;
    stack.appendChild(introBubble);
  }

  if (passage) {
    stack.appendChild(buildVerseCard(passage));
  }

  if (outro) {
    const outroBubble = document.createElement('div');
    outroBubble.className = 'bubble bubble--bot';
    outroBubble.textContent = outro;
    stack.appendChild(outroBubble);
  }

  row.appendChild(avatar);
  row.appendChild(stack);
  messagesEl.appendChild(row);
}

/* The styled passage card: verbatim Arabic (RTL) + translation + reference. */
function buildVerseCard(passage) {
  const card = document.createElement('div');
  card.className = 'verse-card';

  if (passage.arabic) {
    const ar = document.createElement('div');
    ar.className = 'verse-card__arabic';
    ar.setAttribute('lang', 'ar');
    ar.setAttribute('dir', 'rtl');
    ar.textContent = passage.arabic;
    card.appendChild(ar);
  }

  if (passage.translation) {
    const tr = document.createElement('div');
    tr.className = 'verse-card__translation';
    tr.textContent = '“' + passage.translation + '”';
    card.appendChild(tr);
  }

  if (passage.reference) {
    const ref = document.createElement('div');
    ref.className = 'verse-card__ref';
    ref.textContent = passage.reference;
    card.appendChild(ref);
  }

  return card;
}

function appendTyping() {
  const row = document.createElement('div');
  row.className = 'msg-row msg-row--bot';

  const avatar = makeBotAvatar();

  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  indicator.setAttribute('aria-label', 'Sakinah is thinking');
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('div');
    dot.className = 'typing-dot';
    indicator.appendChild(dot);
  }

  row.appendChild(avatar);
  row.appendChild(indicator);
  messagesEl.appendChild(row);
  return row;
}

function appendSources(sources) {
  const container = document.createElement('div');
  container.className = 'sources';

  sources.forEach((src) => {
    const chip = document.createElement('div');
    chip.className = 'source-chip';

    const typeSpan = document.createElement('span');
    typeSpan.className = 'source-chip__type';
    typeSpan.textContent = src.source_type;

    const refSpan = document.createElement('span');
    refSpan.textContent = src.reference;

    chip.appendChild(typeSpan);
    chip.appendChild(refSpan);
    container.appendChild(chip);
  });

  messagesEl.appendChild(container);
}

function appendDisclaimer(text) {
  const el = document.createElement('div');
  el.className = 'disclaimer';
  el.textContent = text;
  messagesEl.appendChild(el);
}

function appendCrisis(text) {
  const row = document.createElement('div');
  row.className = 'msg-row msg-row--bot';

  const avatar = makeBotAvatar();

  const card = document.createElement('div');
  card.className = 'crisis-notice';
  card.setAttribute('role', 'alert');

  const lines = text.split('\n\n');
  const heading = document.createElement('div');
  heading.className = 'crisis-notice__heading';
  heading.textContent = lines[0] || 'Urgent support needed';

  const body = document.createElement('div');
  body.className = 'crisis-notice__body';
  body.textContent = lines.slice(1).join('\n\n');

  card.appendChild(heading);
  card.appendChild(body);

  row.appendChild(avatar);
  row.appendChild(card);
  messagesEl.appendChild(row);
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
