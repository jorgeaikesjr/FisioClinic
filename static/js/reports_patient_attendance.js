document.addEventListener('DOMContentLoaded', async () => {
    // Definir ano atual por padrão
    document.getElementById('reportYear').value = new Date().getFullYear();
    
    // Carregar lista de pacientes para o select
    await loadPatients();
});

async function loadPatients() {
    try {
        const patients = await apiRequest('/patients/');
        const select = document.getElementById('patientSelect');
        
        // Ordenar alfabeticamente
        patients.sort((a, b) => a.name.localeCompare(b.name));
        
        patients.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = p.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
    }
}

async function loadPatientReport() {
    const patientId = document.getElementById('patientSelect').value;
    const year = document.getElementById('reportYear').value;
    
    if (!patientId) {
        alert('Por favor, selecione um paciente.');
        return;
    }
    
    try {
        const data = await apiRequest(`/reports/patient-attendance?patient_id=${patientId}&year=${year}`);
        renderReport(data);
    } catch (error) {
        console.error('Erro ao carregar relatório:', error);
    }
}

function renderReport(data) {
    const resultDiv = document.getElementById('reportResult');
    const noDataDiv = document.getElementById('noDataMessage');
    const tbody = document.getElementById('monthly-table-body');
    const resultTitle = document.getElementById('resultTitle');
    const totalBadge = document.getElementById('totalYearly');
    
    tbody.innerHTML = '';
    
    const monthNames = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];
    
    let total = 0;
    let hasData = false;
    
    // Encontrar o maior valor para a barra de progresso
    const maxVal = Math.max(...Object.values(data.monthly_counts), 1);

    for (let m = 1; m <= 12; m++) {
        const count = data.monthly_counts[m] || 0;
        total += count;
        if (count > 0) hasData = true;
        
        const percentage = (count / (maxVal * 1.2)) * 100; // 1.2 para não encher 100% se for pouco
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${monthNames[m-1]}</td>
            <td><strong>${count}</strong> atendimento(s)</td>
            <td>
                <div style="width: 100%; background: #edf2f7; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="width: ${percentage}%; background: var(--primary); height: 100%; transition: width 0.5s ease;"></div>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    }
    
    if (total > 0) {
        resultTitle.innerText = `Atendimentos de ${data.patient_name} em ${data.year}`;
        totalBadge.innerText = `Total no Ano: ${total}`;
        resultDiv.style.display = 'block';
        noDataDiv.style.display = 'none';
    } else {
        resultDiv.style.display = 'none';
        noDataDiv.style.display = 'block';
    }
}
