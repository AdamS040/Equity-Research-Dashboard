// Simple script to install the missing devtools package
const { execSync } = require('child_process');

try {
  console.log('Installing @tanstack/react-query-devtools...');
  execSync('npm install @tanstack/react-query-devtools', { stdio: 'inherit' });
  console.log('Package installed successfully!');
} catch (error) {
  console.error('Failed to install package:', error.message);
  console.log('You can manually install it with: npm install @tanstack/react-query-devtools');
}
