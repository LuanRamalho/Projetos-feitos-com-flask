// 1. Configurar as fontes via JavaScript
const fontesDisponiveis = [
    "Arial", "Times New Roman", "Courier New", 
    "Verdana", "Georgia", "Comic Sans MS", "Impact"
];

document.addEventListener('DOMContentLoaded', () => {
    const selector = document.getElementById('fontFamilySelector');
    if (selector) {
        fontesDisponiveis.forEach(fonte => {
            let option = document.createElement('option');
            option.value = fonte;
            option.textContent = fonte;
            selector.appendChild(option);
        });

        selector.addEventListener('change', (e) => {
            changeFont(e.target.value);
        });
    }
});

// 2. Funções de Formatação
function format(command, value = null) {
    // Garante que o editor tenha foco antes de executar
    document.getElementById('editor').focus();
    document.execCommand(command, false, value);
}

function changeFont(font) {
    format('fontName', font);
}

function changeSize(step) {
    let currentSize = document.queryCommandValue("fontSize") || 3;
    let newSize = parseInt(currentSize) + step;
    if (newSize >= 1 && newSize <= 7) {
        format("fontSize", newSize);
    }
}

// 3. Salvar Conteúdo
async function saveNote(id) {
    const editor = document.getElementById('editor');
    const content = editor.innerHTML;
    
    try {
        const response = await fetch(`/save_content/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ conteudo: content })
        });

        if (response.ok) {
            alert("Nota salva com sucesso!");
        } else {
            alert("Erro ao salvar a nota.");
        }
    } catch (err) {
        console.error("Erro na requisição:", err);
    }
}

// Função para criar Hiperlink
function createLink() {
    const url = prompt("Insira a URL (ex: https://google.com):");
    if (url) {
        // Se não começar com http, adiciona automaticamente
        const formattedUrl = url.startsWith('http') ? url : `https://${url}`;
        format('createLink', formattedUrl);
    }
}

// Função para Salvar PDF
function downloadPDF() {
    const element = document.getElementById('editor');
    const tituloNota = document.querySelector('header h1').innerText;
    
    // Configurações do PDF
    const opt = {
        margin: [10, 10, 10, 10], // margens em mm
        filename: `${tituloNota}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
            scale: 2, 
            useCORS: true,
            letterRendering: true
        },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    // Gera e baixa o PDF
    html2pdf().set(opt).from(element).save();
}
