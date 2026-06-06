namespace LoginBehaviorAnalysis.Models
{
    public class MouseDataRequestMod1
    {
        public string UserId { get; set; } = "user123";
        public List<MouseEventMod1> Events { get; set; } = new List<MouseEventMod1>();
        public int Label { get; set; } = 0;
    }

    public class MouseEventMod1
    {
        public long Timestamp { get; set; }
        public string Type { get; set; }  // 'mousemove' o 'click'
        public double X { get; set; }
        public double Y { get; set; }
        public double Speed { get; set; }
        public double Acceleration { get; set; }
        public double Velocity { get; set; }
        public bool Correction { get; set; }
        public bool AccelerationDetected { get; set; }
        public bool DecelerationDetected { get; set; }
        public int IdleTime { get; set; }
        public string Button { get; set; } = "";  // 'left', 'middle', 'right' o vacío para mousemove
    }
}
