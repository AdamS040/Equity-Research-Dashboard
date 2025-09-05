"""
Main application runner for Equity Research Dashboard
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app
from config import config

def main():
    """Main function to run the application"""
    
    # Get environment from environment variable or default to development
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create the application
    app = create_app(config_name)
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║            🏦 EQUITY RESEARCH DASHBOARD 📊                    ║
    ║                                                              ║
    ║  Professional Financial Analysis & Portfolio Management      ║
    ║                                                              ║
    ║  Running on: http://{host}:{port}                     ║
    ║  Environment: {config_name.title()}                                   ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  • Real-time market data & analysis                          ║
    ║  • DCF valuation models                                      ║
    ║  • Portfolio optimization                                    ║
    ║  • Risk analytics & reporting                                ║
    ║  • Interactive visualizations                                ║
    ║                                                              ║
    ║  Press Ctrl+C to stop the server                            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=config[config_name].DEBUG,
        threaded=True
    )

if __name__ == '__main__':
    main()