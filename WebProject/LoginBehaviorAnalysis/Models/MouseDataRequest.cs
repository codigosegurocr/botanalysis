using System;
using System.Collections.Generic;

namespace LoginBehaviorAnalysis.Models
{
    public class MouseDataRequest
    {
        public string UserId { get; set; }  // Identificador del usuario
        public List<MouseEvent> Events { get; set; }  // Lista de eventos del mouse
        public int Label { get; set; } = 0; // Aquí agregas la etiqueta
    }

    public class MouseEvent
    {
        public long Timestamp { get; set; }  // Timestamp del evento
        public string Type { get; set; }  // Tipo de evento (mousemove, click, keydown, etc.)
        public float X { get; set; }  // Posición X del mouse
        public float Y { get; set; }  // Posición Y del mouse
        public string Button { get; set; }  // Botón presionado (left, right, middle, etc.)
        public string Element { get; set; }  // Elemento donde ocurrió el evento
        public int ScrollX { get; set; }  // Desplazamiento horizontal
        public int ScrollY { get; set; }  // Desplazamiento vertical
        public int IdleTime { get; set; }  // Tiempo de inactividad antes del evento
    }
}
