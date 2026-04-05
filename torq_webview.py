"""
TORQ WebView App - Android APK
Wraps the Streamlit web app in a native Android WebView
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast

# Android WebView classes
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
WebSettings = autoclass('android.webkit.WebSettings')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
LinearLayout = autoclass('android.widget.LinearLayout')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

# TORQ Web App URL
TORQ_URL = "https://torq-app-dbd36yhetgbc7epzhitxhd.streamlit.app/"

class TORQWebViewApp(App):
    """TORQ WebView Application"""
    
    def build(self):
        # Main layout
        self.layout = BoxLayout(orientation='vertical')
        
        # Header with app name and refresh button
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='48dp',
            padding=['10dp', '5dp']
        )
        
        # App title
        title = Label(
            text='TORQ - AI Assistant',
            size_hint_x=0.7,
            font_size='18sp',
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        
        # Refresh button
        refresh_btn = Button(
            text='🔄 Refresh',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_webview)
        header.add_widget(refresh_btn)
        
        self.layout.add_widget(header)
        
        # Loading indicator
        self.loading_label = Label(
            text='Loading TORQ...',
            size_hint_y=None,
            height='30dp',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.layout.add_widget(self.loading_label)
        
        # Progress bar
        self.progress = ProgressBar(
            max=100,
            size_hint_y=None,
            height='4dp'
        )
        self.layout.add_widget(self.progress)
        
        # Initialize WebView
        Clock.schedule_once(self.create_webview, 0)
        
        return self.layout
    
    @run_on_ui_thread
    def create_webview(self, dt):
        """Create and configure WebView"""
        # Get the activity
        activity = PythonActivity.mActivity
        
        # Create WebView
        self.webview = WebView(activity)
        
        # Configure WebView settings
        settings = self.webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setDatabaseEnabled(True)
        settings.setAllowFileAccess(True)
        settings.setAllowContentAccess(True)
        settings.setLoadWithOverviewMode(True)
        settings.setUseWideViewPort(True)
        settings.setBuiltInZoomControls(False)
        settings.setDisplayZoomControls(False)
        settings.setSupportZoom(True)
        settings.setDefaultTextEncodingName("utf-8")
        
        # Enable caching for better performance
        settings.setCacheMode(WebSettings.LOAD_DEFAULT)
        settings.setAppCacheEnabled(True)
        
        # Set WebView client to handle page loading
        self.webview.setWebViewClient(CustomWebViewClient(self))
        
        # Set layout parameters
        layout_params = LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.MATCH_PARENT
        )
        self.webview.setLayoutParams(layout_params)
        
        # Add WebView to activity
        activity.addContentView(self.webview, layout_params)
        
        # Load TORQ URL
        self.webview.loadUrl(TORQ_URL)
        
        # Update UI
        Clock.schedule_once(lambda dt: self.update_loading_status("Loading TORQ..."), 0)
    
    def refresh_webview(self, instance):
        """Refresh the WebView"""
        if hasattr(self, 'webview'):
            self.webview.reload()
            self.update_loading_status("Refreshing...")
    
    def update_loading_status(self, message):
        """Update loading status message"""
        self.loading_label.text = message
    
    def update_progress(self, progress):
        """Update progress bar"""
        self.progress.value = progress
    
    def on_page_finished(self):
        """Called when page finishes loading"""
        self.loading_label.text = "✅ TORQ Loaded"
        self.progress.value = 100
        
        # Hide loading indicator after 2 seconds
        Clock.schedule_once(lambda dt: self.hide_loading(), 2)
    
    def hide_loading(self):
        """Hide loading indicator"""
        self.loading_label.opacity = 0
        self.progress.opacity = 0
    
    def on_pause(self):
        """Handle app pause"""
        return True
    
    def on_resume(self):
        """Handle app resume"""
        pass

class CustomWebViewClient(WebViewClient):
    """Custom WebView client to handle page events"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
    
    def onPageStarted(self, view, url, favicon):
        """Called when page starts loading"""
        Clock.schedule_once(lambda dt: self.app.update_loading_status("Loading..."), 0)
        Clock.schedule_once(lambda dt: self.app.update_progress(0), 0)
    
    def onPageFinished(self, view, url):
        """Called when page finishes loading"""
        Clock.schedule_once(lambda dt: self.app.on_page_finished(), 0)
    
    def onReceivedError(self, view, errorCode, description, failingUrl):
        """Called when page loading error occurs"""
        error_msg = f"Error loading page: {description}"
        Clock.schedule_once(lambda dt: self.app.update_loading_status(error_msg), 0)

if __name__ == '__main__':
    TORQWebViewApp().run()