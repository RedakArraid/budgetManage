"""
CSS styles for the BudgetManage application
"""

def load_css():
    """Load and return the CSS styles"""
    return """
    <style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    
    .stApp {
        background-color: #0e1117;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e1e1e;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(90deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #333;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.2);
    }
    
    .demand-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #262626 100%);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .demand-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.15);
    }
    
    /* Notifications */
    .notification-card {
        background: #1a1a2e;
        border: 1px solid #16213e;
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .notification-unread {
        background: #2d1b2e;
        border-left-color: #ff6b6b;
    }
    
    /* Status badges */
    .status-brouillon { 
        background-color: #6c757d; 
        color: white; 
        padding: 3px 8px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: bold;
    }
    .status-en_attente_dr { 
        background-color: #ffc107; 
        color: black; 
        padding: 3px 8px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: bold;
    }
    .status-en_attente_financier { 
        background-color: #fd7e14; 
        color: white; 
        padding: 3px 8px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: bold;
    }
    .status-validee { 
        background-color: #28a745; 
        color: white; 
        padding: 3px 8px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: bold;
    }
    .status-rejetee { 
        background-color: #dc3545; 
        color: white; 
        padding: 3px 8px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        transform: translateY(-2px);
    }
    
    /* Secondary buttons */
    .stButton>button[kind="secondary"] {
        background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
    }
    
    /* Form inputs */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #444;
        border-radius: 5px;
    }
    
    /* Form labels - make them white instead of gray */
    .stTextInput>label, 
    .stTextArea>label, 
    .stSelectbox>label,
    .stNumberInput>label,
    .stDateInput>label,
    .stFileUploader>label,
    .stCheckbox>label,
    .stRadio>label,
    .stSlider>label {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Form field labels in Streamlit - modern selectors */
    div[data-testid="stWidgetLabel"] > label,
    div[data-testid="stWidgetLabel"] p,
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stDateInput label,
    .stMultiSelect label,
    .stRadio label,
    .stCheckbox label,
    .stSlider label,
    .stFileUploader label {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Ensure all form labels are white */
    .stFormSubmitButton>label,
    .stForm label,
    label {
        color: white !important;
    }
    
    /* Specific for Streamlit widget labels */
    [data-testid="stWidgetLabel"] {
        color: white !important;
    }
    
    /* Additional modern Streamlit selectors for labels */
    .st-emotion-cache-1wmy9hl,
    .st-emotion-cache-1wmy9hl p,
    .st-emotion-cache-j5r0tf,
    .st-emotion-cache-j5r0tf p,
    .element-container label,
    .widget-label,
    [data-testid="stMarkdownContainer"] label {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Force all labels and p elements in widgets to be white */
    .stTextInput p,
    .stTextArea p,
    .stSelectbox p,
    .stNumberInput p,
    .stDateInput p,
    .stMultiSelect p,
    .stRadio p,
    .stCheckbox p,
    .stSlider p,
    .stFileUploader p {
        color: white !important;
    }
    
    /* Form headers and subheaders */
    .stForm [data-testid="stMarkdownContainer"] h1,
    .stForm [data-testid="stMarkdownContainer"] h2,
    .stForm [data-testid="stMarkdownContainer"] h3,
    .stForm [data-testid="stMarkdownContainer"] h4,
    .stForm [data-testid="stMarkdownContainer"] h5,
    .stForm [data-testid="stMarkdownContainer"] h6 {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Date input */
    .stDateInput>div>div>input {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #444;
        border-radius: 5px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Make sure all text in forms is white */
    .stForm h1, .stForm h2, .stForm h3, .stForm h4, .stForm h5, .stForm h6 {
        color: white !important;
        font-weight: bold !important;
    }
    
    /* Markdown text in forms */
    .stMarkdown p, .stMarkdown div {
        color: white !important;
    }
    
    /* Role badges */
    .role-admin { 
        background: linear-gradient(135deg, #ff6b6b, #ee5a24); 
        color: white; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    .role-tc { 
        background: linear-gradient(135deg, #74b9ff, #0984e3); 
        color: white; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    .role-dr { 
        background: linear-gradient(135deg, #fdcb6e, #e17055); 
        color: white; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    .role-dr_financier { 
        background: linear-gradient(135deg, #a29bfe, #6c5ce7); 
        color: white; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    .role-dg { 
        background: linear-gradient(135deg, #fd79a8, #e84393); 
        color: white; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    .role-marketing { 
        background: linear-gradient(135deg, #55efc4, #00b894); 
        color: white; 
        padding: 4px 12px; 
        border-radius: 15px; 
        font-size: 0.8rem; 
        font-weight: bold; 
    }
    
    /* Login form */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #333;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header h1 {
        color: #4CAF50;
        margin: 0;
        font-size: 3rem;
    }
    
    .login-header h2 {
        margin: 0.5rem 0;
        color: white;
    }
    
    .login-header p {
        color: #888;
        margin: 0;
    }
    
    /* Tables */
    .stDataFrame {
        background-color: #1e1e1e;
    }
    
    .stDataFrame table {
        background-color: #1e1e1e;
        color: white;
    }
    
    .stDataFrame th {
        background-color: #2d2d2d;
        color: white;
        border-bottom: 1px solid #444;
    }
    
    .stDataFrame td {
        border-bottom: 1px solid #333;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2d2d2d;
        color: white;
    }
    
    .streamlit-expanderContent {
        background-color: #1e1e1e;
        border: 1px solid #333;
    }
    
    /* Sidebar navigation */
    .nav-button {
        width: 100%;
        margin: 0.2rem 0;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 5px;
        background: linear-gradient(135deg, #333 0%, #444 100%);
        color: white;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        transform: translateX(5px);
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
    }
    
    /* Charts */
    .plotly-graph-div {
        background-color: transparent !important;
    }
    
    /* Metrics */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-item {
        flex: 1;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        border-radius: 8px;
        border: 1px solid #333;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #888;
        margin: 0;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.1);
        border: 1px solid #28a745;
        color: #28a745;
    }
    
    /* Error messages */
    .stError {
        background-color: rgba(220, 53, 69, 0.1);
        border: 1px solid #dc3545;
        color: #dc3545;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        border: 1px solid #ffc107;
        color: #ffc107;
    }
    
    /* Info messages */
    .stInfo {
        background-color: rgba(23, 162, 184, 0.1);
        border: 1px solid #17a2b8;
        color: #17a2b8;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background-color: #2d2d2d;
        border: 2px dashed #444;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e1e1e;
        border-bottom: 1px solid #333;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #888;
        background-color: transparent;
        border: none;
        padding: 1rem 2rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #4CAF50;
        border-bottom: 2px solid #4CAF50;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #4CAF50 !important;
    }
    
    /* Checkbox and radio */
    .stCheckbox > label {
        color: white;
    }
    
    .stRadio > label {
        color: white;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Custom classes for workflow status */
    .workflow-step {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        background-color: #2d2d2d;
    }
    
    .workflow-step.active {
        background-color: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4CAF50;
    }
    
    .workflow-step.completed {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 4px solid #28a745;
    }
    
    .workflow-step.rejected {
        background-color: rgba(220, 53, 69, 0.1);
        border-left: 4px solid #dc3545;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e1e1e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4CAF50;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #45a049;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .metric-container {
            flex-direction: column;
        }
        
        .header-container {
            padding: 1rem;
        }
        
        .demand-card {
            padding: 1rem;
        }
    }
    </style>
    """
