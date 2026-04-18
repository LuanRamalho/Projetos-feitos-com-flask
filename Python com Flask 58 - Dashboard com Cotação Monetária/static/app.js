let dashboardState = null;
let marketChart = null;
let systemChart = null;

function money(n, digits = 6) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return "--";
  return Number(n).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: digits
  });
}

function pct(n) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return "--";
  const value = Number(n);
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function fmtChange(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  const n = Number(value);
  return `${n >= 0 ? "+" : ""}${n.toFixed(6)}`;
}

function fmtTrend(trend) {
  if (trend === "up") return `<span class="badge-soft badge-up"><i class="bi bi-arrow-up"></i> Alta</span>`;
  if (trend === "down") return `<span class="badge-soft badge-down"><i class="bi bi-arrow-down"></i> Queda</span>`;
  return `<span class="badge-soft badge-flat"><i class="bi bi-dash"></i> Estável</span>`;
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function renderMarketTable(quotes) {
  const tbody = document.getElementById("quotes-body");
  tbody.innerHTML = quotes.map((q) => `
    <tr>
      <td class="fw-semibold">${q.code}</td>
      <td>${q.name}</td>
      <td class="text-end">${money(q.rate, 8)}</td>
      <td class="text-end">
        <span class="${Number(q.change_pct || 0) >= 0 ? 'text-success' : 'text-danger'}">
          ${fmtChange(q.change)} (${pct(q.change_pct)})
        </span>
      </td>
      <td class="text-end">${fmtTrend(q.trend)}</td>
    </tr>
  `).join("");
}

/**
 * Renderiza os selects do conversor.
 * Corrigido para receber o objeto 'market' e evitar erro de 'null'.
 */
function renderSelect(market) {
  const from = document.getElementById("convert-from");
  const to = document.getElementById("convert-to");

  // Evita resetar as moedas que o usuário já selecionou a cada atualização de 20s
  if (from.options.length > 0) return;

  const quotes = market.quotes;
  const currencies = [
    { code: market.base, name: market.base_name },
    ...quotes
  ];

  const options = currencies
    .map((c) => `<option value="${c.code}">${c.code} — ${c.name}</option>`)
    .join("");

  from.innerHTML = options;
  to.innerHTML = options;

  // Define valores padrão na primeira carga
  from.value = market.base;
  to.value = quotes[0]?.code || market.base;
}

function renderMarketChart(quotes) {
  const labels = quotes.map(q => q.code);
  const values = quotes.map(q => q.rate);

  const ctx = document.getElementById("marketChart");
  if (marketChart) marketChart.destroy();

  marketChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Taxa atual",
        data: values,
        backgroundColor: "rgba(13, 110, 253, 0.5)",
        borderColor: "rgba(13, 110, 253, 1)",
        borderWidth: 1,
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { ticks: { color: "rgba(255,255,255,.7)" }, grid: { display: false } },
        y: { ticks: { color: "rgba(255,255,255,.7)" }, grid: { color: "rgba(255,255,255,.08)" } }
      }
    }
  });
}

function renderSystemChart(system) {
  const ctx = document.getElementById("systemChart");
  if (systemChart) systemChart.destroy();

  systemChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["CPU", "Memória", "Disco"],
      datasets: [{
        data: [
          system.cpu.percent,
          system.memory.percent,
          system.disk.percent
        ],
        backgroundColor: [
          "rgba(255, 99, 132, 0.7)",
          "rgba(54, 162, 235, 0.7)",
          "rgba(75, 192, 192, 0.7)"
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      cutout: "70%",
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: "rgba(255,255,255,.8)", padding: 20 }
        }
      }
    }
  });
}

function updateStats(data) {
  // 1. ATRIBUIÇÃO IMEDIATA: Resolve o erro de "reading 'market' of null"
  dashboardState = data;
  
  const { market, system, generated_at } = data;

  // Atualização de textos e badges
  setText("base-currency", `${market.base} — ${market.base_name}`);
  setText("source-info", `${market.source} • ${market.source_detail}`);
  setText("updated-at", `Atualizado em ${market.updated_at}`);
  setText("last-update", `Último refresh: ${generated_at}`);

  const g = market.best_gainer;
  const l = market.worst_loser;
  setText("best-gainer", g ? `${g.code} ${pct(g.change_pct)}` : "--");
  setText("best-gainer-sub", g ? `${g.name} • taxa ${money(g.rate, 4)}` : "--");
  setText("worst-loser", l ? `${l.code} ${pct(l.change_pct)}` : "--");
  setText("worst-loser-sub", l ? `${l.name} • taxa ${money(l.rate, 4)}` : "--");
  setText("avg-change", `${market.avg_change_pct >= 0 ? "+" : ""}${market.avg_change_pct.toFixed(2)}%`);

  // Métricas do sistema
  setText("cpu-summary", `${system.cpu.percent.toFixed(1)}% • ${system.cpu.cores_logical} núcleos`);
  setText("memory-summary", `${system.memory.percent.toFixed(1)}% • ${system.memory.used_gb} / ${system.memory.total_gb} GB`);
  setText("disk-summary", `${system.disk.percent.toFixed(1)}% • ${system.disk.used_gb} / ${system.disk.total_gb} GB`);
  setText("uptime-summary", `${system.uptime}`);

  // Renderização de componentes visuais
  renderMarketTable(market.quotes);
  renderSelect(market); // Passando o objeto market diretamente
  renderMarketChart(market.quotes);
  renderSystemChart(system);

  updateConversion();
}

function updateConversion() {
  if (!dashboardState) return;

  const amountEl = document.getElementById("convert-amount");
  const fromEl = document.getElementById("convert-from");
  const toEl = document.getElementById("convert-to");
  const resultEl = document.getElementById("convert-result");

  const amount = Number(amountEl.value || 0);
  const fromCode = fromEl.value;
  const toCode = toEl.value;
  const base = dashboardState.market.base;
  const quotes = dashboardState.market.quotes;

  const getRate = (code) => {
    if (code === base) return 1;
    const q = quotes.find((item) => item.code === code);
    return q ? q.rate : null;
  };

  const fromRate = getRate(fromCode);
  const toRate = getRate(toCode);

  if (fromRate === null || toRate === null) {
    resultEl.textContent = "--";
    return;
  }

  // Cálculo: Transforma origem em base, depois base em destino
  const valueInBase = amount / fromRate;
  const finalValue = valueInBase * toRate;

  resultEl.textContent = `${amount.toLocaleString("pt-BR")} ${fromCode} = ${finalValue.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })} ${toCode}`;
}

async function loadDashboard() {
  try {
    const res = await fetch("/api/dashboard", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    updateStats(data);
  } catch (err) {
    console.error("Erro ao carregar dashboard:", err);
    const body = document.getElementById("quotes-body");
    if (body) {
        body.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Falha ao carregar dados: ${err.message}</td></tr>`;
    }
    setText("last-update", "Falha na atualização");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Listeners para o conversor
  const convBtn = document.getElementById("convert-btn");
  if (convBtn) convBtn.addEventListener("click", updateConversion);
  
  ["convert-from", "convert-to", "convert-amount"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", updateConversion);
  });

  loadDashboard();
  setInterval(loadDashboard, (window.DASH_CONFIG?.pollSeconds || 20) * 1000);
});