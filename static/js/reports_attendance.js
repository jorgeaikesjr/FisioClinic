document.addEventListener('DOMContentLoaded', () => {
    // Inicializar datas: início do mês atual até hoje
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    
    document.getElementById('startDate').value = firstDay.toISOString().split('T')[0];
    document.getElementById('endDate').value = now.toISOString().split('T')[0];
    
    loadReport();
});

async function loadReport() {
    const start = document.getElementById('startDate').value;
    const end = document.getElementById('endDate').value;
    
    let url = '/reports/attendance';
    const params = [];
    if (start) params.push(`start_date=${start}T00:00:00`);
    if (end) params.push(`end_date=${end}T23:59:59`);
    
    if (params.length > 0) url += '?' + params.join('&');
    
    try {
        const data = await apiRequest(url);
        renderReport(data);
    } catch (e) {
        console.error('Erro ao carregar relatório:', e);
    }
}

function renderReport(data) {
    document.getElementById('totalAppointments').innerText = data.total_count;
    
    // Status Table
    const statusBody = document.getElementById('status-table-body');
    statusBody.innerHTML = '';
    const statuses = Object.entries(data.status_summary).sort((a, b) => b[1] - a[1]);
    
    if (statuses.length === 0) {
        statusBody.innerHTML = '<tr><td colspan="2" style="text-align:center">Nenhum dado no período.</td></tr>';
    } else {
        statuses.forEach(([status, count]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${status}</td><td><strong>${count}</strong></td>`;
            statusBody.appendChild(tr);
        });
    }
    
    // Category Table
    const categoryBody = document.getElementById('category-table-body');
    categoryBody.innerHTML = '';
    
    // Ordenar categorias pelo total de itens em cada uma
    const categories = Object.entries(data.category_summary).sort((a, b) => {
        const totalA = Object.values(a[1]).reduce((sum, val) => sum + val, 0);
        const totalB = Object.values(b[1]).reduce((sum, val) => sum + val, 0);
        return totalB - totalA;
    });
    
    if (categories.length === 0) {
        categoryBody.innerHTML = '<tr><td colspan="2" style="text-align:center">Nenhum dado no período.</td></tr>';
    } else {
        categories.forEach(([cat, statuses]) => {
            const total = Object.values(statuses).reduce((sum, val) => sum + val, 0);
            
            // Criar string detalhada de status
            const detailStr = Object.entries(statuses)
                .map(([status, count]) => `${count} ${status}`)
                .join(', ');

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <strong>${cat}</strong>
                    <div style="font-size: 0.85em; color: #64748b; margin-top: 4px;">${detailStr}</div>
                </td>
                <td style="vertical-align: top;"><strong>${total}</strong></td>
            `;
            categoryBody.appendChild(tr);
        });
    }
}
