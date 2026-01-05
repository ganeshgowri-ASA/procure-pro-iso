# Procure-Pro-ISO Deployment Guide

This guide covers deploying the Procure-Pro-ISO application to production.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Vercel (CDN)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            React Frontend (Static Build)              │  │
│  │  - Dashboard, Equipment, RFQ, Vendors, Evaluations   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (Future)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Python/Flask REST API                    │  │
│  │  - Authentication, RFQ CRUD, Vendor Management       │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL                         │  │
│  │  - Users, Projects, RFQs, Vendors, Evaluations       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Deployment

### Option 1: Vercel (Recommended)

#### Via GitHub Integration

1. **Connect Repository**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository

2. **Configure Build Settings**
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically

#### Via CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Deploy (first time - links project)
vercel

# Deploy to production
vercel --prod
```

### Option 2: Netlify

1. **Build Command**: `npm run build`
2. **Publish Directory**: `dist`
3. **Node Version**: 18.x

Add `netlify.toml`:

```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Option 3: AWS S3 + CloudFront

```bash
# Build
cd frontend && npm run build

# Sync to S3
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Option 4: Docker

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# frontend/nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Environment Configuration

### Frontend Environment Variables

Create `.env.production` for production builds:

```env
VITE_API_URL=https://api.your-domain.com
VITE_API_VERSION=v1
VITE_ENABLE_ANALYTICS=true
```

### Vercel Environment Variables

Set via Vercel Dashboard or CLI:

```bash
vercel env add VITE_API_URL
vercel env add VITE_API_VERSION
```

## Backend Deployment (Future)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/procurepro
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=procurepro

volumes:
  postgres_data:
```

### Cloud Platform Options

| Platform | Frontend | Backend | Database |
|----------|----------|---------|----------|
| Vercel + Railway | Vercel | Railway | Railway PostgreSQL |
| AWS | CloudFront + S3 | ECS/Lambda | RDS PostgreSQL |
| GCP | Cloud CDN | Cloud Run | Cloud SQL |
| Azure | Static Web Apps | App Service | Azure PostgreSQL |

## Domain Configuration

### Custom Domain (Vercel)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS:
   - A Record: `76.76.21.21`
   - CNAME: `cname.vercel-dns.com`

### SSL/TLS

- Vercel: Automatic SSL via Let's Encrypt
- Netlify: Automatic SSL
- Custom: Use Cloudflare or Let's Encrypt

## Monitoring & Analytics

### Recommended Tools

- **Error Tracking**: Sentry
- **Analytics**: Plausible, Posthog, or Google Analytics
- **Uptime**: UptimeRobot, Pingdom

### Sentry Integration

```bash
npm install @sentry/react
```

```typescript
// src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: import.meta.env.MODE,
});
```

## Performance Optimization

### Build Optimizations

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
        },
      },
    },
  },
});
```

### CDN Caching

Assets in `/assets` have immutable cache headers (1 year).

## Security Checklist

- [ ] Enable HTTPS only
- [ ] Set security headers (CSP, X-Frame-Options, etc.)
- [ ] Configure CORS for API
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting on API
- [ ] Implement authentication (future)
- [ ] Regular dependency updates

## Troubleshooting

### Build Failures

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 404 on Page Refresh

Ensure rewrites are configured for SPA routing. See `vercel.json` or nginx config.

### Environment Variables Not Loading

- Prefix with `VITE_` for Vite
- Rebuild after changing env vars
- Check `.env` file location

## Support

For deployment issues, check:
- [Vercel Documentation](https://vercel.com/docs)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
