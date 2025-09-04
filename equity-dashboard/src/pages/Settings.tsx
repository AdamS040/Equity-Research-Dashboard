import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  UserIcon, 
  BellIcon, 
  ShieldCheckIcon, 
  CogIcon,
  KeyIcon,
  GlobeAltIcon,
  ChartBarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'preferences', name: 'Preferences', icon: CogIcon },
    { id: 'api', name: 'API Keys', icon: KeyIcon },
    { id: 'appearance', name: 'Appearance', icon: GlobeAltIcon },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-4">Profile Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    First Name
                  </label>
                  <Input placeholder="John" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Last Name
                  </label>
                  <Input placeholder="Doe" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Email
                  </label>
                  <Input type="email" placeholder="john.doe@example.com" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Phone
                  </label>
                  <Input placeholder="+1 (555) 123-4567" />
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <Button>Save Changes</Button>
            </div>
          </div>
        )
      
      case 'notifications':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-4">Notification Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-neutral-900">Email Notifications</h4>
                    <p className="text-sm text-neutral-500">Receive email updates about your portfolio</p>
                  </div>
                  <input type="checkbox" className="rounded border-neutral-300" defaultChecked />
                </div>
                <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-neutral-900">Push Notifications</h4>
                    <p className="text-sm text-neutral-500">Get real-time alerts on your device</p>
                  </div>
                  <input type="checkbox" className="rounded border-neutral-300" />
                </div>
                <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-neutral-900">Market Alerts</h4>
                    <p className="text-sm text-neutral-500">Notifications for significant market movements</p>
                  </div>
                  <input type="checkbox" className="rounded border-neutral-300" defaultChecked />
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'security':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-4">Security Settings</h3>
              <div className="space-y-4">
                <div className="p-4 border border-neutral-200 rounded-lg">
                  <h4 className="font-medium text-neutral-900 mb-2">Change Password</h4>
                  <div className="space-y-3">
                    <Input type="password" placeholder="Current password" />
                    <Input type="password" placeholder="New password" />
                    <Input type="password" placeholder="Confirm new password" />
                  </div>
                  <Button className="mt-3">Update Password</Button>
                </div>
                <div className="p-4 border border-neutral-200 rounded-lg">
                  <h4 className="font-medium text-neutral-900 mb-2">Two-Factor Authentication</h4>
                  <p className="text-sm text-neutral-500 mb-3">
                    Add an extra layer of security to your account
                  </p>
                  <Button variant="secondary">Enable 2FA</Button>
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'preferences':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-4">Application Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-neutral-900">Auto-refresh Data</h4>
                    <p className="text-sm text-neutral-500">Automatically refresh market data every 30 seconds</p>
                  </div>
                  <input type="checkbox" className="rounded border-neutral-300" defaultChecked />
                </div>
                <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-neutral-900">Show Advanced Charts</h4>
                    <p className="text-sm text-neutral-500">Display technical indicators and advanced charting tools</p>
                  </div>
                  <input type="checkbox" className="rounded border-neutral-300" />
                </div>
                <div className="flex items-center justify-between p-4 border border-neutral-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-neutral-900">Compact View</h4>
                    <p className="text-sm text-neutral-500">Use a more compact layout for data tables</p>
                  </div>
                  <input type="checkbox" className="rounded border-neutral-300" />
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'api':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-4">API Keys</h3>
              <div className="p-4 border border-neutral-200 rounded-lg">
                <p className="text-sm text-neutral-500 mb-4">
                  Manage your API keys for third-party integrations
                </p>
                <Button>Generate New API Key</Button>
              </div>
            </div>
          </div>
        )
      
      case 'appearance':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-4">Appearance Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Theme
                  </label>
                  <select className="w-full p-2 border border-neutral-300 rounded-lg">
                    <option>Light</option>
                    <option>Dark</option>
                    <option>System</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Language
                  </label>
                  <select className="w-full p-2 border border-neutral-300 rounded-lg">
                    <option>English</option>
                    <option>Spanish</option>
                    <option>French</option>
                    <option>German</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Date Format
                  </label>
                  <select className="w-full p-2 border border-neutral-300 rounded-lg">
                    <option>MM/DD/YYYY</option>
                    <option>DD/MM/YYYY</option>
                    <option>YYYY-MM-DD</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Settings</h1>
        <p className="text-neutral-600 mt-1">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card className="p-0">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-4 py-3 text-left text-sm font-medium rounded-none border-l-4 transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 border-primary-600'
                      : 'text-neutral-700 hover:bg-neutral-50 border-transparent'
                  }`}
                >
                  <tab.icon className="w-5 h-5 mr-3" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </Card>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <Card>
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
            >
              {renderTabContent()}
            </motion.div>
          </Card>
        </div>
      </div>
    </div>
  )
}
