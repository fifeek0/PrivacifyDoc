using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MongoDB.Driver;
using PrivacifyDoc.Application;
using PrivacifyDoc.Application.Commands;
using PrivacifyDoc.Application.Queries;
using PrivacifyDoc.Application.Handlers;
using PrivacifyDoc.Application.Interfaces;
using PrivacifyDoc.Domain.Entities;
using PrivacifyDoc.Domain.Repositories;
using PrivacifyDoc.Domain.Services;
using PrivacifyDoc.Infrastructure.Messaging;
using PrivacifyDoc.Infrastructure.Persistence;
using PrivacifyDoc.Infrastructure.Storage;
using PrivacifyDoc.Api.BackgroundServices;

var builder = WebApplication.CreateBuilder(args);

// Configuration
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Database
var mongoConnectionString = builder.Configuration.GetConnectionString("MongoDB") ?? "mongodb://localhost:27017";
builder.Services.AddSingleton<IMongoClient>(new MongoClient(mongoConnectionString));
builder.Services.AddSingleton(sp => sp.GetRequiredService<IMongoClient>().GetDatabase("PrivacifyDoc"));

// Services and Application Layer
builder.Services.AddSingleton<Dispatcher>();
builder.Services.AddSingleton<IFileStorage, LocalFileStorage>();
builder.Services.AddSingleton<IMessagePublisher, RabbitMqPublisher>();
builder.Services.AddSingleton<IDocumentRepository, DocumentRepository>();

// Command and Query Handlers
builder.Services.AddTransient<ICommandHandler<UploadDocumentCommand>, UploadDocumentCommandHandler>();
builder.Services.AddTransient<IQueryHandler<GetDocumentStatusQuery, DocumentStatusResponse?>, GetDocumentStatusQueryHandler>();
builder.Services.AddTransient<IQueryHandler<GetDocumentByIdQuery, Document?>, GetDocumentByIdQueryHandler>();

// Background Services
builder.Services.AddHostedService<DocumentResultConsumer>();

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