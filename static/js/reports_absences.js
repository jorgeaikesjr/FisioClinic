let absencesList = [];
let sortCol = 'absences_count';
let sortAsc = false; // Começa por maior numero de faltas

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar inputs de data com valores padrões atuais
    const now = new Date();
    
    // Set current week
    const year = now.getFullYear();
    const weekObj = getWeekNumber(now);
    document.getElementById('filterWeek').value = `${weekObj[0]}-W${weekObj[1].toString().padStart(2, '0')}`;
    
    // Set current month
    const month = (now.getMonth() + 1).toString().padStart(2, '0');
    document.getElementById('filterMonth').value = `${year}-${month}`;
    
    // Set current year
    document.getElementById('filterYear').value = year;
    
    // Set current custom dates (last 30 days)
    const thirtyDaysAgo = new Date(now);
    thirtyDaysAgo.setDate(now.getDate() - 30);
    document.getElementById('filterStartDate').value = thirtyDaysAgo.toISOString().split('T')[0];
    document.getElementById('filterEndDate').value = now.toISOString().split('T')[0];
    
    // Carrega a view inicial
    toggleFilterInputs();
    applyFilter();
});

function getWeekNumber(d) {
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
    var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7);
    return [d.getUTCFullYear(), weekNo];
}

function getDateOfISOWeek(w, y) {
    var simple = new Date(y, 0, 1 + (w - 1) * 7);
    var dow = simple.getDay();
    var ISOweekStart = simple;
    if (dow <= 4)
        ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1);
    else
        ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay());
    return ISOweekStart;
}

function toggleFilterInputs() {
    const type = document.getElementById('filterType').value;
    
    // Esconde todos
    document.getElementById('weekInputGroup').style.display = 'none';
    document.getElementById('monthInputGroup').style.display = 'none';
    document.getElementById('yearInputGroup').style.display = 'none';
    document.getElementById('customInputGroup').style.display = 'none';
    
    // Mostra o selecionado
    if (type === 'week') document.getElementById('weekInputGroup').style.display = 'block';
    if (type === 'month') document.getElementById('monthInputGroup').style.display = 'block';
    if (type === 'year') document.getElementById('yearInputGroup').style.display = 'block';
    if (type === 'custom') document.getElementById('customInputGroup').style.display = 'block';
}

async function applyFilter() {
    const type = document.getElementById('filterType').value;
    let url = '/reports/absences';
    
    let startDate = null;
    let endDate = null;
    
    if (type === 'week') {
        const val = document.getElementById('filterWeek').value; // Formato: YYYY-Www
        if (val) {
            const [y, w] = val.split('-W');
            startDate = getDateOfISOWeek(parseInt(w), parseInt(y));
            
            endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + 6);
            endDate.setHours(23, 59, 59, 999);
        }
    } else if (type === 'month') {
        const val = document.getElementById('filterMonth').value; // Formato: YYYY-MM
        if (val) {
            const [y, m] = val.split('-');
            startDate = new Date(y, parseInt(m)-1, 1);
            endDate = new Date(y, parseInt(m), 0, 23, 59, 59, 999);
        }
    } else if (type === 'year') {
        const y = document.getElementById('filterYear').value;
        if (y) {
            startDate = new Date(y, 0, 1);
            endDate = new Date(y, 11, 31, 23, 59, 59, 999);
        }
    } else if (type === 'custom') {
        const s = document.getElementById('filterStartDate').value;
        const e = document.getElementById('filterEndDate').value;
        if (s) startDate = new Date(s + 'T00:00:00');
        if (e) {
            endDate = new Date(e + 'T23:59:59');
        }
    }
    
    if (type !== 'total') {
        if (startDate && endDate) {
            url += `?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`;
        }
    }
    
    try {
        const reportData = await apiRequest(url);
        absencesList = reportData;
        renderTable();
    } catch (e) {}
}

function sortTable(col) {
    if (sortCol === col) {
        sortAsc = !sortAsc;
    } else {
        sortCol = col;
        sortAsc = true;
    }
    renderTable();
}

function renderTable() {
    const tbody = document.getElementById('reports-table-body');
    tbody.innerHTML = '';
    
    if (absencesList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Nenhuma falta registrada neste período. Parabéns!</td></tr>';
        return;
    }

    let sortedData = [...absencesList];
    sortedData.sort((a, b) => {
        let valA = a[sortCol];
        let valB = b[sortCol];

        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();

        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
    });
    
    sortedData.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${item.patient_name}</strong></td>
            <td>${item.patient_contact}</td>
            <td><span class="badge" style="background-color: var(--secondary); color: white; min-width: 40px; display: inline-block;">${item.absences_count}</span></td>
            <td><span class="badge" style="background-color: #e53e3e; color: white; min-width: 40px; display: inline-block;">${item.unjustified_absences}</span></td>
            <td><span class="badge" style="background-color: #f6ad55; color: white; min-width: 40px; display: inline-block;">${item.justified_absences}</span></td>
        `;
        tbody.appendChild(tr);
    });
}
