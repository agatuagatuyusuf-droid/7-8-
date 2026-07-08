FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 5000

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/AutoDoor.Api/AutoDoor.Api.csproj", "src/AutoDoor.Api/"]
COPY ["src/AutoDoor.Domain/AutoDoor.Domain.csproj", "src/AutoDoor.Domain/"]
COPY ["src/AutoDoor.Infrastructure/AutoDoor.Infrastructure.csproj", "src/AutoDoor.Infrastructure/"]
RUN dotnet restore "src/AutoDoor.Api/AutoDoor.Api.csproj"
COPY . .
WORKDIR "/src/src/AutoDoor.Api"
RUN dotnet build "AutoDoor.Api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AutoDoor.Api.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AutoDoor.Api.dll"]
