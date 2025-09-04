import React, { useState } from 'react'
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Badge,
  Spinner,
  Modal,
  Container,
  Grid,
  GridItem,
  Flex,
  Heading,
  Text,
  Code,
} from './index'

/**
 * Design System Demo Component
 * 
 * This component showcases all the design system components with various
 * configurations and use cases. It serves as both documentation and testing.
 */
export const DesignSystemDemo: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')

  return (
    <Container maxWidth="7xl" className="py-8">
      <div className="space-y-12">
        {/* Header */}
        <div className="text-center">
          <Heading level={1} size="4xl" weight="bold" className="mb-4">
            Equity Research Dashboard
          </Heading>
          <Text size="xl" color="neutral" className="max-w-2xl mx-auto">
            Comprehensive design system with modern components, typography, and layout utilities
            built for financial applications.
          </Text>
        </div>

        {/* Typography Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Typography
          </Heading>
          
          <Grid cols={2} gap={6}>
            <Card>
              <CardHeader title="Headings" />
              <CardBody className="space-y-4">
                <Heading level={1} size="3xl">Heading 1</Heading>
                <Heading level={2} size="2xl">Heading 2</Heading>
                <Heading level={3} size="xl">Heading 3</Heading>
                <Heading level={4} size="lg">Heading 4</Heading>
                <Heading level={5} size="base">Heading 5</Heading>
                <Heading level={6} size="sm">Heading 6</Heading>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Text Variants" />
              <CardBody className="space-y-4">
                <Text size="lg" weight="bold">Large Bold Text</Text>
                <Text size="base" weight="medium">Medium Weight Text</Text>
                <Text size="sm" color="neutral">Small Neutral Text</Text>
                <Text size="xs" italic>Extra Small Italic Text</Text>
                <Text underline>Underlined Text</Text>
                <Text strikethrough>Strikethrough Text</Text>
              </CardBody>
            </Card>
          </Grid>

          <Card className="mt-6">
            <CardHeader title="Code Examples" />
            <CardBody>
              <div className="space-y-4">
                <div>
                  <Text size="sm" weight="medium" className="mb-2">Inline Code:</Text>
                  <Code inline>const portfolio = usePortfolio()</Code>
                </div>
                <div>
                  <Text size="sm" weight="medium" className="mb-2">Code Block:</Text>
                  <Code>
{`function calculateReturns(investment: number, returns: number[]) {
  return returns.reduce((total, ret) => total * (1 + ret), investment);
}`}
                  </Code>
                </div>
              </div>
            </CardBody>
          </Card>
        </section>

        {/* Buttons Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Buttons
          </Heading>
          
          <Grid cols={3} gap={6}>
            <Card>
              <CardHeader title="Variants" />
              <CardBody className="space-y-4">
                <Button variant="solid" color="primary" fullWidth>
                  Primary Solid
                </Button>
                <Button variant="outline" color="primary" fullWidth>
                  Primary Outline
                </Button>
                <Button variant="ghost" color="primary" fullWidth>
                  Primary Ghost
                </Button>
                <Button variant="link" color="primary" fullWidth>
                  Primary Link
                </Button>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Colors" />
              <CardBody className="space-y-4">
                <Button color="primary" fullWidth>Primary</Button>
                <Button color="secondary" fullWidth>Secondary</Button>
                <Button color="success" fullWidth>Success</Button>
                <Button color="warning" fullWidth>Warning</Button>
                <Button color="danger" fullWidth>Danger</Button>
                <Button color="neutral" fullWidth>Neutral</Button>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="States" />
              <CardBody className="space-y-4">
                <Button fullWidth>Normal</Button>
                <Button loading fullWidth>Loading</Button>
                <Button disabled fullWidth>Disabled</Button>
                <Button size="sm" fullWidth>Small</Button>
                <Button size="lg" fullWidth>Large</Button>
              </CardBody>
            </Card>
          </Grid>
        </section>

        {/* Inputs Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Inputs
          </Heading>
          
          <Grid cols={2} gap={6}>
            <Card>
              <CardHeader title="Input Types" />
              <CardBody className="space-y-4">
                <Input
                  label="Text Input"
                  placeholder="Enter text..."
                  value={inputValue}
                  onChange={setInputValue}
                />
                <Input
                  type="email"
                  label="Email Input"
                  placeholder="Enter email..."
                />
                <Input
                  type="password"
                  label="Password Input"
                  placeholder="Enter password..."
                />
                <Input
                  type="search"
                  label="Search Input"
                  placeholder="Search..."
                  clearable
                />
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Input States" />
              <CardBody className="space-y-4">
                <Input
                  label="Default State"
                  placeholder="Normal input..."
                />
                <Input
                  label="Error State"
                  state="error"
                  errorMessage="This field is required"
                  placeholder="Error input..."
                />
                <Input
                  label="Success State"
                  state="success"
                  helperText="Input is valid"
                  placeholder="Success input..."
                />
                <Input
                  label="Warning State"
                  state="warning"
                  helperText="Please review this input"
                  placeholder="Warning input..."
                />
              </CardBody>
            </Card>
          </Grid>
        </section>

        {/* Cards Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Cards
          </Heading>
          
          <Grid cols={3} gap={6}>
            <Card hoverable>
              <CardHeader
                title="Portfolio Overview"
                subtitle="Total value: $125,430"
                actions={<Badge color="success">+12.5%</Badge>}
              />
              <CardBody>
                <Text size="sm" color="neutral">
                  Your portfolio has grown by 12.5% this month, outperforming the market average.
                </Text>
              </CardBody>
              <CardFooter>
                <Button size="sm" fullWidth>View Details</Button>
              </CardFooter>
            </Card>

            <Card shadow="lg" bordered="thick">
              <CardHeader title="Stock Analysis" />
              <CardBody>
                <div className="space-y-2">
                  <Flex justify="between">
                    <Text size="sm">Current Price:</Text>
                    <Text size="sm" weight="medium">$142.50</Text>
                  </Flex>
                  <Flex justify="between">
                    <Text size="sm">Change:</Text>
                    <Text size="sm" className="financial-positive">+$2.30 (+1.64%)</Text>
                  </Flex>
                  <Flex justify="between">
                    <Text size="sm">Volume:</Text>
                    <Text size="sm" weight="medium">2.4M</Text>
                  </Flex>
                </div>
              </CardBody>
            </Card>

            <Card clickable onClick={() => setIsModalOpen(true)}>
              <CardHeader title="Research Report" />
              <CardBody>
                <Text size="sm" color="neutral">
                  Click to view the latest research report for AAPL with detailed analysis and recommendations.
                </Text>
              </CardBody>
            </Card>
          </Grid>
        </section>

        {/* Badges Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Badges
          </Heading>
          
          <Card>
            <CardHeader title="Badge Variants" />
            <CardBody>
              <div className="space-y-6">
                <div>
                  <Text size="sm" weight="medium" className="mb-3">Colors:</Text>
                  <Flex gap={3} wrap="wrap">
                    <Badge color="primary">Primary</Badge>
                    <Badge color="secondary">Secondary</Badge>
                    <Badge color="success">Success</Badge>
                    <Badge color="warning">Warning</Badge>
                    <Badge color="danger">Danger</Badge>
                    <Badge color="neutral">Neutral</Badge>
                  </Flex>
                </div>

                <div>
                  <Text size="sm" weight="medium" className="mb-3">Shapes:</Text>
                  <Flex gap={3} wrap="wrap">
                    <Badge shape="rounded">Rounded</Badge>
                    <Badge shape="pill">Pill</Badge>
                    <Badge shape="square">Square</Badge>
                  </Flex>
                </div>

                <div>
                  <Text size="sm" weight="medium" className="mb-3">Count Badges:</Text>
                  <Flex gap={3} wrap="wrap">
                    <Badge count={5} color="primary" />
                    <Badge count={99} color="success" />
                    <Badge count={150} max={99} color="warning" />
                    <Badge dot color="danger" />
                  </Flex>
                </div>

                <div>
                  <Text size="sm" weight="medium" className="mb-3">Outlined:</Text>
                  <Flex gap={3} wrap="wrap">
                    <Badge outlined color="primary">Primary</Badge>
                    <Badge outlined color="success">Success</Badge>
                    <Badge outlined color="warning">Warning</Badge>
                    <Badge outlined color="danger">Danger</Badge>
                  </Flex>
                </div>
              </div>
            </CardBody>
          </Card>
        </section>

        {/* Spinners Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Loading Spinners
          </Heading>
          
          <Grid cols={2} gap={6}>
            <Card>
              <CardHeader title="Spinner Variants" />
              <CardBody>
                <div className="space-y-6">
                  <div>
                    <Text size="sm" weight="medium" className="mb-3">Dots:</Text>
                    <Spinner variant="dots" color="primary" />
                  </div>
                  <div>
                    <Text size="sm" weight="medium" className="mb-3">Ring:</Text>
                    <Spinner variant="ring" color="success" />
                  </div>
                  <div>
                    <Text size="sm" weight="medium" className="mb-3">Bars:</Text>
                    <Spinner variant="bars" color="warning" />
                  </div>
                  <div>
                    <Text size="sm" weight="medium" className="mb-3">Pulse:</Text>
                    <Spinner variant="pulse" color="danger" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="With Text" />
              <CardBody>
                <div className="space-y-6">
                  <Spinner variant="ring" color="primary" text="Loading data..." />
                  <Spinner variant="dots" color="success" text="Processing..." />
                  <Spinner variant="bars" color="warning" text="Analyzing..." />
                </div>
              </CardBody>
            </Card>
          </Grid>
        </section>

        {/* Layout Section */}
        <section>
          <Heading level={2} size="2xl" weight="semibold" className="mb-6">
            Layout Components
          </Heading>
          
          <Card>
            <CardHeader title="Grid System" />
            <CardBody>
              <div className="space-y-4">
                <Text size="sm" weight="medium">12-Column Grid:</Text>
                <Grid cols={12} gap={2}>
                  <GridItem span={6}>
                    <div className="bg-primary-100 p-2 text-center text-xs">6 cols</div>
                  </GridItem>
                  <GridItem span={6}>
                    <div className="bg-primary-100 p-2 text-center text-xs">6 cols</div>
                  </GridItem>
                  <GridItem span={4}>
                    <div className="bg-primary-100 p-2 text-center text-xs">4 cols</div>
                  </GridItem>
                  <GridItem span={4}>
                    <div className="bg-primary-100 p-2 text-center text-xs">4 cols</div>
                  </GridItem>
                  <GridItem span={4}>
                    <div className="bg-primary-100 p-2 text-center text-xs">4 cols</div>
                  </GridItem>
                </Grid>
              </div>
            </CardBody>
          </Card>

          <Card className="mt-6">
            <CardHeader title="Flex Layouts" />
            <CardBody>
              <div className="space-y-4">
                <div>
                  <Text size="sm" weight="medium" className="mb-2">Space Between:</Text>
                  <Flex justify="between" className="bg-neutral-100 p-4 rounded">
                    <div className="bg-primary-500 text-white px-3 py-1 rounded text-sm">Left</div>
                    <div className="bg-primary-500 text-white px-3 py-1 rounded text-sm">Right</div>
                  </Flex>
                </div>
                <div>
                  <Text size="sm" weight="medium" className="mb-2">Center:</Text>
                  <Flex justify="center" className="bg-neutral-100 p-4 rounded">
                    <div className="bg-primary-500 text-white px-3 py-1 rounded text-sm">Centered</div>
                  </Flex>
                </div>
                <div>
                  <Text size="sm" weight="medium" className="mb-2">Column with Gap:</Text>
                  <Flex direction="column" gap={2} className="bg-neutral-100 p-4 rounded">
                    <div className="bg-primary-500 text-white px-3 py-1 rounded text-sm">Item 1</div>
                    <div className="bg-primary-500 text-white px-3 py-1 rounded text-sm">Item 2</div>
                    <div className="bg-primary-500 text-white px-3 py-1 rounded text-sm">Item 3</div>
                  </Flex>
                </div>
              </div>
            </CardBody>
          </Card>
        </section>

        {/* Modal Demo */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Research Report"
          size="lg"
        >
          <div className="space-y-4">
            <Text>
              This is a sample research report modal. It demonstrates the modal component
              with proper accessibility features and backdrop handling.
            </Text>
            <Card>
              <CardHeader title="AAPL Analysis" />
              <CardBody>
                <div className="space-y-2">
                  <Flex justify="between">
                    <Text size="sm">Target Price:</Text>
                    <Text size="sm" weight="medium">$180.00</Text>
                  </Flex>
                  <Flex justify="between">
                    <Text size="sm">Rating:</Text>
                    <Badge color="success">Buy</Badge>
                  </Flex>
                  <Flex justify="between">
                    <Text size="sm">Risk Level:</Text>
                    <Badge color="warning">Medium</Badge>
                  </Flex>
                </div>
              </CardBody>
            </Card>
          </div>
        </Modal>
      </div>
    </Container>
  )
}
