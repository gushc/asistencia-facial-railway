// Cargar asistencias al abrir la página
document.addEventListener('DOMContentLoaded', function() {
    cargarAsistencias();
    
    // Configurar eventos
    document.getElementById('btn-actualizar').addEventListener('click', cargarAsistencias);
    document.getElementById('btn-exportar').addEventListener('click', exportarCSV);
    document.getElementById('filtro-nombre').addEventListener('input', filtrarAsistencias);
    document.getElementById('filtro-fecha').addEventListener('change', filtrarAsistencias);
});

function cargarAsistencias() {
    fetch('/obtener_asistencias')
        .then(response => response.json())
        .then(data => {
            mostrarAsistencias(data.asistencias);
            actualizarEstadisticas(data.asistencias);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('lista-asistencias').innerHTML = 
                '<div class="error">Error al cargar las asistencias</div>';
        });
}

function mostrarAsistencias(asistencias) {
    const contenedor = document.getElementById('lista-asistencias');
    
    if (!asistencias || asistencias.length === 0) {
        contenedor.innerHTML = '<div class="loading">No hay asistencias registradas</div>';
        return;
    }
    
    contenedor.innerHTML = asistencias.map(asistencia => `
        <div class="asistencia-item">
            <div class="asistencia-info">
                <span class="asistencia-nombre">${asistencia.Nombre || 'Desconocido'}</span>
                <span class="asistencia-fecha">${asistencia.Fecha} • ${asistencia.Hora}</span>
            </div>
            <span class="asistencia-hora">${asistencia.Hora}</span>
            <span class="badge badge-success">✅ Registrado</span>
        </div>
    `).join('');
}

function actualizarEstadisticas(asistencias) {
    const hoy = new Date().toLocaleDateString('es-ES');
    const registrosHoy = asistencias.filter(a => a.Fecha === hoy).length;
    const ultimoRegistro = asistencias.length > 0 ? 
        `${asistencias[asistencias.length-1].Nombre} - ${asistencias[asistencias.length-1].Hora}` : 
        '---';
    
    document.getElementById('total-registros').textContent = asistencias.length;
    document.getElementById('registros-hoy').textContent = registrosHoy;
    document.getElementById('ultimo-registro').textContent = ultimoRegistro;
}

function filtrarAsistencias() {
    const filtroNombre = document.getElementById('filtro-nombre').value.toLowerCase();
    const filtroFecha = document.getElementById('filtro-fecha').value;
    
    fetch('/obtener_asistencias')
        .then(response => response.json())
        .then(data => {
            let asistenciasFiltradas = data.asistencias;
            
            if (filtroNombre) {
                asistenciasFiltradas = asistenciasFiltradas.filter(a => 
                    a.Nombre.toLowerCase().includes(filtroNombre)
                );
            }
            
            if (filtroFecha) {
                asistenciasFiltradas = asistenciasFiltradas.filter(a => 
                    a.Fecha === formatFecha(filtroFecha)
                );
            }
            
            mostrarAsistencias(asistenciasFiltradas);
        });
}

function formatFecha(fechaInput) {
    // Convertir de YYYY-MM-DD a DD/MM/YYYY
    const [year, month, day] = fechaInput.split('-');
    return `${day}/${month}/${year}`;
}

function exportarCSV() {
    fetch('/obtener_asistencias')
        .then(response => response.json())
        .then(data => {
            const csvContent = "data:text/csv;charset=utf-8," 
                + "Nombre,Fecha,Hora\n"
                + data.asistencias.map(a => 
                    `"${a.Nombre}","${a.Fecha}","${a.Hora}"`
                ).join("\n");
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "asistencias.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
}

function exportarJSON() {
    fetch('/obtener_asistencias')
        .then(response => response.json())
        .then(data => {
            const jsonContent = "data:text/json;charset=utf-8," 
                + encodeURIComponent(JSON.stringify(data.asistencias, null, 2));
            
            const link = document.createElement("a");
            link.setAttribute("href", jsonContent);
            link.setAttribute("download", "asistencias.json");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
}

function imprimirLista() {
    window.print();
}