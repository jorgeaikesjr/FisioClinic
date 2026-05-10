document.addEventListener('DOMContentLoaded', () => {
    loadWaitingList();
});

async function loadWaitingList() {
    const category = document.getElementById('filterCategory').value;
    let url = '/waiting-list/';
    if (category) {
        url += `?category=${encodeURIComponent(category)}`;
    }

    const list = await apiRequest(url);
    const tbody = document.getElementById('waitingListBody');
    tbody.innerHTML = '';

    if (!list || list.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">A fila de espera está vazia.</td></tr>';
        return;
    }

    list.forEach(item => {
        const dateStr = new Date(item.date_added).toLocaleString('pt-BR');
        const patientName = item.patient ? item.patient.name : 'Desconhecido';
        const contact = item.patient ? item.patient.contact : 'N/A';
        const notes = item.notes || '-';
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${dateStr}</td>
            <td>${patientName}</td>
            <td>${contact}</td>
            <td><span class="badge" style="background-color: var(--primary); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.85em;">${item.category}</span></td>
            <td>${notes}</td>
            <td>
                <button class="btn" style="background-color: #fce4e4; color: #dc3545;" onclick="removeFromWaitingList('${item.id}')" title="Remover da Fila">
                    <i class="fa-solid fa-check"></i> Atendido/Remover
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function loadPatientsForSelect() {
    const patients = await apiRequest('/patients/?active_only=true');
    const select = document.getElementById('wlPatient');
    select.innerHTML = '<option value="">Selecione o paciente...</option>';
    
    if (patients) {
        patients.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `${p.name} - ${p.contact}`;
            select.appendChild(opt);
        });
    }
}

async function openWaitingListModal() {
    document.getElementById('waitingListForm').reset();
    await loadPatientsForSelect();
    openModal('waitingListModal');
}

async function submitWaitingList(event) {
    event.preventDefault();
    const data = {
        patient_id: document.getElementById('wlPatient').value,
        category: document.getElementById('wlCategory').value,
        notes: document.getElementById('wlNotes').value
    };

    try {
        await apiRequest('/waiting-list/', 'POST', data);
        closeModal('waitingListModal');
        loadWaitingList();
    } catch (error) {
        // Erro já tratado no alert do base.html
    }
}

async function removeFromWaitingList(id) {
    if (confirm("Deseja realmente remover este paciente da fila de espera?")) {
        try {
            await apiRequest(`/waiting-list/${id}`, 'DELETE');
            loadWaitingList();
        } catch (error) {
            // Tratado
        }
    }
}
