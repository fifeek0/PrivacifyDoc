using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MongoDB.Driver;
using PrivacifyDoc.Api.CQRS;
using PrivacifyDoc.Api.CQRS.Commands;
using PrivacifyDoc.Api.CQRS.Dispatcher;
using PrivacifyDoc.Api.CQRS.Handlers;
using PrivacifyDoc.Api.Infrastructure;

var builder = WebApplication.CreateBuilder(args);

// Konfiguracja
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Baza danych
var mongoConnectionString = builder.Configuration.GetConnectionString("MongoDB") ?? "mongodb://localhost:27017";
builder.Services.AddSingleton<IMongoClient>(new MongoClient(mongoConnectionString));
builder.Services.AddSingleton(sp => sp.GetRequiredService<IMongoClient>().GetDatabase("PrivacifyDoc"));

// Usługi i CQRS
builder.Services.AddSingleton<Dispatcher>();
builder.Services.AddSingleton<IFileStorage, FileSystemStorage>();
builder.Services.AddSingleton<IMessagePublisher, RabbitMqPublisher>();

// Handlery
builder.Services.AddTransient<ICommandHandler<AnonymizeDocumentCommand>, AnonymizeDocumentCommandHandler>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();
app.Run();