def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    import os
    import sys
    
    # Determine if the application is running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # If we're running in a PyInstaller bundle
        application_path = sys._MEIPASS
    else:
        # If we're running in a normal Python environment
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(application_path, relative_path)