import React, { useState } from 'react'
import { 
  PageTransition, 
  StaggeredList, 
  HoverScale, 
  LoadingStates, 
  SkeletonCard, 
  SkeletonChart,
  ErrorStates,
  FeedbackAnimation,
  AnimatedCounter,
  PullToRefresh,
  SwipeableCard,
  BottomSheet,
  TouchButton,
  MobileTabs,
  ThemeToggle,
  AccessibilitySettings,
  SettingsPanel
} from '../ui'

/**
 * UX Demo Component
 * 
 * This component showcases all the UX enhancements implemented
 * for the equity research dashboard. It demonstrates loading states,
 * animations, error handling, accessibility features, and mobile
 * interactions.
 */
export const UXDemo: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [showError, setShowError] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [showBottomSheet, setShowBottomSheet] = useState(false)
  const [activeTab, setActiveTab] = useState('loading')

  const tabs = [
    { id: 'loading', label: 'Loading', icon: '⏳' },
    { id: 'animations', label: 'Animations', icon: '✨' },
    { id: 'errors', label: 'Errors', icon: '⚠️' },
    { id: 'mobile', label: 'Mobile', icon: '📱' },
    { id: 'accessibility', label: 'A11y', icon: '♿' },
    { id: 'themes', label: 'Themes', icon: '🎨' }
  ]

  const handleRefresh = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsLoading(false)
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 3000)
  }

  const handleError = () => {
    setShowError(true)
    setTimeout(() => setShowError(false), 5000)
  }

  const renderLoadingDemo = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <LoadingStates loading={isLoading} skeleton={<SkeletonCard />}>
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Portfolio Value</h3>
            <div className="text-3xl font-bold text-primary-600">
              <AnimatedCounter value={125430.50} prefix="$" decimals={2} />
            </div>
            <p className="text-sm text-neutral-600 mt-2">+2.34% from yesterday</p>
          </div>
        </LoadingStates>

        <LoadingStates loading={isLoading} skeleton={<SkeletonChart />}>
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Performance Chart</h3>
            <div className="h-40 bg-gradient-to-r from-primary-100 to-primary-200 rounded-lg flex items-center justify-center">
              <span className="text-primary-600 font-medium">Chart Placeholder</span>
            </div>
          </div>
        </LoadingStates>
      </div>

      <div className="flex space-x-4">
        <TouchButton onClick={() => setIsLoading(!isLoading)}>
          {isLoading ? 'Stop Loading' : 'Start Loading'}
        </TouchButton>
        <TouchButton variant="secondary" onClick={handleRefresh}>
          Simulate Refresh
        </TouchButton>
      </div>
    </div>
  )

  const renderAnimationsDemo = () => (
    <div className="space-y-6">
      <StaggeredList className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((item) => (
          <HoverScale key={item}>
            <div className="card cursor-pointer">
              <h3 className="text-lg font-semibold mb-2">Animated Card {item}</h3>
              <p className="text-neutral-600">
                Hover over this card to see the scale animation.
              </p>
              <div className="mt-4">
                <AnimatedCounter 
                  value={Math.random() * 1000} 
                  prefix="$" 
                  decimals={0}
                />
              </div>
            </div>
          </HoverScale>
        ))}
      </StaggeredList>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Counter Animation</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              <AnimatedCounter value={125430} prefix="$" />
            </div>
            <p className="text-sm text-neutral-600">Portfolio Value</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">
              <AnimatedCounter value={15.23} suffix="%" />
            </div>
            <p className="text-sm text-neutral-600">Total Return</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">
              <AnimatedCounter value={68.5} suffix="%" />
            </div>
            <p className="text-sm text-neutral-600">Win Rate</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-danger-600">
              <AnimatedCounter value={2340} prefix="$" />
            </div>
            <p className="text-sm text-neutral-600">Today's P&L</p>
          </div>
        </div>
      </div>
    </div>
  )

  const renderErrorsDemo = () => (
    <div className="space-y-6">
      <div className="flex space-x-4">
        <TouchButton onClick={handleError}>
          Trigger Error
        </TouchButton>
        <TouchButton variant="secondary" onClick={() => setShowSuccess(true)}>
          Show Success
        </TouchButton>
      </div>

      {showError && (
        <ErrorStates
          error="Failed to load market data"
          onRetry={() => setShowError(false)}
          variant="card"
        />
      )}

      <FeedbackAnimation type="success" show={showSuccess}>
        <div className="flex items-center space-x-2">
          <span>✅</span>
          <span>Data loaded successfully!</span>
        </div>
      </FeedbackAnimation>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ErrorStates
          error="Network connection failed"
          onRetry={() => console.log('Retrying...')}
          variant="inline"
        />
        <ErrorStates
          error="Request timeout"
          onRetry={() => console.log('Retrying...')}
          variant="inline"
        />
      </div>
    </div>
  )

  const renderMobileDemo = () => (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Swipeable Card</h3>
        <SwipeableCard
          onSwipeLeft={() => alert('Swiped left!')}
          onSwipeRight={() => alert('Swiped right!')}
          leftAction={<span className="text-white">Delete</span>}
          rightAction={<span className="text-white">Archive</span>}
        >
          <div className="p-4">
            <h4 className="font-semibold">AAPL - Apple Inc.</h4>
            <p className="text-neutral-600">$175.43 (+2.34%)</p>
            <p className="text-sm text-neutral-500">Swipe left or right for actions</p>
          </div>
        </SwipeableCard>
      </div>

      <div className="flex space-x-4">
        <TouchButton onClick={() => setShowBottomSheet(true)}>
          Open Bottom Sheet
        </TouchButton>
      </div>

      <BottomSheet
        isOpen={showBottomSheet}
        onClose={() => setShowBottomSheet(false)}
        title="Mobile Actions"
      >
        <div className="space-y-4">
          <TouchButton fullWidth>Action 1</TouchButton>
          <TouchButton variant="secondary" fullWidth>Action 2</TouchButton>
          <TouchButton variant="danger" fullWidth>Action 3</TouchButton>
        </div>
      </BottomSheet>
    </div>
  )

  const renderAccessibilityDemo = () => (
    <div className="space-y-6">
      <AccessibilitySettings />
      
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Accessible Components</h3>
        <div className="space-y-4">
          <button className="px-4 py-2 bg-primary-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
            Accessible Button
          </button>
          <input 
            type="text" 
            placeholder="Accessible input"
            className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            aria-label="Sample input field"
          />
        </div>
      </div>
    </div>
  )

  const renderThemesDemo = () => (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Theme Controls</h3>
        <div className="flex items-center space-x-4">
          <ThemeToggle showLabel />
        </div>
      </div>

      <SettingsPanel />
    </div>
  )

  const renderContent = () => {
    switch (activeTab) {
      case 'loading':
        return renderLoadingDemo()
      case 'animations':
        return renderAnimationsDemo()
      case 'errors':
        return renderErrorsDemo()
      case 'mobile':
        return renderMobileDemo()
      case 'accessibility':
        return renderAccessibilityDemo()
      case 'themes':
        return renderThemesDemo()
      default:
        return renderLoadingDemo()
    }
  }

  return (
    <PageTransition>
      <PullToRefresh onRefresh={handleRefresh}>
        <div className="space-y-6" id="main-content">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              UX Enhancements Demo
            </h1>
            <p className="text-neutral-600 dark:text-neutral-400">
              Showcase of professional UX features and interactions
            </p>
          </div>

          <MobileTabs
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />

          {renderContent()}
        </div>
      </PullToRefresh>
    </PageTransition>
  )
}
