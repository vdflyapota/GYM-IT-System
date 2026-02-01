# Documentation Index

Welcome to the GYM IT System documentation. Here you'll find everything you need to understand, develop, and deploy this microservices-based gym management platform.

## 📖 Core Documentation

### Getting Started
- **[Main README](../README.md)** - Quick start guide and project overview
- **[Final Implementation Summary](../FINAL_SUMMARY.md)** - Complete overview of all implemented features

### Architecture & Design
- **[Architecture Overview](./architecture/ARCHITECTURE.md)** - System design, patterns, and diagrams
- **[Microservices Guide](./guides/MICROSERVICES.md)** - Complete description of each microservice

### Deployment & Operations
- **[Kubernetes Deployment](./guides/K8S_DEPLOYMENT.md)** - Production deployment to Kubernetes
- **[Migration Summary](./guides/MIGRATION_SUMMARY.md)** - Migration history and changes

### Features & Guides
- **[Role-Based UI Permissions](./guides/ROLE_BASED_UI_PERMISSIONS.md)** - RBAC implementation details
- **[Tournament User Guide](./guides/TOURNAMENT_USER_GUIDE.md)** - How to use tournament features
- **[Implementation Summary](./guides/IMPLEMENTATION_SUMMARY.md)** - Detailed implementation notes

## 🔍 Archived Documentation

See `./archived/` for legacy fix documents and notes from development:
- Individual fix documents (TOURNAMENT_FIX.md, ADMIN_PANEL_FIX.md, etc.)
- These are preserved for reference but all improvements are consolidated in current docs

## 📋 Service Documentation

Each microservice has its own README in `services/{service-name}/`:

```
services/
├── api-gateway/        → API Gateway documentation
├── auth-service/       → Authentication service documentation
├── user-service/       → User management documentation
├── tournament-service/ → Tournament engine documentation
└── notification-service/ → Notifications documentation
```

## 🚀 Quick Navigation

**I want to...**

- **Run the application** → See [Main README](../README.md#-getting-started)
- **Understand the architecture** → Read [Architecture Overview](./architecture/ARCHITECTURE.md)
- **Deploy to production** → Check [Kubernetes Deployment](./guides/K8S_DEPLOYMENT.md)
- **Work on a specific service** → Find service docs in `services/{service-name}/`
- **Learn about features** → See specific guides in `./guides/`
- **Check what changed** → Review [Implementation Summary](./guides/IMPLEMENTATION_SUMMARY.md)

## 📚 Documentation Standards

This project uses Markdown for all documentation:
- All docs follow a consistent structure
- Code examples are included where relevant
- Diagrams help explain complex concepts
- Links between documents make navigation easy

## ❓ Need Help?

1. Check the relevant guide in `./guides/`
2. Look at service-specific README in `services/{service-name}/`
3. Review the main [README.md](../README.md)
4. Check [FINAL_SUMMARY.md](../FINAL_SUMMARY.md) for feature details

---

**Last Updated:** February 2026  
**Status:** Active Development
