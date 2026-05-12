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
            
        const age = p.birth_date ? calculateAge(p.birth_date) : '-';
        const sexMap = { 'M': 'Masc', 'F': 'Fem', 'O': 'Outro' };
        const sexStr = p.sex ? (sexMap[p.sex] || p.sex) : '-';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${p.name}</strong></td>
            <td>${sexStr}</td>
            <td>${age}</td>
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

function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    return age;
}

function openPatientModal(patient = null) {
    const title = document.getElementById('modalTitle');
    const form = document.getElementById('patientForm');
    
    if (patient) {
        title.innerText = 'Editar Paciente';
        document.getElementById('patientId').value = patient.id;
        document.getElementById('patientName').value = patient.name;
        document.getElementById('patientContact').value = patient.contact;
        document.getElementById('patientSex').value = patient.sex || '';
        document.getElementById('patientBirthDate').value = patient.birth_date || '';
        document.getElementById('patientGuardian').value = patient.guardian || '';
        document.getElementById('patientAnamnesis').value = patient.anamnesis || '';
        document.getElementById('patientActive').checked = patient.is_active !== false;
    } else {
        title.innerText = 'Novo Paciente';
        form.reset();
        document.getElementById('patientId').value = '';
        document.getElementById('patientSex').value = '';
        document.getElementById('patientBirthDate').value = '';
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
        sex: document.getElementById('patientSex').value || null,
        birth_date: document.getElementById('patientBirthDate').value || null,
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
    try {
        const check = await apiRequest(`/patients/${id}/future-count`);
        const count = check.count;
        
        let cancelFuture = false;
        let message = 'Deseja inativar este paciente? Ele não aparecerá mais para novos agendamentos, mas o histórico será mantido.';
        
        if (count > 0) {
            message = `Este paciente possui ${count} agendamento(s) futuro(s).\n\nDeseja inativá-lo e CANCELAR todos os agendamentos futuros?\n\n- Clique em [OK] para Inativar e Cancelar os ${count} agendamentos.\n- Clique em [Cancelar] para apenas Inativar (mantendo os agendamentos na agenda).`;
            if (confirm(message)) {
                cancelFuture = true;
            } else {
                // Pergunta se deseja apenas inativar sem cancelar
                if (!confirm('Deseja apenas inativar o paciente (mantendo os agendamentos futuros)?')) {
                    return; // Aborta tudo
                }
                cancelFuture = false;
            }
        } else {
            if (!confirm(message)) return;
        }

        await apiRequest(`/patients/${id}?cancel_future=${cancelFuture}`, 'DELETE');
        await loadPatients();
    } catch(error) {
        console.error('Erro ao inativar paciente:', error);
    }
}
