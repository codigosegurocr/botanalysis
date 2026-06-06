var builder = WebApplication.CreateBuilder(args);

// Agrega servicios de MVC con soporte para JSON
builder.Services.AddControllersWithViews()
                .AddJsonOptions(options =>
                {
                    // Configuración adicional si es necesario
                    options.JsonSerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase;
                });

var app = builder.Build();

// Configura middleware para recibir JSON
app.UseRouting();
app.UseStaticFiles();
app.UseAuthorization();

// Configurar las rutas para los controladores
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Account}/{action=Login}/{id?}"
);


app.Run();
