namespace LoginBehaviorAnalysis.Models
{
    public class MouseDataRequestModSVM
    {
        public string UserId { get; set; } = "user123";
        public List<MouseEventModSVM> Events { get; set; } = new List<MouseEventModSVM>();
        public int Label { get; set; } = 0;
    }
    public class MouseEventModSVM
    {
        public long Timestamp { get; set; }
        public string Type { get; set; }  // 'mousemove' o 'click'
        public double X { get; set; }
        public double Y { get; set; }
        public double Speed { get; set; }
        public double Acceleration { get; set; }
        public bool CurvatureDetected { get; set; } // ✅ Nuevo campo para detectar cambios de dirección
        public bool ErrorMovement { get; set; } // ✅ Nuevo campo para detectar errores en el movimiento
        public bool Correction { get; set; }
        public bool AccelerationDetected { get; set; }
        public bool DecelerationDetected { get; set; }
        public int IdleTime { get; set; }
        public string Button { get; set; } = "";  // 'left', 'middle', 'right' o vacío para mousemove
    }
}
