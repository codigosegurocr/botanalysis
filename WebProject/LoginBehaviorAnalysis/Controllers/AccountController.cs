using LoginBehaviorAnalysis.Models;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml;
using Formatting = Newtonsoft.Json.Formatting;

namespace LoginBehaviorAnalysis.Controllers
{
    public class AccountController : Controller
    {
        private readonly string _jsonFilePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "data", "mouse_data.json");

        public IActionResult Login()
        {
            return View();
        }

        [HttpPost]
        [Route("Account/CaptureMouseData")]
        public IActionResult CaptureMouseData([FromBody] MouseDataRequest mouseDataRequest)
        {
            if (mouseDataRequest?.Events != null && mouseDataRequest.Events.Any())
            {
                // Guardar los eventos en el archivo JSON
                SaveMouseDataToJson(mouseDataRequest);
            }
            return Ok(new { message = "Data received successfully" });
        }

        // Método para guardar los eventos en un archivo JSON
        private void SaveMouseDataToJson(MouseDataRequest mouseDataRequest)
        {
            // Leer los datos existentes si el archivo ya existe
            List<MouseDataRequest> existingData = new List<MouseDataRequest>();
            if (System.IO.File.Exists(_jsonFilePath))
            {
                var jsonData = System.IO.File.ReadAllText(_jsonFilePath);
                existingData = JsonConvert.DeserializeObject<List<MouseDataRequest>>(jsonData);
            }

            // Agregar los nuevos datos al conjunto existente
            existingData.Add(mouseDataRequest);

            // Serializar y guardar los datos actualizados en el archivo JSON
            var newJsonData = JsonConvert.SerializeObject(existingData, Formatting.Indented);
            System.IO.File.WriteAllText(_jsonFilePath, newJsonData);
        }

        [HttpPost]
        [Route("Account/CaptureMouseDataMod1")]
        public IActionResult CaptureMouseDataMod1([FromBody] MouseDataRequestMod1 mouseDataRequest)
        {
            if (mouseDataRequest?.Events != null && mouseDataRequest.Events.Any())
            {
                // Guardar los eventos en el archivo JSON
                SaveMouseDataToJsonMod1(mouseDataRequest);
            }
            return Ok(new { message = "Data received successfully" });
        }

        [HttpPost]
        [Route("Account/CaptureMouseDataModSVM")]
        public IActionResult CaptureMouseDataModSVM([FromBody] MouseDataRequestModSVM mouseDataRequest)
        {
            if (mouseDataRequest?.Events != null && mouseDataRequest.Events.Any())
            {
                // Guardar los eventos en el archivo JSON
                SaveMouseDataToJsonModSVM(mouseDataRequest);
            }
            return Ok(new { message = "Data received successfully" });
        }

        // Método para guardar los eventos en un archivo JSON
        private static readonly object fileLock = new object(); // Global lock

        private void SaveMouseDataToJsonMod1(MouseDataRequestMod1 mouseDataRequest)
        {
            lock (fileLock)
            {
                List<MouseDataRequestMod1> existingData = new List<MouseDataRequestMod1>();

                if (System.IO.File.Exists(_jsonFilePath))
                {
                    var jsonData = System.IO.File.ReadAllText(_jsonFilePath);
                    existingData = JsonConvert.DeserializeObject<List<MouseDataRequestMod1>>(jsonData) ?? new List<MouseDataRequestMod1>();
                }

                existingData.Add(mouseDataRequest);

                var newJsonData = JsonConvert.SerializeObject(existingData, Formatting.Indented);
                System.IO.File.WriteAllText(_jsonFilePath, newJsonData);
            }
        }

        [HttpPost]
        [Route("Account/CaptureMouseDataRF")]
        public IActionResult CaptureMouseDataRF([FromBody] MouseDataRequestRF mouseDataRequest)
        {
            if (mouseDataRequest?.Events != null && mouseDataRequest.Events.Any())
            {
                // Guardar los eventos en el archivo JSON
                SaveMouseDataToJsonModRF(mouseDataRequest);
            }
            return Ok(new { message = "Data received successfully" });
        }



        private void SaveMouseDataToJsonModSVM(MouseDataRequestModSVM mouseDataRequest)
        {
            // Leer los datos existentes si el archivo ya existe
            List<MouseDataRequestModSVM> existingData = new List<MouseDataRequestModSVM>();
            if (System.IO.File.Exists(_jsonFilePath))
            {
                using (var reader = new StreamReader(_jsonFilePath))
                {
                    var jsonData = reader.ReadToEnd();
                    existingData = JsonConvert.DeserializeObject<List<MouseDataRequestModSVM>>(jsonData) ?? new List<MouseDataRequestModSVM>();
                }
            }

            // Agregar los nuevos datos al conjunto existente
            existingData.Add(mouseDataRequest);

            // Serializar y guardar los datos actualizados en el archivo JSON
            using (var writer = new StreamWriter(_jsonFilePath, false)) // `false` sobrescribe el archivo
            {
                var newJsonData = JsonConvert.SerializeObject(existingData, Formatting.Indented);
                writer.Write(newJsonData);
            }
        }

        private void SaveMouseDataToJsonModRF(MouseDataRequestRF mouseDataRequest)
        {
            // Leer los datos existentes si el archivo ya existe
            List<MouseDataRequestRF> existingData = new List<MouseDataRequestRF>();
            if (System.IO.File.Exists(_jsonFilePath))
            {
                using (var reader = new StreamReader(_jsonFilePath))
                {
                    var jsonData = reader.ReadToEnd();
                    existingData = JsonConvert.DeserializeObject<List<MouseDataRequestRF>>(jsonData) ?? new List<MouseDataRequestRF>();
                }
            }

            // Agregar los nuevos datos al conjunto existente
            existingData.Add(mouseDataRequest);

            // Serializar y guardar los datos actualizados en el archivo JSON
            using (var writer = new StreamWriter(_jsonFilePath, false)) // `false` sobrescribe el archivo
            {
                var newJsonData = JsonConvert.SerializeObject(existingData, Formatting.Indented);
                writer.Write(newJsonData);
            }
        }


    }
}
