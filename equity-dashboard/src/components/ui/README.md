# Equity Research Dashboard Design System

A comprehensive design system built for financial applications with modern components, typography, and layout utilities.

## 🎨 Design Principles

- **Consistency**: Unified visual language across all components
- **Accessibility**: WCAG 2.1 AA compliant with proper focus management
- **Performance**: Optimized for fast rendering and minimal bundle size
- **Flexibility**: Highly customizable with TypeScript support
- **Financial Focus**: Specialized components for financial data display

## 📦 Components

### Base Components

#### Button
Multi-variant button component with loading states and icons.

```tsx
import { Button } from '@/components/ui'

<Button variant="solid" color="primary" size="lg" loading>
  Save Changes
</Button>
```

**Variants**: `solid`, `outline`, `ghost`, `link`  
**Colors**: `primary`, `secondary`, `success`, `warning`, `danger`, `neutral`  
**Sizes**: `xs`, `sm`, `base`, `lg`, `xl`, `2xl`, `3xl`, `4xl`

#### Input
Form input with validation states and icons.

```tsx
import { Input } from '@/components/ui'

<Input
  label="Email Address"
  type="email"
  state="error"
  errorMessage="Please enter a valid email"
  leftIcon={<EmailIcon />}
  clearable
/>
```

**Types**: `text`, `email`, `password`, `number`, `search`, `tel`, `url`  
**States**: `default`, `error`, `success`, `warning`

#### Card
Container component with header, body, and footer sections.

```tsx
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui'

<Card hoverable>
  <CardHeader title="Portfolio" subtitle="Total: $125,430" />
  <CardBody>
    <p>Your portfolio performance</p>
  </CardBody>
  <CardFooter>
    <Button>View Details</Button>
  </CardFooter>
</Card>
```

#### Badge
Status indicators and labels with count support.

```tsx
import { Badge } from '@/components/ui'

<Badge color="success" shape="pill">Active</Badge>
<Badge count={5} max={99} color="primary" />
<Badge dot color="warning" />
```

#### Spinner
Loading indicators with multiple animation variants.

```tsx
import { Spinner } from '@/components/ui'

<Spinner variant="ring" color="primary" text="Loading..." />
```

**Variants**: `dots`, `pulse`, `ring`, `bars`

#### Modal
Accessible modal with backdrop and keyboard navigation.

```tsx
import { Modal } from '@/components/ui'

<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Confirm Action"
  size="md"
>
  <p>Are you sure?</p>
</Modal>
```

### Layout Components

#### Container
Responsive container with max-width constraints.

```tsx
import { Container } from '@/components/ui'

<Container maxWidth="lg" padded>
  <h1>Page Content</h1>
</Container>
```

#### Grid
12-column responsive grid system.

```tsx
import { Grid, GridItem } from '@/components/ui'

<Grid cols={12} gap={4}>
  <GridItem span={6}>Half width</GridItem>
  <GridItem span={6}>Half width</GridItem>
</Grid>
```

#### Flex
Flexible layout component with common patterns.

```tsx
import { Flex } from '@/components/ui'

<Flex direction="row" justify="between" align="center" gap={4}>
  <div>Left content</div>
  <div>Right content</div>
</Flex>
```

### Typography Components

#### Heading
Semantic heading component with size and weight variants.

```tsx
import { Heading } from '@/components/ui'

<Heading level={1} size="3xl" weight="bold">
  Page Title
</Heading>
```

#### Text
Body text component with styling options.

```tsx
import { Text } from '@/components/ui'

<Text size="lg" weight="medium" color="neutral">
  Body text content
</Text>
```

#### Code
Code display component for inline and block code.

```tsx
import { Code } from '@/components/ui'

<Code inline>const value = 42;</Code>
<Code background="neutral">
  function example() {
    return "Hello World";
  }
</Code>
```

## 🎨 Design Tokens

### Colors

The design system includes a comprehensive color palette:

- **Primary**: Blue tones for primary actions
- **Secondary**: Slate tones for secondary elements
- **Success**: Green tones for positive states
- **Warning**: Amber tones for caution states
- **Danger**: Red tones for error states
- **Neutral**: Gray tones for text and backgrounds
- **Financial**: Specialized colors for financial data

### Typography

- **Primary Font**: Inter (sans-serif)
- **Monospace Font**: JetBrains Mono
- **Size Scale**: xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl, 6xl
- **Weight Scale**: light, normal, medium, semibold, bold, extrabold, black

### Spacing

Based on a 4px grid system:
- **xs**: 4px
- **sm**: 8px
- **base**: 12px
- **lg**: 16px
- **xl**: 20px
- **2xl**: 24px
- **3xl**: 32px
- **4xl**: 40px

## 🚀 Usage

### Installation

The design system is already configured in the project. Import components as needed:

```tsx
import { Button, Input, Card } from '@/components/ui'
```

### TypeScript Support

All components are fully typed with comprehensive prop interfaces:

```tsx
import type { ButtonProps, InputProps } from '@/components/ui'

const MyButton: React.FC<ButtonProps> = (props) => {
  return <Button {...props} />
}
```

### Customization

Components can be customized using:

1. **Props**: Built-in customization options
2. **CSS Classes**: Additional Tailwind classes via `className`
3. **CSS Variables**: Override design tokens in CSS
4. **Tailwind Config**: Extend the design system tokens

## 📱 Responsive Design

All components are built with mobile-first responsive design:

- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- **Grid System**: Responsive 12-column grid
- **Typography**: Responsive text sizing
- **Spacing**: Responsive spacing utilities

## ♿ Accessibility

The design system prioritizes accessibility:

- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and roles
- **Focus Management**: Visible focus indicators
- **Color Contrast**: WCAG 2.1 AA compliant
- **Semantic HTML**: Proper HTML structure

## 🎯 Financial-Specific Features

### Financial Data Colors

Specialized color classes for financial data:

```tsx
<span className="financial-positive">+$1,250.00</span>
<span className="financial-negative">-$850.00</span>
<span className="financial-neutral">$0.00</span>
<span className="financial-warning">High Risk</span>
```

### Financial Backgrounds

Background variants for financial data:

```tsx
<div className="financial-positive-bg">Positive Change</div>
<div className="financial-negative-bg">Negative Change</div>
```

## 🔧 Development

### Adding New Components

1. Create component file in `src/components/ui/`
2. Define TypeScript interfaces in `src/types/design-system.ts`
3. Export from `src/components/ui/index.ts`
4. Add to demo in `DesignSystemDemo.tsx`

### Testing Components

Use the `DesignSystemDemo` component to test and showcase components:

```tsx
import { DesignSystemDemo } from '@/components/ui/DesignSystemDemo'

// View at http://localhost:5173/
```

## 📚 Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Inter Font](https://rsms.me/inter/)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 🤝 Contributing

When contributing to the design system:

1. Follow existing patterns and conventions
2. Ensure TypeScript types are complete
3. Add comprehensive JSDoc comments
4. Test components in the demo
5. Update this documentation

## 📄 License

This design system is part of the Equity Research Dashboard project.
