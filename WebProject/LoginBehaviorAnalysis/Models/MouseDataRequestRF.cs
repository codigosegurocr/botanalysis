namespace LoginBehaviorAnalysis.Models
{
    public class MouseDataRequestRF
    {
        public string UserId { get; set; }
        public List<MouseEventRF> Events { get; set; }
        public double TiempoTotal { get; set; }
        public double X_Start { get; set; }
        public double Y_Start { get; set; }
        public double X_End { get; set; }
        public double Y_End { get; set; }
        public int Label { get; set; }

    }

    public class MouseEventRF
    {
        public long Timestamp { get; set; }
        public double X { get; set; }
        public double Y { get; set; }
        public double DeltaX { get; set; }
        public double DeltaY { get; set; }
        public double Distance { get; set; }
        public double Direction { get; set; }
        public double TimeElapsed { get; set; }
        public double Speed { get; set; }
        public double Acceleration { get; set; }
        public bool CurvatureDetected { get; set; }
        public bool AccelerationDetected { get; set; }
        public bool DecelerationDetected { get; set; }
        public double IdleTime { get; set; }
    }

}
