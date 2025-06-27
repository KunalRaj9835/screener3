# Screener Frontend

A modern financial screening application built with Next.js 14+ using the App Router. This frontend provides an intuitive interface for creating, managing, and executing financial screening queries.

## 🚀 Features

- **Query Builder**: Interactive interface for creating custom screening criteria
- **Real-time Results**: Dynamic display of screening results with filtering and sorting
- **Query Management**: Save, edit, and organize your screening queries
- **Responsive Design**: Optimized for desktop and mobile devices
- **Modern UI**: Built with Tailwind CSS for a clean, professional interface

## 🛠 Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Font**: Geist (Vercel's font family)
- **Linting**: ESLint with Next.js configuration

## 📁 Project Structure

```
screener-frontend/
├── app/
│   ├── (route)/               # Route groups
│   ├── api/                   # API route handlers
│   │   ├── data/             # Data-related endpoints
│   │   ├── saved-queries/    # Saved queries management
│   │   └── update/           # Update operations
│   ├── my-query/             # Query builder pages
│   ├── query-result/         # Results display pages
│   └── save-query/           # Query saving functionality
├── components/
│   ├── MyQuery.tsx           # Query builder component
│   ├── Navbar.tsx            # Navigation bar
│   ├── QueryResult.tsx       # Results display
│   ├── Save.tsx              # Save functionality
│   ├── SearchPage.tsx        # Search interface
│   └── Sidebar.tsx           # Side navigation
└── public/                   # Static assets
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, pnpm, or bun
- Backend API server running (separate repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd screener-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   Configure your environment variables:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000) to see the application.

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## 🎯 Key Components

### MyQuery Component
Interactive query builder allowing users to:
- Set screening criteria
- Configure filters and parameters
- Preview query logic

### QueryResult Component
Results display featuring:
- Sortable and filterable data tables
- Export functionality
- Pagination for large datasets

### Save Component
Query management system for:
- Saving custom queries
- Organizing query collections
- Quick access to frequently used screens

## 🌐 API Integration

This frontend connects to a separate backend API. Ensure your backend server is running and accessible at the configured `NEXT_PUBLIC_API_BASE_URL`.

Key API endpoints used:
- `/api/queries` - Query management
- `/api/screen` - Execute screening
- `/api/data` - Data retrieval
- `/api/saved-queries` - Saved query operations

## 📱 Responsive Design

The application is fully responsive and optimized for:
- Desktop computers (1024px+)
- Tablets (768px - 1023px)
- Mobile devices (320px - 767px)

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect your repository** to Vercel
2. **Configure environment variables** in the Vercel dashboard
3. **Deploy** - Vercel will automatically build and deploy your app

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- Digital Ocean App Platform
- AWS Amplify

## 🛠 Development

### Code Style
- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting (if configured)

### File Naming Conventions
- Components: PascalCase (`MyQuery.tsx`)
- Pages: kebab-case (`my-query/page.tsx`)
- Utilities: camelCase (`utils/formatData.ts`)

## 📚 Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs) - Learn about Next.js features and API
- [Tailwind CSS](https://tailwindcss.com/docs) - Utility-first CSS framework
- [TypeScript](https://www.typescriptlang.org/docs) - JavaScript with types

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Review the documentation
3. Contact the development team

---

**Note**: This is the frontend application only. Make sure to set up and run the corresponding backend API server for full functionality.