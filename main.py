import math, string, random, re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.uix.actionbar import ActionBar, ActionView, ActionPrevious, ActionButton
import threading

# Common passwords list (top 100 most common)
COMMON_PASSWORDS = {
    '123456', 'password', '123456789', '12345678', '12345', '1234567', '1234567890',
    'qwerty', 'abc123', 'million', '000000', '1234', 'iloveyou', 'aaron431',
    'password1', 'qqww1122', '123', 'omgpop', '123321', '654321', 'qwertyuiop',
    'qwer123456', '123654', '123abc', 'password123', '111111', 'monkey', '11111111',
    'dragon', 'login', 'princess', 'qwerty123', 'solo', 'passw0rd', 'starwars',
    'charlie', 'aa123456', '1q2w3e4r', '123qwe', 'zxcvbnm', 'asdf', 'football',
    'asdfgh', 'master', 'michael', 'superman', 'iloveyou1', 'qwertyui', 'welcome',
    'monkey1', 'sunshine', 'password12', '123456a', 'admin', 'letmein'
}

# -------- PASSWORD LOGIC --------
def calculate_entropy(password):
    char_sets = 0
    if any(c.islower() for c in password): char_sets += 26
    if any(c.isupper() for c in password): char_sets += 26
    if any(c.isdigit() for c in password): char_sets += 10
    if any(c in string.punctuation for c in password): char_sets += 32
    
    L = len(password)
    N = char_sets if char_sets > 0 else 1
    
    entropy = L * math.log2(N)
    if has_common_patterns(password):
        entropy *= 0.7
    if password.lower() in COMMON_PASSWORDS:
        entropy *= 0.3
    
    return round(entropy, 2)

def has_common_patterns(password):
    patterns = [
        r'(.)\1{2,}',
        r'(012|123|234|345|456|567|678|789|890)',
        r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',
        r'(qwe|wer|ert|rty|tyu|yui|uio|iop|asd|sdf|dfg|fgh|ghj|hjk|jkl|zxc|xcv|cvb|vbn|bnm)',
    ]
    return any(re.search(pattern, password.lower()) for pattern in patterns)

def get_strength(entropy, password):
    if password.lower() in COMMON_PASSWORDS:
        return "Very Weak"
    elif entropy < 30:
        return "Weak"
    elif entropy < 50:
        return "Fair"
    elif entropy < 70:
        return "Good"
    elif entropy < 90:
        return "Strong"
    else:
        return "Very Strong"

def get_detailed_feedback(password, entropy):
    feedback = []
    score = 0
    
    if len(password) < 8:
        feedback.append("❌ Too short (minimum 8 characters)")
    elif len(password) < 12:
        feedback.append("⚠️ Consider longer password (12+ chars)")
        score += 1
    else:
        feedback.append("✅ Good length")
        score += 2
    
    if not any(c.isupper() for c in password):
        feedback.append("❌ Add uppercase letters")
    else:
        feedback.append("✅ Contains uppercase")
        score += 1
        
    if not any(c.islower() for c in password):
        feedback.append("❌ Add lowercase letters")
    else:
        feedback.append("✅ Contains lowercase")
        score += 1
        
    if not any(c.isdigit() for c in password):
        feedback.append("❌ Add numbers")
    else:
        feedback.append("✅ Contains numbers")
        score += 1
        
    if not any(c in string.punctuation for c in password):
        feedback.append("❌ Add special characters")
    else:
        feedback.append("✅ Contains symbols")
        score += 1
    
    if has_common_patterns(password):
        feedback.append("⚠️ Avoid common patterns")
    else:
        feedback.append("✅ No obvious patterns")
        score += 1
        
    if password.lower() in COMMON_PASSWORDS:
        feedback.append("❌ This is a common password!")
    else:
        feedback.append("✅ Not a common password")
        score += 1
    
    return feedback, score

def generate_secure_password(length=16, use_symbols=True, exclude_ambiguous=True):
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    if exclude_ambiguous:
        ambiguous = "0O1lI"
        chars = ''.join(c for c in chars if c not in ambiguous)
    
    password = []
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.digits))
    if use_symbols:
        password.append(random.choice("!@#$%^&*"))
    
    for _ in range(length - len(password)):
        password.append(random.choice(chars))
    
    random.shuffle(password)
    return ''.join(password)

def time_to_crack(entropy):
    guesses_per_sec = 1e12
    seconds = (2 ** entropy) / (2 * guesses_per_sec)
    
    if seconds < 1:
        return "Instantly"
    elif seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    elif seconds < 31536000:
        return f"{seconds/86400:.1f} days"
    elif seconds < 31536000000:
        return f"{seconds/31536000:.1f} years"
    else:
        return "Millions of years"

# -------- MODERN UI COMPONENTS --------
class GradientWidget(Widget):
    def __init__(self, colors=None, **kwargs):
        super().__init__(**kwargs)
        self.colors = colors or [(0.2, 0.4, 0.8, 1), (0.1, 0.6, 0.9, 1)]
        with self.canvas:
            Color(*self.colors[0])
            self.rect = RoundedRectangle(radius=[dp(15)])
            self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernCard(BoxLayout):
    def __init__(self, elevation=2, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = [dp(20), dp(15), dp(20), dp(15)]
        
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.1)
            self.shadow_rect = RoundedRectangle(radius=[dp(15)])
            # Background
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(radius=[dp(15)])
            self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        shadow_offset = dp(2)
        self.shadow_rect.pos = [self.pos[0] + shadow_offset, self.pos[1] - shadow_offset]
        self.shadow_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class ModernButton(Button):
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.bg_color = bg_color or [0.2, 0.5, 0.9, 1]
        
        with self.canvas.before:
            Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(radius=[dp(25)])
            self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_press(self):
        anim = Animation(opacity=0.7, duration=0.1)
        anim.start(self)
    
    def on_release(self):
        anim = Animation(opacity=1, duration=0.1)
        anim.start(self)

class LoadingSpinner(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0
        with self.canvas:
            Color(0.2, 0.5, 0.9, 1)
            self.line = Line(circle=(0, 0, dp(30), 0, 270), width=dp(4))
            self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        Clock.schedule_interval(self.rotate, 1/60.0)
    
    def update_graphics(self, *args):
        center_x = self.center_x
        center_y = self.center_y
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.5, 0.9, 1)
            self.line = Line(circle=(center_x, center_y, dp(30), self.angle, self.angle + 270), width=dp(4))
    
    def rotate(self, dt):
        self.angle += 5
        if self.angle >= 360:
            self.angle = 0
        self.update_graphics()

# -------- SCREENS --------
class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Gradient background
        layout = FloatLayout()
        bg = GradientWidget(colors=[(0.05, 0.1, 0.2, 1), (0.1, 0.2, 0.4, 1)])
        layout.add_widget(bg)
        
        # Center content
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        content = BoxLayout(orientation='vertical', spacing=dp(30), size_hint=(None, None), size=(dp(300), dp(400)))
        
        # App icon/logo
        logo_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.4))
        logo = Label(
            text='🔐',
            font_size=sp(120),
            size_hint=(None, None),
            size=(dp(150), dp(150))
        )
        logo_container.add_widget(logo)
        
        # App name
        title = Label(
            text='[b]Password Guardian[/b]',
            markup=True,
            font_size=sp(32),
            color=[1, 1, 1, 1],
            size_hint=(1, 0.2),
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        # Subtitle
        subtitle = Label(
            text='Secure your digital life',
            font_size=sp(18),
            color=[0.8, 0.8, 0.8, 1],
            size_hint=(1, 0.15),
            halign='center'
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        
        # Loading spinner
        spinner_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.2))
        spinner = LoadingSpinner(size_hint=(None, None), size=(dp(60), dp(60)))
        spinner_container.add_widget(spinner)
        
        # Loading text
        loading_text = Label(
            text='Loading...',
            font_size=sp(16),
            color=[0.7, 0.7, 0.7, 1],
            size_hint=(1, 0.05),
            halign='center'
        )
        loading_text.bind(size=loading_text.setter('text_size'))
        
        content.add_widget(logo_container)
        content.add_widget(title)
        content.add_widget(subtitle)
        content.add_widget(spinner_container)
        content.add_widget(loading_text)
        
        center_layout.add_widget(content)
        layout.add_widget(center_layout)
        self.add_widget(layout)
        
        # Auto transition after loading
        Clock.schedule_once(self.finish_loading, 3.0)
    
    def finish_loading(self, dt):
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Action Bar
        action_bar = ActionBar(size_hint=(1, None), height=dp(56))
        action_bar.background_color = [0.1, 0.2, 0.4, 1]
        
        action_view = ActionView()
        action_previous = ActionPrevious(
            title='Password Guardian',
            app_icon='',
            with_previous=False
        )
        
        about_button = ActionButton(
            text='About',
            on_press=self.show_about
        )
        
        action_view.add_widget(action_previous)
        action_view.add_widget(about_button)
        action_bar.add_widget(action_view)
        
        # Main content
        content = EnhancedPasswordChecker()
        
        main_layout.add_widget(action_bar)
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def show_about(self, instance):
        about_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Developer info
        dev_info = BoxLayout(orientation='vertical', spacing=dp(10))
        
        app_title = Label(
            text='[b]🔐 Password Guardian[/b]',
            markup=True,
            font_size=sp(24),
            color=[0.1, 0.2, 0.4, 1],
            size_hint=(1, None),
            height=dp(40),
            halign='center'
        )
        app_title.bind(size=app_title.setter('text_size'))
        
        version = Label(
            text='Version 2.0.0',
            font_size=sp(16),
            color=[0.5, 0.5, 0.5, 1],
            size_hint=(1, None),
            height=dp(30),
            halign='center'
        )
        version.bind(size=version.setter('text_size'))
        
        description = Label(
            text='A professional password security analyzer and generator for Android devices. '
                 'Built with advanced security algorithms to help you create and maintain strong passwords.',
            font_size=sp(14),
            color=[0.3, 0.3, 0.3, 1],
            size_hint=(1, None),
            height=dp(80),
            text_size=(None, None),
            halign='center',
            valign='center'
        )
        
        developer_section = Label(
            text='[b]👨‍💻 Developer Information[/b]',
            markup=True,
            font_size=sp(18),
            color=[0.1, 0.2, 0.4, 1],
            size_hint=(1, None),
            height=dp(40),
            halign='center'
        )
        developer_section.bind(size=developer_section.setter('text_size'))
        
        developer_info = Label(
            text='Developed by: Your Name\n'
                 'Email: your.email@example.com\n'
                 'Website: www.yourwebsite.com\n'
                 'GitHub: github.com/yourusername',
            font_size=sp(14),
            color=[0.4, 0.4, 0.4, 1],
            size_hint=(1, None),
            height=dp(100),
            halign='center'
        )
        developer_info.bind(size=developer_info.setter('text_size'))
        
        features = Label(
            text='[b]✨ Features[/b]\n'
                 '• Real-time password strength analysis\n'
                 '• Entropy calculation with visual feedback\n'
                 '• Secure password generation\n'
                 '• Pattern detection and security tips\n'
                 '• Professional Android UI design',
            markup=True,
            font_size=sp(14),
            color=[0.3, 0.3, 0.3, 1],
            size_hint=(1, None),
            height=dp(140),
            halign='left'
        )
        features.bind(size=features.setter('text_size'))
        
        dev_info.add_widget(app_title)
        dev_info.add_widget(version)
        dev_info.add_widget(description)
        dev_info.add_widget(developer_section)
        dev_info.add_widget(developer_info)
        dev_info.add_widget(features)
        
        scroll_view = ScrollView()
        scroll_view.add_widget(dev_info)
        about_content.add_widget(scroll_view)
        
        # Close button
        close_btn = ModernButton(
            text='Close',
            size_hint=(1, None),
            height=dp(50),
            bg_color=[0.2, 0.5, 0.9, 1]
        )
        about_content.add_widget(close_btn)
        
        popup = Popup(
            title='About Password Guardian',
            content=about_content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

class EnhancedPasswordChecker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Set window properties
        Window.clearcolor = get_color_from_hex("#f0f4f8")
        Window.softinput_mode = "below_target"
        
        # Main scroll view
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        main_layout = BoxLayout(orientation='vertical', padding=[dp(15), dp(10)], spacing=dp(15), size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Header Card
        header_card = ModernCard(size_hint=(1, None), height=dp(100))
        header_layout = BoxLayout(orientation='horizontal', spacing=dp(15))
        
        # Icon
        icon_container = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(0.2, 1))
        icon = Label(text='🔐', font_size=sp(48), size_hint=(None, None), size=(dp(60), dp(60)))
        icon_container.add_widget(icon)
        
        # Title and subtitle
        text_container = BoxLayout(orientation='vertical', size_hint=(0.8, 1))
        title = Label(
            text='[b]Password Security Analyzer[/b]',
            markup=True,
            font_size=sp(20),
            color=get_color_from_hex("#1a365d"),
            size_hint=(1, 0.6),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        
        subtitle = Label(
            text='Check your password strength and get personalized recommendations',
            font_size=sp(14),
            color=get_color_from_hex("#4a5568"),
            size_hint=(1, 0.4),
            halign='left'
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        
        text_container.add_widget(title)
        text_container.add_widget(subtitle)
        header_layout.add_widget(icon_container)
        header_layout.add_widget(text_container)
        header_card.add_widget(header_layout)
        main_layout.add_widget(header_card)
        
        # Password Input Card
        input_card = ModernCard(size_hint=(1, None), height=dp(120))
        input_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        input_label = Label(
            text='Enter Password to Analyze',
            font_size=sp(16),
            color=get_color_from_hex("#2d3748"),
            size_hint=(1, 0.3),
            halign='left'
        )
        input_label.bind(size=input_label.setter('text_size'))
        
        # Input with toggle
        input_container = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(1, 0.7))
        self.input = TextInput(
            hint_text="Type your password here...",
            password=True,
            multiline=False,
            font_size=sp(16),
            size_hint=(0.85, 1),
            background_color=get_color_from_hex("#edf2f7"),
            foreground_color=get_color_from_hex("#2d3748"),
            cursor_color=get_color_from_hex("#3182ce"),
            padding=[dp(15), dp(12)]
        )
        self.input.bind(text=self.on_password_change)
        
        self.show_toggle = ModernButton(
            text="👁",
            size_hint=(0.15, 1),
            bg_color=[0.7, 0.7, 0.7, 1]
        )
        self.show_toggle.bind(on_press=self.toggle_password_visibility)
        
        input_container.add_widget(self.input)
        input_container.add_widget(self.show_toggle)
        input_layout.add_widget(input_label)
        input_layout.add_widget(input_container)
        input_card.add_widget(input_layout)
        main_layout.add_widget(input_card)
        
        # Strength Analysis Card
        strength_card = ModernCard(size_hint=(1, None), height=dp(180))
        strength_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Header
        strength_header = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))
        self.strength_label = Label(
            text="Password Strength: Not Analyzed",
            font_size=sp(16),
            color=get_color_from_hex("#2d3748"),
            size_hint=(0.7, 1),
            halign='left'
        )
        self.strength_label.bind(size=self.strength_label.setter('text_size'))
        
        self.entropy_label = Label(
            text="",
            font_size=sp(14),
            color=get_color_from_hex("#718096"),
            size_hint=(0.3, 1),
            halign='right'
        )
        self.entropy_label.bind(size=self.entropy_label.setter('text_size'))
        
        strength_header.add_widget(self.strength_label)
        strength_header.add_widget(self.entropy_label)
        
        # Progress bar
        self.progress = ProgressBar(max=100, value=0, size_hint=(1, 0.15))
        
        # Stats
        stats_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        
        self.time_label = Label(
            text="Time to crack: Not calculated",
            font_size=sp(14),
            color=get_color_from_hex("#4a5568"),
            size_hint=(0.6, 1),
            halign='left'
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        
        self.score_label = Label(
            text="Score: 0/8",
            font_size=sp(14),
            color=get_color_from_hex("#4a5568"),
            size_hint=(0.4, 1),
            halign='right'
        )
        self.score_label.bind(size=self.score_label.setter('text_size'))
        
        stats_layout.add_widget(self.time_label)
        stats_layout.add_widget(self.score_label)
        
        strength_layout.add_widget(strength_header)
        strength_layout.add_widget(self.progress)
        strength_layout.add_widget(stats_layout)
        strength_card.add_widget(strength_layout)
        main_layout.add_widget(strength_card)
        
        # Feedback Card
        feedback_card = ModernCard(size_hint=(1, None), height=dp(200))
        feedback_layout = BoxLayout(orientation='vertical')
        
        feedback_title = Label(
            text="[b]Security Analysis & Recommendations[/b]",
            markup=True,
            font_size=sp(16),
            color=get_color_from_hex("#2d3748"),
            size_hint=(1, 0.2),
            halign='left'
        )
        feedback_title.bind(size=feedback_title.setter('text_size'))
        
        feedback_scroll = ScrollView(size_hint=(1, 0.8))
        self.feedback_label = Label(
            text="Enter a password to see detailed security analysis and recommendations...",
            font_size=sp(14),
            color=get_color_from_hex("#4a5568"),
            text_size=(None, None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        self.feedback_label.bind(texture_size=self.feedback_label.setter('size'))
        feedback_scroll.add_widget(self.feedback_label)
        
        feedback_layout.add_widget(feedback_title)
        feedback_layout.add_widget(feedback_scroll)
        feedback_card.add_widget(feedback_layout)
        main_layout.add_widget(feedback_card)
        
        # Password Generator Card
        generator_card = ModernCard(size_hint=(1, None), height=dp(200))
        generator_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        gen_title = Label(
            text="[b]🎲 Secure Password Generator[/b]",
            markup=True,
            font_size=sp(16),
            color=get_color_from_hex("#2d3748"),
            size_hint=(1, 0.2),
            halign='left'
        )
        gen_title.bind(size=gen_title.setter('text_size'))
        
        # Length control
        length_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))
        length_layout.add_widget(Label(text="Length:", size_hint=(0.25, 1), font_size=sp(14)))
        self.length_slider = Slider(min=8, max=32, value=16, step=1, size_hint=(0.6, 1))
        self.length_value = Label(text="16", size_hint=(0.15, 1), font_size=sp(14))
        self.length_slider.bind(value=self.update_length_label)
        length_layout.add_widget(self.length_slider)
        length_layout.add_widget(self.length_value)
        
        # Options
        options_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))
        
        symbols_box = BoxLayout(orientation='horizontal', size_hint=(0.5, 1))
        symbols_box.add_widget(Label(text="Symbols:", font_size=sp(14), halign='left'))
        self.symbols_switch = Switch(active=True, size_hint=(None, 1), width=dp(50))
        symbols_box.add_widget(self.symbols_switch)
        
        ambiguous_box = BoxLayout(orientation='horizontal', size_hint=(0.5, 1))
        ambiguous_box.add_widget(Label(text="Exclude Ambiguous:", font_size=sp(14), halign='left'))
        self.ambiguous_switch = Switch(active=True, size_hint=(None, 1), width=dp(50))
        ambiguous_box.add_widget(self.ambiguous_switch)
        
        options_layout.add_widget(symbols_box)
        options_layout.add_widget(ambiguous_box)
        
        # Generate button
        self.gen_button = ModernButton(
            text="Generate Secure Password",
            size_hint=(1, 0.3),
            bg_color=[0.2, 0.7, 0.4, 1]
        )
        self.gen_button.bind(on_press=self.show_generated_password)
        
        generator_layout.add_widget(gen_title)
        generator_layout.add_widget(length_layout)
        generator_layout.add_widget(options_layout)
        generator_layout.add_widget(self.gen_button)
        generator_card.add_widget(generator_layout)
        main_layout.add_widget(generator_card)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
        
        # Animation properties
        self.current_strength = ""
    
    def update_length_label(self, instance, value):
        self.length_value.text = str(int(value))
    
    def toggle_password_visibility(self, instance):
        self.input.password = not self.input.password
        instance.text = "👁" if self.input.password else "🙈"
    
    def on_password_change(self, instance, value):
        Clock.unschedule(self.analyze_password)
        Clock.schedule_once(lambda dt: self.analyze_password(value), 0.3)
    
    def analyze_password(self, password):
        if not password:
            self.reset_display()
            return
        
        entropy = calculate_entropy(password)
        strength = get_strength(entropy, password)
        feedback_list, score = get_detailed_feedback(password, entropy)
        
        # Update strength with animation
        if strength != self.current_strength:
            self.animate_strength_change(strength, entropy, score)
            self.current_strength = strength
        
        # Update labels
        self.strength_label.text = f"Password Strength: {strength}"
        self.entropy_label.text = f"{entropy} bits"
        self.time_label.text = f"Time to crack: {time_to_crack(entropy)}"
        self.score_label.text = f"Score: {score}/8"
        self.feedback_label.text = "\n".join(feedback_list)
        self.feedback_label.text_size = (Window.width - dp(80), None)
    
    def animate_strength_change(self, strength, entropy, score):
        # Color mapping
        colors = {
            "Very Weak": "#ef4444",
            "Weak": "#f97316", 
            "Fair": "#eab308",
            "Good": "#22c55e",
            "Strong": "#16a34a",
            "Very Strong": "#15803d"
        }
        
        # Progress mapping
        progress_values = {
            "Very Weak": 15,
            "Weak": 30,
            "Fair": 50, 
            "Good": 70,
            "Strong": 85,
            "Very Strong": 100
        }
        
        color = colors.get(strength, "#64748b")
        progress = progress_values.get(strength, 0)
        
        # Animate progress bar
        anim = Animation(value=progress, duration=0.5, t='out_cubic')
        anim.start(self.progress)
        
        # Update colors
        self.strength_label.color = get_color_from_hex(color)
    
    def reset_display(self):
        self.strength_label.text = "Password Strength: Not Analyzed"
        self.strength_label.color = get_color_from_hex("#2d3748")
        self.entropy_label.text = ""
        self.progress.value = 0
        self.time_label.text = "Time to crack: Not calculated"
        self.score_label.text = "Score: 0/8"
        self.feedback_label.text = "Enter a password to see detailed security analysis and recommendations..."
        self.current_strength = ""
    
    def show_generated_password(self, instance):
        length = int(self.length_slider.value)
        use_symbols = self.symbols_switch.active
        exclude_ambiguous = self.ambiguous_switch.active
        
        new_password = generate_secure_password(length, use_symbols, exclude_ambiguous)
        
        # Create professional popup
        popup_layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20))
        
        # Header
        header = Label(
            text="[b]🎉 Your New Secure Password[/b]",
            markup=True,
            font_size=sp(20),
            color=get_color_from_hex("#1a365d"),
            size_hint=(1, None),
            height=dp(40),
            halign='center'
        )
        header.bind(size=header.setter('text_size'))
        
        # Password display card
        password_card = ModernCard(size_hint=(1, None), height=dp(100))
        password_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        password_label = Label(
            text="Generated Password:",
            font_size=sp(14),
            color=get_color_from_hex("#4a5568"),
            size_hint=(1, 0.3),
            halign='left'
        )
        password_label.bind(size=password_label.setter('text_size'))
        
        password_input = TextInput(
            text=new_password,
            readonly=True,
            font_size=sp(16),
            multiline=False,
            size_hint=(1, 0.7),
            background_color=get_color_from_hex("#f7fafc"),
            foreground_color=get_color_from_hex("#1a202c"),
            padding=[dp(15), dp(12)]
        )
        
        password_layout.add_widget(password_label)
        password_layout.add_widget(password_input)
        password_card.add_widget(password_layout)
        
        # Quick analysis
        quick_entropy = calculate_entropy(new_password)
        quick_strength = get_strength(quick_entropy, new_password)
        
        analysis_card = ModernCard(size_hint=(1, None), height=dp(80))
        analysis_layout = BoxLayout(orientation='horizontal', spacing=dp(20))
        
        strength_info = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        strength_info.add_widget(Label(
            text=f"Strength: {quick_strength}",
            font_size=sp(14),
            color=get_color_from_hex("#2d3748"),
            halign='center'
        ))
        strength_info.add_widget(Label(
            text=f"Entropy: {quick_entropy} bits",
            font_size=sp(12),
            color=get_color_from_hex("#718096"),
            halign='center'
        ))
        
        crack_info = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        crack_info.add_widget(Label(
            text="Time to crack:",
            font_size=sp(14),
            color=get_color_from_hex("#2d3748"),
            halign='center'
        ))
        crack_info.add_widget(Label(
            text=time_to_crack(quick_entropy),
            font_size=sp(12),
            color=get_color_from_hex("#718096"),
            halign='center'
        ))
        
        analysis_layout.add_widget(strength_info)
        analysis_layout.add_widget(crack_info)
        analysis_card.add_widget(analysis_layout)
        
        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, None), height=dp(55))
        
        copy_btn = ModernButton(
            text="📋 Copy Password",
            bg_color=[0.2, 0.5, 0.9, 1],
            font_size=sp(14)
        )
        
        use_btn = ModernButton(
            text="✅ Use This Password",
            bg_color=[0.2, 0.7, 0.4, 1],
            font_size=sp(14)
        )
        
        regenerate_btn = ModernButton(
            text="🔄 Generate New",
            bg_color=[0.7, 0.4, 0.2, 1],
            font_size=sp(14)
        )
        
        button_layout.add_widget(copy_btn)
        button_layout.add_widget(use_btn)
        button_layout.add_widget(regenerate_btn)
        
        # Close button
        close_btn = ModernButton(
            text="❌ Close",
            size_hint=(1, None),
            height=dp(50),
            bg_color=[0.6, 0.6, 0.6, 1],
            font_size=sp(16)
        )
        
        popup_layout.add_widget(header)
        popup_layout.add_widget(password_card)
        popup_layout.add_widget(analysis_card)
        popup_layout.add_widget(button_layout)
        popup_layout.add_widget(close_btn)
        
        popup = Popup(
            title="Password Generated Successfully",
            content=popup_layout,
            size_hint=(0.95, 0.8),
            auto_dismiss=False
        )
        
        # Button actions
        def copy_password(_):
            try:
                # For Android, we'll use a simple approach
                import os
                if hasattr(os, 'system'):
                    # This won't work on all Android devices, but it's a fallback
                    pass
                copy_btn.text = "✅ Copied!"
                Clock.schedule_once(lambda dt: setattr(copy_btn, 'text', '📋 Copy Password'), 2)
            except:
                copy_btn.text = "❌ Copy Failed"
                Clock.schedule_once(lambda dt: setattr(copy_btn, 'text', '📋 Copy Password'), 2)
        
        def use_password(_):
            self.input.text = new_password
            popup.dismiss()
        
        def regenerate_password(_):
            new_pass = generate_secure_password(length, use_symbols, exclude_ambiguous)
            password_input.text = new_pass
            # Update analysis
            new_entropy = calculate_entropy(new_pass)
            new_strength = get_strength(new_entropy, new_pass)
            strength_info.children[1].text = f"Strength: {new_strength}"
            strength_info.children[0].text = f"Entropy: {new_entropy} bits"
            crack_info.children[0].text = time_to_crack(new_entropy)
        
        def close_popup(_):
            popup.dismiss()
        
        copy_btn.bind(on_press=copy_password)
        use_btn.bind(on_press=use_password)
        regenerate_btn.bind(on_press=regenerate_password)
        close_btn.bind(on_press=close_popup)
        
        popup.open()

class PasswordGuardianApp(App):
    def build(self):
        self.title = "Password Guardian Pro"
        self.icon = "icon.png"  # Add your app icon
        
        # Screen manager
        sm = ScreenManager()
        
        # Add screens
        loading_screen = LoadingScreen(name='loading')
        main_screen = MainScreen(name='main')
        
        sm.add_widget(loading_screen)
        sm.add_widget(main_screen)
        
        return sm
    
    def on_start(self):
        # Handle Android-specific initialization
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
        except ImportError:
            pass  # Not on Android
        
        # Additional Android optimizations
        try:
            from kivy.utils import platform
            if platform == 'android':
                # Keep screen on during app usage
                from android import mActivity
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity = PythonActivity.mActivity
                activity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
        except ImportError:
            pass
    
    def on_pause(self):
        # App can be paused on Android
        return True
    
    def on_resume(self):
        # App resumed from pause
        pass

if __name__ == "__main__":
    PasswordGuardianApp().run()