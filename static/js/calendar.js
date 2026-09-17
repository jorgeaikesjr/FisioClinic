let calendar;
let patients = [];
let interns = [];
let isPrivateClinic = false;

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
    
    // Mostra ou oculta o bloco de pagamento no modal (apenas Particular)
    const paymentBlock = document.getElementById('paymentBlock');
    if (paymentBlock) {
        paymentBlock.style.display = isPrivateClinic ? 'block' : 'none';
    }
    
    // Mostra ou oculta o bloco de categoria no modal (apenas Escola)
    const categoryGroup = document.getElementById('categoryGroup');
    if (categoryGroup) {
        categoryGroup.style.display = isPrivateClinic ? 'none' : 'block';
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
        headerToolbar: false, // Toolbar customizada externa
        locale: 'pt-br',
        slotMinTime: '07:00:00', // Clínica abre às 7h
        slotMaxTime: '23:00:00', // Clínica fecha às 23h
        allDaySlot: false,
        nowIndicator: true,
        selectable: true,
        editable: true,
        longPressDelay: 100,
        selectLongPressDelay: 100,
        
        // Customização do cabeçalho das colunas dos dias
        dayHeaderContent: function(arg) {
            const date = arg.date;
            const isToday = arg.isToday;
            
            const weekdays = ['DOM.', 'SEG.', 'TER.', 'QUA.', 'QUI.', 'SEX.', 'SÁB.'];
            const dayName = weekdays[date.getDay()];
            
            const dayNum = String(date.getDate()).padStart(2, '0');
            const monthNum = String(date.getMonth() + 1).padStart(2, '0');
            const dateFormatted = `${dayNum}/${monthNum}`;
            
            const weekdayDisplay = isToday ? `${dayName.replace('.', '')} (HOJE)` : dayName;
            
            return {
                html: `
                    <div class="fc-custom-col-header ${isToday ? 'fc-today-header' : ''}">
                        ${isToday ? '<span class="fc-today-dot"></span>' : ''}
                        <span class="fc-col-weekday">${weekdayDisplay}</span>
                        <span class="fc-col-date">${dateFormatted}</span>
                    </div>
                `
            };
        },
        
        // Customização dos cards de agendamento (Event Content alinhado aos Status)
        eventContent: function(arg) {
            const props = arg.event.extendedProps || {};
            const status = props.status || 'Agendado';
            const category = props.category || '';
            const internName = props.intern_name || '';
            const patientName = props.patient_name || arg.event.title.split(' - ')[0] || 'Paciente';
            
            const startTimeStr = arg.event.start ? arg.event.start.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';
            const endTimeStr = arg.event.end ? arg.event.end.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';
            const timeRange = `${startTimeStr} - ${endTimeStr}`;
            
            let themeClass = 'card-theme-blue';
            let tagText = category ? category.toUpperCase() : 'AGENDADO';
            
            if (status === 'Cancelado') {
                themeClass = 'card-theme-gray';
                tagText = 'CANCELADO';
            } else if (status === 'Faltou') {
                themeClass = 'card-theme-red';
                tagText = 'FALTOU';
            } else if (status === 'Falta Justificada') {
                themeClass = 'card-theme-amber';
                tagText = 'JUSTIFICADA';
            } else if (status === 'Realizado') {
                themeClass = 'card-theme-emerald';
                if (!category) tagText = 'REALIZADO';
            } else {
                themeClass = 'card-theme-blue';
                if (!category) tagText = 'AGENDADO';
            }
            
            return {
                html: `
                    <div class="cal-event-card ${themeClass}">
                        <div class="card-top-row">
                            <span class="card-time-text">${timeRange}</span>
                            <span class="card-tag-pill">${tagText}</span>
                        </div>
                        <div class="card-patient-name" title="${patientName}">${patientName}</div>
                        <div class="card-footer-sub">
                            <span class="card-intern-name" title="${internName}">${internName ? (internName.startsWith('Dr') ? internName : 'Dr(a). ' + internName) : 'Atendimento'}</span>
                        </div>
                    </div>
                `
            };
        },
        
        // Atualiza a toolbar externa quando o período ou view mudar
        datesSet: function(info) {
            updateCalendarToolbarInfo(info);
        },
        
        // Carrega eventos da nossa API
        events: async function(info, successCallback, failureCallback) {
            try {
                const events = await apiRequest(`/appointments/calendar?start=${info.startStr}&end=${info.endStr}`);
                
                const fcEvents = events.map(e => ({
                    id: e.id,
                    title: e.title,
                    start: e.start,
                    end: e.end,
                    extendedProps: {
                        status: e.status,
                        patient_name: e.patient_name,
                        intern_name: e.intern_name,
                        category: e.category
                    }
                }));
                
                successCallback(fcEvents);
                updateSummaryFooter(fcEvents);
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
                const appt = await apiRequest(`/appointments/${info.event.id}`);
                openAppointmentModal(appt);
            } catch(e) {}
        },
        
        // Arrastar evento -> Atualizar horário
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
                calendar.refetchEvents();
            } catch(e) {
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
                calendar.refetchEvents();
            } catch(e) {
                info.revert();
            }
        }
    });
    
    calendar.render();
}

// Controles externos de navegação
function navCalendar(action) {
    if (!calendar) return;
    if (action === 'prev') calendar.prev();
    if (action === 'next') calendar.next();
    if (action === 'today') calendar.today();
}

function changeCalView(viewName) {
    if (!calendar) return;
    calendar.changeView(viewName);
    
    document.querySelectorAll('.cal-pill').forEach(btn => btn.classList.remove('active'));
    if (viewName === 'dayGridMonth') document.getElementById('pillMonth')?.classList.add('active');
    if (viewName === 'timeGridWeek') document.getElementById('pillWeek')?.classList.add('active');
    if (viewName === 'timeGridDay') document.getElementById('pillDay')?.classList.add('active');
}

// Atualizar título do período e número da semana na toolbar externa
function updateCalendarToolbarInfo(info) {
    const start = info.start;
    const end = new Date(info.end.getTime() - 1); // Subtrai 1ms pois o end do FC é exclusivo
    const viewType = info.view.type;
    
    const months = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
    
    let titleStr = '';
    if (viewType === 'timeGridWeek') {
        if (start.getMonth() === end.getMonth()) {
            titleStr = `${start.getDate()} – ${end.getDate()} de ${months[start.getMonth()]} de ${start.getFullYear()}`;
        } else {
            titleStr = `${start.getDate()} de ${months[start.getMonth()]} – ${end.getDate()} de ${months[end.getMonth()]} de ${start.getFullYear()}`;
        }
    } else if (viewType === 'timeGridDay') {
        const fullMonths = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
        titleStr = `${start.getDate()} de ${fullMonths[start.getMonth()]} de ${start.getFullYear()}`;
    } else {
        const fullMonths = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        titleStr = `${fullMonths[start.getMonth()]} de ${start.getFullYear()}`;
    }
    
    const titleEl = document.getElementById('calDateTitle');
    if (titleEl) titleEl.innerText = titleStr;
    
    const weekNum = getISOWeekNumber(start);
    const weekEl = document.getElementById('calWeekNumber');
    if (weekEl) {
        weekEl.innerText = viewType === 'timeGridWeek' ? `(Semana ${weekNum})` : '';
    }
}

function getISOWeekNumber(d) {
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const dayNum = date.getUTCDay() || 7;
    date.setUTCDate(date.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
}

// Atualizar métricas de resumo no rodapé (sempre mostra dados da semana atual)
function updateSummaryFooter(eventsList) {
    // Calcula o início (Domingo) e fim (Sábado) da semana atual
    const now = new Date();
    const dayOfWeek = now.getDay(); // 0=Dom, 6=Sáb
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - dayOfWeek);
    weekStart.setHours(0, 0, 0, 0);
    
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 7);
    weekEnd.setHours(0, 0, 0, 0);
    
    // Filtra apenas eventos da semana atual, excluindo cancelados
    const weekEvents = eventsList.filter(e => {
        if (e.extendedProps.status === 'Cancelado') return false;
        const eventStart = new Date(e.start);
        return eventStart >= weekStart && eventStart < weekEnd;
    });
    
    const totalCount = weekEvents.length;
    
    const countEl = document.getElementById('calSummaryCount');
    if (countEl) countEl.innerText = totalCount;
    
    const maxCapacity = 40;
    let occPercent = Math.min(100, Math.round((totalCount / maxCapacity) * 100));
    if (totalCount > 0 && occPercent === 0) occPercent = 10;
    
    const occEl = document.getElementById('calSummaryOcc');
    if (occEl) occEl.innerText = `${occPercent}%`;
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
        
        const pSelect = document.getElementById('selectPatient');
        const iSelect = document.getElementById('selectIntern');

        if (!Array.from(pSelect.options).some(opt => opt.value === appt.patient_id)) {
            const pName = appt.patient ? appt.patient.name : 'Paciente Inativo';
            pSelect.options.add(new Option(`${pName} (Inativo)`, appt.patient_id));
        }
        
        if (!Array.from(iSelect.options).some(opt => opt.value === appt.intern_id)) {
            const labelInactive = isPrivateClinic ? 'Profissional Inativo' : 'Estagiário Inativo';
            const iName = appt.intern ? appt.intern.name : labelInactive;
            iSelect.options.add(new Option(`${iName} (Inativo)`, appt.intern_id));
        }

        pSelect.value = appt.patient_id;
        iSelect.value = appt.intern_id;
        document.getElementById('startTime').value = appt.start_time.slice(0, 16);
        document.getElementById('endTime').value = appt.end_time.slice(0, 16);
        
        document.getElementById('appointmentStatus').value = appt.status;
        document.getElementById('paymentMethod').value = appt.payment_method || '';
        document.getElementById('amountPaid').value = appt.amount_paid != null ? appt.amount_paid : '';
        document.getElementById('appointmentCategory').value = appt.category || '';
        
        document.getElementById('recurrenceToggleGroup').style.display = 'none';
        document.getElementById('isRecurring').checked = false;
        toggleRecurrence();
        
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
        
        if (interns.length === 1) {
            document.getElementById('selectIntern').value = interns[0].id;
        }
        
        const s = start || new Date();
        const e = end || new Date(s.getTime() + 50*60000);
        
        document.getElementById('startTime').value = toLocalISOString(s);
        document.getElementById('endTime').value = toLocalISOString(e);
        
        document.getElementById('cancelArea').style.display = 'none';
        form.querySelectorAll('input, select, button[type="submit"]').forEach(el => el.disabled = false);

        document.getElementById('recurrenceToggleGroup').style.display = 'block';
        document.getElementById('isRecurring').checked = false;
        toggleRecurrence();

        const currentDay = s.getDay();
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
        amount_paid: document.getElementById('amountPaid').value !== '' ? parseFloat(document.getElementById('amountPaid').value) : null,
        category: !isPrivateClinic ? (document.getElementById('appointmentCategory').value || null) : null
    };
    
    data.status = document.getElementById('appointmentStatus').value;
    
    if (!id && document.getElementById('isRecurring').checked) {
        const days = Array.from(document.querySelectorAll('input[name="recurDays"]:checked')).map(cb => parseInt(cb.value));
        const weeks = parseInt(document.getElementById('recurWeeks').value);
        const period = document.getElementById('recurrencePeriod').value;
        if (days.length === 0) {
            alert('Por favor, selecione pelo menos um dia da semana para a recorrência.');
            return;
        }
        data.recurrence_days = days;
        data.recurrence_weeks = weeks;
        data.recurrence_period = period;
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
    if (reason === null) return;
    
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

