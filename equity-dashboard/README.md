# Equity Research Dashboard

A modern, responsive React TypeScript application for equity research and portfolio management.

## Features

- **Dashboard**: Portfolio overview with performance metrics and charts
- **Portfolio Management**: Create and manage multiple investment portfolios
- **Research Reports**: Access comprehensive equity research and analysis
- **Stock Analysis**: DCF, Comparable, Risk, and Monte Carlo analysis tools
- **Real-time Data**: Live stock quotes and market data
- **Responsive Design**: Mobile-first design with Tailwind CSS

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Server State**: TanStack React Query
- **Routing**: React Router DOM
- **Charts**: Recharts + D3
- **UI Components**: Headless UI
- **Icons**: Heroicons
- **Animations**: Framer Motion

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd equity-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp env.example .env
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API services
├── store/              # Zustand stores
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── main.tsx           # Application entry point
```

## Design System

The application uses a custom design system built on Tailwind CSS:

- **Primary Colors**: Blue palette (#eff6ff to #1e3a8a)
- **Success Colors**: Green palette (#10b981, #059669)
- **Warning Colors**: Orange palette (#f59e0b, #d97706)
- **Danger Colors**: Red palette (#ef4444, #dc2626)
- **Neutral Colors**: Gray palette (#f9fafb to #111827)

## API Integration

The dashboard is designed to work with a backend API. Configure the API base URL in your environment variables:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
