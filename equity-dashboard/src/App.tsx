import { Routes, Route } from 'react-router-dom'

// Simple test component
function TestComponent() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-blue-600 mb-4">
        Equity Research Dashboard
      </h1>
      <p className="text-gray-600 mb-8">
        Welcome to your equity research dashboard. The application is working!
      </p>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Dashboard Features</h2>
        <ul className="list-disc list-inside space-y-2">
          <li>Portfolio Management</li>
          <li>Stock Analysis</li>
          <li>Research Reports</li>
          <li>Risk Assessment</li>
        </ul>
      </div>
    </div>
  )
}

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<TestComponent />} />
        <Route path="/portfolio" element={<TestComponent />} />
        <Route path="/research" element={<TestComponent />} />
        <Route path="/analysis" element={<TestComponent />} />
      </Routes>
    </div>
  )
}

export default App
