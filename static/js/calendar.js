let calendar;
let patients = [];
let interns = [];
let isPrivateClinic = false; // Controlado pela config do servidor

document.addEventListener('DOMContentLoaded', async function() {
    await applyClinicConfig();
    await loadSelectData();
    initCalendar();
});

async function applyClinicConfig() {
    try {
        const config = await apiRequest('/settings/clinic-type');
        isPrivateClinic = config.clinic_type === 'particular';
    } catch(e) {
        isPrivateClinic = false;
    }
    
    // Mostra ou oculta o bloco de pagamento no modal
    const paymentBlock = document.getElementById('paymentBlock');
    if (paymentBlock) {
        paymentBlock.style.display = isPrivateClinic ? 'block' : 'none';
    }
}

async function loadSelectData() {
    try {
        patients = await apiRequest('/patients/?active_only=true');
        interns = await apiRequest('/interns/?active_only=true');
        
        const pSelect = document.getElementById('selectPatient');
        const iSelect = document.getElementById('selectIntern');
        
        patients.forEach(p => {
            pSelect.options.add(new Option(p.name, p.id));
        });
        
        interns.forEach(i => {
            iSelect.options.add(new Option(i.name, i.id));
        });
    } catch(e) {}
}

function initCalendar() {
    var calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        locale: 'pt-br',
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia',
            list: 'Lista'
        },
        slotMinTime: '07:00:00', // Clínica abre às 7h
        slotMaxTime: '23:00:00', // Clínica fecha às 23h
        allDaySlot: false,
        selectable: true,
        editable: true,
        
        // Carrega eventos da nossa API
        events: async function(info, successCallback, failureCallback) {
            try {
                const events = await apiRequest(`/appointments/calendar?start=${info.startStr}&end=${info.endStr}`);
                
                // Mapear propriedades para o FullCalendar
                const fcEvents = events.map(e => {
                    let className = 'event-agendado';
                    if (e.status === 'Cancelado') className = 'event-cancelado';
                    if (e.status === 'Realizado') className = 'event-realizado';
                    if (e.status === 'Faltou') className = 'event-faltou';
                    
                    return {
                        id: e.id,
                        title: e.title,
                        start: e.start,
                        end: e.end,
                        classNames: [className],
                        extendedProps: { status: e.status }
                    };
                });
                successCallback(fcEvents);
            } catch (error) {
                failureCallback(error);
            }
        },
        
        // Clicar em horário vazio -> Criar
        select: function(info) {
            openAppointmentModal(null, info.start, info.end);
            calendar.unselect();
        },
        
        // Clicar em evento -> Editar
        eventClick: async function(info) {
            try {
                // Busca dados completos do agendamento
                const appt = await apiRequest(`/appointments/${info.event.id}`);
                openAppointmentModal(appt);
            } catch(e) {}
        },
        
        // Arrastar evento -> Atualizar horário (Apenas permitimos se não estiver Cancelado)
        eventDrop: async function(info) {
            if (info.event.extendedProps.status === 'Cancelado') {
                info.revert();
                alert('Agendamentos cancelados não podem ser movidos.');
                return;
            }
            
            try {
                await apiRequest(`/appointments/${info.event.id}`, 'PATCH', {
                    start_time: info.event.startStr,
                    end_time: info.event.endStr
                });
            } catch(e) {
                // Em caso de erro (ex: conflito de horário disparado pelo backend), reverte o bloco
                info.revert();
            }
        },
        eventResize: async function(info) {
            if (info.event.extendedProps.status === 'Cancelado') {
                info.revert();
                return;
            }
            try {
                await apiRequest(`/appointments/${info.event.id}`, 'PATCH', {
                    start_time: info.event.startStr,
                    end_time: info.event.endStr
                });
            } catch(e) {
                info.revert();
            }
        }
    });
    calendar.render();
}

// Formatador helper de Datetime Local
function toLocalISOString(dateObj) {
    const tzoffset = (new Date()).getTimezoneOffset() * 60000;
    const localISOTime = (new Date(dateObj.getTime() - tzoffset)).toISOString().slice(0, 16);
    return localISOTime;
}

function openAppointmentModal(appt = null, start = null, end = null) {
    const title = document.getElementById('modalTitle');
    const form = document.getElementById('appointmentForm');
    
    if (appt) {
        title.innerText = 'Editar Agendamento';
        document.getElementById('appointmentId').value = appt.id;
        document.getElementById('selectPatient').value = appt.patient_id;
        document.getElementById('selectIntern').value = appt.intern_id;
        document.getElementById('startTime').value = appt.start_time.slice(0, 16);
        document.getElementById('endTime').value = appt.end_time.slice(0, 16);
        
        document.getElementById('appointmentStatus').value = appt.status;
        document.getElementById('paymentMethod').value = appt.payment_method || '';
        document.getElementById('amountPaid').value = appt.amount_paid != null ? appt.amount_paid : '';
        
        document.getElementById('recurrenceToggleGroup').style.display = 'none';
        document.getElementById('isRecurring').checked = false;
        toggleRecurrence();
        
        // Se já está cancelado, não pode editar ou cancelar novamente
        if (appt.status === 'Cancelado') {
            document.getElementById('cancelArea').style.display = 'none';
            form.querySelectorAll('input, select, button[type="submit"]').forEach(el => el.disabled = true);
        } else {
            document.getElementById('cancelArea').style.display = 'block';
            form.querySelectorAll('input, select, button[type="submit"]').forEach(el => el.disabled = false);
        }
    } else {
        title.innerText = 'Novo Agendamento';
        form.reset();
        document.getElementById('appointmentId').value = '';
        
        // Pega data default ou do clique no calendário
        const s = start || new Date();
        const e = end || new Date(s.getTime() + 50*60000); // Default + 50 min
        
        document.getElementById('startTime').value = toLocalISOString(s);
        document.getElementById('endTime').value = toLocalISOString(e);
        
        document.getElementById('cancelArea').style.display = 'none';
        form.querySelectorAll('input, select, button[type="submit"]').forEach(el => el.disabled = false);

        document.getElementById('recurrenceToggleGroup').style.display = 'block';
        document.getElementById('isRecurring').checked = false;
        toggleRecurrence();
        // Marcar o dia atual como pré-selecionado na recorrência
        const currentDay = s.getDay();
        // JS getDay(): 0=Dom, 1=Seg...
        // No nosso backend: 0=Seg, 6=Dom
        const backDay = currentDay === 0 ? 6 : currentDay - 1;
        document.querySelectorAll('input[name="recurDays"]').forEach(cb => {
            cb.checked = (parseInt(cb.value) === backDay);
        });
    }
    
    openModal('appointmentModal');
}

async function saveAppointment(e) {
    e.preventDefault();
    
    const id = document.getElementById('appointmentId').value;
    const data = {
        patient_id: document.getElementById('selectPatient').value,
        intern_id: document.getElementById('selectIntern').value,
        start_time: document.getElementById('startTime').value,
        end_time: document.getElementById('endTime').value,
        payment_method: document.getElementById('paymentMethod').value || null,
        amount_paid: document.getElementById('amountPaid').value !== '' ? parseFloat(document.getElementById('amountPaid').value) : null
    };
    
    data.status = document.getElementById('appointmentStatus').value;
    
    if (!id && document.getElementById('isRecurring').checked) {
        const days = Array.from(document.querySelectorAll('input[name="recurDays"]:checked')).map(cb => parseInt(cb.value));
        const weeks = parseInt(document.getElementById('recurWeeks').value);
        if (days.length === 0) {
            alert('Por favor, selecione pelo menos um dia da semana para a recorrência.');
            return;
        }
        data.recurrence_days = days;
        data.recurrence_weeks = weeks;
    }
    
    try {
        if (id) {
            await apiRequest(`/appointments/${id}`, 'PATCH', data);
        } else {
            await apiRequest('/appointments/', 'POST', data);
        }
        closeModal('appointmentModal');
        calendar.refetchEvents();
    } catch(err) {}
}

async function cancelAppointment() {
    const id = document.getElementById('appointmentId').value;
    if (!id) return;
    
    const reason = prompt("Informe o motivo do cancelamento (Opcional):");
    if (reason === null) return; // clicou em cancelar no prompt
    
    try {
        await apiRequest(`/appointments/${id}?reason=${encodeURIComponent(reason)}`, 'DELETE');
        closeModal('appointmentModal');
        calendar.refetchEvents();
    } catch(err) {}
}

function toggleRecurrence() {
    const isRecurring = document.getElementById('isRecurring').checked;
    document.getElementById('recurrenceBlock').style.display = isRecurring ? 'block' : 'none';
}
