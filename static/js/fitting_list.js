document.addEventListener('DOMContentLoaded', () => {
    loadPatients();
    loadFittingList();
});

async function loadPatients() {
    try {
        const patients = await apiRequest('/patients/?active_only=true');
        const select = document.getElementById('selectPatient');
        
        patients.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.name;
            select.appendChild(opt);
        });
    } catch (e) {}
}

async function loadFittingList() {
    try {
        const items = await apiRequest('/fitting-list/');
        renderTable(items);
    } catch (e) {}
}

function renderTable(items) {
    const tbody = document.getElementById('fitting-list-body');
    const badge = document.getElementById('countBadge');
    tbody.innerHTML = '';
    badge.textContent = `${items.length} paciente(s)`;
    
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">A lista de encaixe está vazia.</td></tr>';
        return;
    }
    
    items.forEach(item => {
        const tr = document.createElement('tr');
        const dateStr = new Date(item.date_added).toLocaleString('pt-BR');
        
        tr.innerHTML = `
            <td><strong>${item.patient ? item.patient.name : 'Paciente Desconhecido'}</strong></td>
            <td>${item.patient ? item.patient.contact : '-'}</td>
            <td>${dateStr}</td>
            <td>
                <button class="btn btn-danger" onclick="removeFromList('${item.id}')" title="Remover da lista">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function addToFittingList() {
    const patientId = document.getElementById('selectPatient').value;
    if (!patientId) {
        alert('Selecione um paciente para adicionar.');
        return;
    }
    
    try {
        await apiRequest('/fitting-list/', 'POST', { patient_id: patientId });
        loadFittingList();
        document.getElementById('selectPatient').value = '';
    } catch (e) {}
}

async function removeFromList(id) {
    if (confirm('Deseja remover este paciente da lista de encaixe?')) {
        try {
            await apiRequest(`/fitting-list/${id}`, 'DELETE');
            loadFittingList();
        } catch (e) {}
    }
}
