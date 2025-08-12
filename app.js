// Claude Voice Assistant - Frontend JavaScript

let isRecording = false;
let recognition = null;
let speechSynthesis = window.speechSynthesis;
let conversations = [];

// Initialize speech recognition
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = document.getElementById('language').value || 'he-IL';
        
        recognition.onstart = () => {
            console.log('Voice recognition started');
            updateStatus('מאזין...');
            document.getElementById('micButton').classList.add('active');
            document.getElementById('waveContainer').classList.add('active');
        };
        
        recognition.onresult = (event) => {
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                }
            }
            
            if (finalTranscript) {
                handleUserInput(finalTranscript);
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            updateStatus('שגיאה: ' + event.error);
            stopRecording();
        };
        
        recognition.onend = () => {
            console.log('Voice recognition ended');
            stopRecording();
        };
    } else {
        updateStatus('הדפדפן שלך לא תומך בזיהוי קולי');
    }
}

// Toggle recording
document.getElementById('micButton').addEventListener('click', () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
});

function startRecording() {
    if (!recognition) {
        initSpeechRecognition();
    }
    
    if (recognition) {
        isRecording = true;
        recognition.lang = document.getElementById('language').value || 'he-IL';
        recognition.start();
    }
}

function stopRecording() {
    isRecording = false;
    if (recognition) {
        recognition.stop();
    }
    document.getElementById('micButton').classList.remove('active');
    document.getElementById('waveContainer').classList.remove('active');
    updateStatus('לחץ על המיקרופון כדי להתחיל');
}

// Handle user input
async function handleUserInput(text) {
    console.log('User said:', text);
    addMessage(text, 'user');
    updateStatus('מעבד...');
    
    try {
        const response = await sendToClaude(text);
        addMessage(response, 'claude');
        speakText(response);
    } catch (error) {
        console.error('Error:', error);
        updateStatus('שגיאה בתקשורת עם Claude');
    }
}

// Send message to Claude API
async function sendToClaude(message) {
    // In production, this would connect to your backend API
    // For now, returning a mock response
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve('שלום! אני Claude, העוזר הקולי שלך. איך אוכל לעזור לך היום?');
        }, 1000);
    });
}

// Text to speech
function speakText(text) {
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
    }
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = document.getElementById('language').value || 'he-IL';
    utterance.rate = parseFloat(document.getElementById('speechRate').value || 1);
    
    // Select voice based on settings
    const voices = speechSynthesis.getVoices();
    const voiceType = document.getElementById('voice').value;
    if (voiceType !== 'default' && voices.length > 0) {
        const selectedVoice = voices.find(voice => 
            voice.lang.startsWith(utterance.lang.split('-')[0]) &&
            ((voiceType === 'male' && voice.name.toLowerCase().includes('male')) ||
             (voiceType === 'female' && voice.name.toLowerCase().includes('female')))
        );
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
    }
    
    utterance.onstart = () => {
        updateStatus('מדבר...');
    };
    
    utterance.onend = () => {
        updateStatus('לחץ על המיקרופון כדי להתחיל');
    };
    
    speechSynthesis.speak(utterance);
}

// Add message to conversation
function addMessage(text, sender) {
    const conversation = document.getElementById('conversation');
    conversation.style.display = 'block';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    
    conversation.appendChild(messageDiv);
    conversation.scrollTop = conversation.scrollHeight;
    
    // Store in conversations array
    conversations.push({
        sender: sender,
        text: text,
        timestamp: new Date().toISOString()
    });
}

// Update status
function updateStatus(text) {
    document.getElementById('status').textContent = text;
}

// Clear conversation
function clearConversation() {
    document.getElementById('conversation').innerHTML = '';
    document.getElementById('conversation').style.display = 'none';
    conversations = [];
    updateStatus('השיחה נוקתה');
}

// Toggle settings
function toggleSettings() {
    const settings = document.getElementById('settings');
    settings.style.display = settings.style.display === 'none' ? 'block' : 'none';
}

// Export conversation
function exportConversation() {
    if (conversations.length === 0) {
        alert('אין שיחה לייצא');
        return;
    }
    
    const content = conversations.map(msg => 
        `[${new Date(msg.timestamp).toLocaleString()}] ${msg.sender}: ${msg.text}`
    ).join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `claude-conversation-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize on load
window.addEventListener('load', () => {
    initSpeechRecognition();
    
    // Load voices
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = () => {
            const voices = speechSynthesis.getVoices();
            console.log('Available voices:', voices.length);
        };
    }
    
    // Set default values
    document.getElementById('language').value = 'he-IL';
    document.getElementById('speechRate').value = '1';
    document.getElementById('voice').value = 'default';
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Space bar to toggle recording
    if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        document.getElementById('micButton').click();
    }
    
    // Escape to stop recording
    if (e.code === 'Escape' && isRecording) {
        stopRecording();
    }
});

// Mobile optimizations
if ('ontouchstart' in window) {
    document.getElementById('micButton').addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (!isRecording) {
            startRecording();
        }
    });
    
    document.getElementById('micButton').addEventListener('touchend', (e) => {
        e.preventDefault();
        if (isRecording) {
            setTimeout(stopRecording, 1000); // Stop after 1 second
        }
    });
}