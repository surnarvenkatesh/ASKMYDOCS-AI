param location string = resourceGroup().location
param backendImage string
param frontendImage string
param containerAppsEnvId string

@secure()
param databaseUrl string
@secure()
param redisUrl string
@secure()
param jwtSecretKey string
@secure()
param openaiApiKey string

resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'askmydocs-backend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      secrets: [
        { name: 'database-url', value: databaseUrl }
        { name: 'redis-url', value: redisUrl }
        { name: 'jwt-secret-key', value: jwtSecretKey }
        { name: 'openai-api-key', value: openaiApiKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImage
          resources: { cpu: json('1.0'), memory: '2Gi' }
          env: [
            { name: 'APP_ENV', value: 'production' }
            { name: 'LLM_PROVIDER', value: 'openai' }
            { name: 'DATABASE_URL', secretRef: 'database-url' }
            { name: 'REDIS_URL', secretRef: 'redis-url' }
            { name: 'JWT_SECRET_KEY', secretRef: 'jwt-secret-key' }
            { name: 'OPENAI_API_KEY', secretRef: 'openai-api-key' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8000 }
              periodSeconds: 30
            }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 5 }
    }
  }
}

resource frontendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'askmydocs-frontend'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvId
    configuration: {
      ingress: { external: true, targetPort: 3000, transport: 'auto' }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'NEXT_PUBLIC_API_BASE_URL', value: 'https://${backendApp.properties.configuration.ingress.fqdn}/api/v1' }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 3 }
    }
  }
}
