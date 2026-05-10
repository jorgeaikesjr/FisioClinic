document.addEventListener('DOMContentLoaded', loadInterns);

let internsList = [];
let sortCol = 'name';
let sortAsc = true;

async function loadInterns() {
    try {
        internsList = await apiRequest('/interns/');
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
    const tbody = document.getElementById('interns-table-body');
    tbody.innerHTML = '';
    
    if (internsList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center">Nenhum estagiário cadastrado.</td></tr>';
        return;
    }

    let sortedData = [...internsList];
    sortedData.sort((a, b) => {
        let valA = a[sortCol];
        let valB = b[sortCol];

        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();

        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
    });
    
    sortedData.forEach(i => {
        const badge = i.is_active 
            ? '<span class="badge badge-success">Ativo</span>'
            : '<span class="badge badge-gray">Inativo</span>';
            
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${i.name}</strong></td>
            <td>${badge}</td>
            <td>
                <button class="btn btn-secondary" onclick="editIntern('${i.id}')">
                    <i class="fa-solid fa-pen"></i>
                </button>
                ${i.is_active ? `
                <button class="btn btn-danger" onclick="deleteIntern('${i.id}')" title="Desativar Estagiário">
                    <i class="fa-solid fa-user-xmark"></i>
                </button>
                ` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function openInternModal(intern = null) {
    const title = document.getElementById('modalTitle');
    const form = document.getElementById('internForm');
    
    if (intern) {
        title.innerText = 'Editar Estagiário';
        document.getElementById('internId').value = intern.id;
        document.getElementById('internName').value = intern.name;
        document.getElementById('internActive').checked = intern.is_active;
    } else {
        title.innerText = 'Novo Estagiário';
        form.reset();
        document.getElementById('internId').value = '';
        document.getElementById('internActive').checked = true;
    }
    
    openModal('internModal');
}

function editIntern(id) {
    const intern = internsList.find(i => i.id === id);
    if (intern) openInternModal(intern);
}

async function saveIntern(e) {
    e.preventDefault();
    
    const id = document.getElementById('internId').value;
    const data = {
        name: document.getElementById('internName').value,
        is_active: document.getElementById('internActive').checked
    };
    
    try {
        if (id) {
            await apiRequest(`/interns/${id}`, 'PATCH', data);
        } else {
            await apiRequest('/interns/', 'POST', data);
        }
        closeModal('internModal');
        await loadInterns();
    } catch (error) {}
}

async function deleteIntern(id) {
    if (confirm('Deseja inativar este estagiário? Ele não aparecerá mais para novos agendamentos.')) {
        try {
            await apiRequest(`/interns/${id}`, 'DELETE');
            await loadInterns();
        } catch(error){}
    }
}
