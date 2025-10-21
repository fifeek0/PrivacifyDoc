FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["PrivacifyDoc.Api.csproj", "PrivacifyDoc.Api/"]
COPY ["../PrivacifyDoc.Core/PrivacifyDoc.Core.csproj", "PrivacifyDoc.Core/"]
COPY ["../PrivacifyDoc.Infrastructure/PrivacifyDoc.Infrastructure.csproj", "PrivacifyDoc.Infrastructure/"]
RUN dotnet restore "PrivacifyDoc.Api/PrivacifyDoc.Api.csproj"
COPY . .
WORKDIR "/src/PrivacifyDoc.Api"
RUN dotnet build "PrivacifyDoc.Api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "PrivacifyDoc.Api.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "PrivacifyDoc.Api.dll"]