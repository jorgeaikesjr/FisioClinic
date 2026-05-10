document.addEventListener('DOMContentLoaded', loadPatients);

let patientsList = [];
let sortCol = 'name';
let sortAsc = true;

async function loadPatients() {
    try {
        patientsList = await apiRequest('/patients/');
        renderTable();
    } catch (e) {
        // Error already handled in apiRequest
    }
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
    const tbody = document.getElementById('patients-table-body');
    tbody.innerHTML = '';
    
    if (patientsList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Nenhum paciente cadastrado.</td></tr>';
        return;
    }

    let sortedData = [...patientsList];
    sortedData.sort((a, b) => {
        let valA = a[sortCol];
        let valB = b[sortCol];

        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();
        
        // Tratar nulos para comparação
        if (valA === null) valA = '';
        if (valB === null) valB = '';

        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
    });
    
    sortedData.forEach(p => {
        const badge = p.is_active !== false // Trata undef/true como ativo pra retrocompatibilidade
            ? '<span class="badge badge-success">Ativo</span>'
            : '<span class="badge badge-gray">Inativo</span>';
            
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${p.name}</strong></td>
            <td>${p.contact}</td>
            <td>${p.guardian ? p.guardian : '<span class="text-muted">-</span>'}</td>
            <td>${badge}</td>
            <td>
                <button class="btn btn-secondary" onclick="editPatient('${p.id}')">
                    <i class="fa-solid fa-pen"></i>
                </button>
                ${p.is_active !== false ? `
                <button class="btn btn-danger" onclick="deletePatient('${p.id}')" title="Inativar Paciente">
                    <i class="fa-solid fa-user-slash"></i>
                </button>
                ` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openPatientModal(patient = null) {
    const title = document.getElementById('modalTitle');
    const form = document.getElementById('patientForm');
    
    if (patient) {
        title.innerText = 'Editar Paciente';
        document.getElementById('patientId').value = patient.id;
        document.getElementById('patientName').value = patient.name;
        document.getElementById('patientContact').value = patient.contact;
        document.getElementById('patientGuardian').value = patient.guardian || '';
        document.getElementById('patientAnamnesis').value = patient.anamnesis || '';
        document.getElementById('patientActive').checked = patient.is_active !== false;
    } else {
        title.innerText = 'Novo Paciente';
        form.reset();
        document.getElementById('patientId').value = '';
        document.getElementById('patientActive').checked = true;
    }
    
    openModal('patientModal');
}

function editPatient(id) {
    const patient = patientsList.find(p => p.id === id);
    if (patient) openPatientModal(patient);
}

async function savePatient(e) {
    e.preventDefault();
    
    const id = document.getElementById('patientId').value;
    const data = {
        name: document.getElementById('patientName').value,
        contact: document.getElementById('patientContact').value,
        guardian: document.getElementById('patientGuardian').value || null,
        anamnesis: document.getElementById('patientAnamnesis').value || null,
        is_active: document.getElementById('patientActive').checked
    };
    
    try {
        if (id) {
            await apiRequest(`/patients/${id}`, 'PATCH', data);
        } else {
            await apiRequest('/patients/', 'POST', data);
        }
        closeModal('patientModal');
        await loadPatients();
    } catch (error) {}
}

async function deletePatient(id) {
    if (confirm('Deseja inativar este paciente? Ele não aparecerá mais para novos agendamentos, mas o histórico será mantido.')) {
        try {
            await apiRequest(`/patients/${id}`, 'DELETE');
            await loadPatients();
        } catch(error){}
    }
}
