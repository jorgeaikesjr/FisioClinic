const DAYS_PT = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];
const MONTHS_PT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

let isPrivateClinic = false;

// ── Helpers de semana ISO ────────────────────────────────────────────────────

function getISOWeek(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return [d.getUTCFullYear(), Math.ceil(((d - yearStart) / 86400000 + 1) / 7)];
}

function mondayOfISOWeek(week, year) {
    const simple = new Date(year, 0, 1 + (week - 1) * 7);
    const dow = simple.getDay();
    if (dow <= 4) simple.setDate(simple.getDate() - dow + 1);
    else simple.setDate(simple.getDate() + 8 - dow);
    return simple;
}

function weekInputValue(date) {
    const [y, w] = getISOWeek(date);
    return `${y}-W${w.toString().padStart(2, '0')}`;
}

// ── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    // Detectar tipo de clínica
    try {
        const config = await apiRequest('/settings/clinic-type');
        isPrivateClinic = config.clinic_type === 'particular';
    } catch (e) { isPrivateClinic = false; }

    // Mostrar/ocultar colunas de pagamento
    const pmHeader = document.getElementById('paymentMethodHeader');
    if (pmHeader) pmHeader.style.display = isPrivateClinic ? '' : 'none';

    // Set semana atual
    document.getElementById('filterWeek').value = weekInputValue(new Date());
    await loadReport();
});

// ── Navegação de semana ───────────────────────────────────────────────────────

function shiftWeek(delta) {
    const input = document.getElementById('filterWeek');
    const val = input.value;           // "YYYY-Www"
    if (!val) return;
    const [y, w] = val.split('-W').map(Number);
    const monday = mondayOfISOWeek(w, y);
    monday.setDate(monday.getDate() + delta * 7);
    input.value = weekInputValue(monday);
    loadReport();
}

// ── Carga de dados ────────────────────────────────────────────────────────────

async function loadReport() {
    const val = document.getElementById('filterWeek').value;
    if (!val) return;

    const [y, w] = val.split('-W').map(Number);
    const monday = mondayOfISOWeek(w, y);
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    sunday.setHours(23, 59, 59, 999);

    // Atualiza label descritivo
    const label = document.getElementById('weekLabel');
    if (label) {
        label.textContent =
            `${monday.getDate()} de ${MONTHS_PT[monday.getMonth()]} — ${sunday.getDate()} de ${MONTHS_PT[sunday.getMonth()]} de ${y}`;
    }

    const url = `/reports/weekly-summary?start_date=${monday.toISOString()}&end_date=${sunday.toISOString()}`;
    try {
        const data = await apiRequest(url);
        renderTable(data);
    } catch (e) { }
}

// ── Renderização ──────────────────────────────────────────────────────────────

const STATUS_BADGE = {
    'Agendado': '<span class="badge" style="background:var(--primary);color:#fff">Agendado</span>',
    'Realizado': '<span class="badge badge-success">Realizado</span>',
    'Faltou':    '<span class="badge" style="background:#e53e3e;color:#fff">Faltou</span>',
};

function renderTable(data) {
    const tbody = document.getElementById('weekly-table-body');
    const totalRow = document.getElementById('totalRow');
    const totalAmountEl = document.getElementById('totalAmount');
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center">Nenhum atendimento registrado nesta semana.</td></tr>`;
        totalRow.style.display = 'none';
        return;
    }

    let total = 0;

    data.forEach(item => {
        const start = new Date(item.start_time);
        const end   = new Date(item.end_time);

        const dia      = `${DAYS_PT[start.getDay()]}, ${start.getDate()}/${(start.getMonth()+1).toString().padStart(2,'0')}`;
        const horario  = `${start.toLocaleTimeString('pt-BR', {hour:'2-digit', minute:'2-digit'})} – ${end.toLocaleTimeString('pt-BR', {hour:'2-digit', minute:'2-digit'})}`;
        const badge    = STATUS_BADGE[item.status] || item.status;

        let paymentMethodCell = '';
        let amountCell = '';

        if (isPrivateClinic) {
            paymentMethodCell = `<td>${item.payment_method || '<span class="text-muted">—</span>'}</td>`;
        }

        const paid = item.amount_paid != null ? item.amount_paid : null;
        if (paid != null) total += paid;
        amountCell = paid != null
            ? `<td style="font-weight:600;color:var(--success)">R$ ${paid.toFixed(2).replace('.', ',')}</td>`
            : `<td><span class="text-muted">—</span></td>`;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${item.patient_name}</strong></td>
            <td>${dia}</td>
            <td>${horario}</td>
            <td>${badge}</td>
            ${paymentMethodCell}
            ${amountCell}
        `;
        tbody.appendChild(tr);
    });

    // Totalizador
    if (isPrivateClinic) {
        // ajusta colspan para incluir coluna de forma de pagamento
        totalRow.querySelector('td:first-child').colSpan = 4;
    } else {
        totalRow.querySelector('td:first-child').colSpan = 3;
    }

    totalAmountEl.textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
    totalRow.style.display = '';
}
