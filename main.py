import streamlit as st
import json
import re
import traceback
import sys
from io import StringIO
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import time

# Page configuration
st.set_page_config(
    page_title="SHL Coding Exam Prep",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Try to import streamlit-ace for better code editing
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False
    st.warning("streamlit-ace not found. Using basic text area for code editing.")

# Custom CSS for better styling
st.markdown("""
<style>
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .hint-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .problem-stats {
        display: flex;
        gap: 1rem;
        margin: 0.5rem 0;
    }
    .stat-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
    }
    .failure-badge {
        background-color: #dc3545;
        color: white;
    }
    .total-badge {
        background-color: #6c757d;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'problems' not in st.session_state:
        st.session_state.problems = load_problems()
    if 'selected_problem' not in st.session_state:
        st.session_state.selected_problem = None
    if 'user_stats' not in st.session_state:
        st.session_state.user_stats = defaultdict(lambda: {'success': 0, 'failure': 0})
    if 'show_hints' not in st.session_state:
        st.session_state.show_hints = defaultdict(bool)
    if 'current_hint_index' not in st.session_state:
        st.session_state.current_hint_index = defaultdict(int)

def load_problems():
    """Load problems from JSON file"""
    try:
        # Try to load from uploaded file first
        if hasattr(st.session_state, 'uploaded_problems') and st.session_state.uploaded_problems:
            return st.session_state.uploaded_problems
        
        # Try to load from local file
        try:
            with open('shl_problems.json', 'r', encoding='utf-8') as f:
                problems_data = json.load(f)
                return {problem['id']: problem for problem in problems_data['problems']}
        except FileNotFoundError:
            st.error("❌ JSON file 'shl_problems.json' not found. Please upload a problems file.")
            st.info("💡 Create a JSON file with the problems data or upload one using the file uploader below.")
            return {}
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON format: {str(e)}")
            return {}
    except Exception as e:
        st.error(f"❌ Error loading problems: {str(e)}")
        return {}

def execute_user_code(user_code, test_cases):
    """Execute user code safely and run test cases"""
    results = []
    
    try:
        # Create a namespace for execution
        namespace = {}
        
        # Execute the user's code
        exec(user_code, namespace)
        
        # Extract the function (assume it's the first function defined)
        function_name = None
        for name, obj in namespace.items():
            if callable(obj) and not name.startswith('_'):
                function_name = name
                break
        
        if not function_name:
            return False, "No function found in your code"
        
        user_function = namespace[function_name]
        
        # Run test cases
        passed = 0
        total = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            try:
                # Prepare input arguments
                args = test_case['input']
                expected = test_case['expected']
                
                # Call the function
                if len(args) == 1:
                    result = user_function(args[0])
                else:
                    result = user_function(*args)
                
                # Compare result
                if result == expected:
                    results.append(f"✅ Test case {i+1}: PASSED")
                    passed += 1
                else:
                    results.append(f"❌ Test case {i+1}: FAILED - Expected {expected}, got {result}")
                    
            except Exception as e:
                results.append(f"❌ Test case {i+1}: ERROR - {str(e)}")
        
        success = passed == total
        summary = f"Passed {passed}/{total} test cases"
        
        return success, summary + "\n\n" + "\n".join(results)
        
    except Exception as e:
        return False, f"Code execution error: {str(e)}\n\n{traceback.format_exc()}"

def display_problem_stats(problem_id):
    """Display statistics for a problem"""
    stats = st.session_state.user_stats[problem_id]
    total = stats['success'] + stats['failure']
    
    if total > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<span class="stat-badge success-badge">✅ {stats["success"]}</span>', 
                       unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="stat-badge failure-badge">❌ {stats["failure"]}</span>', 
                       unsafe_allow_html=True)
        with col3:
            st.markdown(f'<span class="stat-badge total-badge">📊 {total}</span>', 
                       unsafe_allow_html=True)

def main():
    init_session_state()
    
    st.title("🎯 SHL Coding Exam Preparation Tool")
    st.markdown("Practice coding problems similar to those found in SHL assessments")
    
    # Sidebar for problem selection
    with st.sidebar:
        st.header("📋 Problems")
        
        # Check if problems are loaded
        if not st.session_state.problems:
            st.error("❌ No problems loaded!")
            st.info("💡 Please create 'shl_problems.json' in your project directory or upload a problems file below.")
            
            # File uploader for problems JSON
            uploaded_file = st.file_uploader(
                "Upload Problems JSON File",
                type=['json'],
                help="Upload a JSON file containing the problems data"
            )
            
            if uploaded_file is not None:
                try:
                    # Read and parse the uploaded file
                    content = uploaded_file.read().decode('utf-8')
                    problems_data = json.loads(content)
                    
                    # Store in session state and reload
                    st.session_state.uploaded_problems = {problem['id']: problem for problem in problems_data['problems']}
                    st.session_state.problems = st.session_state.uploaded_problems
                    st.success("✅ Problems loaded successfully!")
                    st.rerun()  # Refresh the app
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
            
            return
        
        # Overall progress
        total_problems = len(st.session_state.problems)
        solved_problems = sum(1 for problem_id in st.session_state.problems.keys() 
                            if st.session_state.user_stats[problem_id]['success'] > 0)
        
        # Avoid division by zero
        progress_percentage = (solved_problems/total_problems*100) if total_problems > 0 else 0
        
        st.metric("Progress", f"{solved_problems}/{total_problems}", 
                 f"{progress_percentage:.1f}%")
        
        st.markdown("---")
        
        # Problem list
        for problem_id, problem in st.session_state.problems.items():
            stats = st.session_state.user_stats[problem_id]
            success_rate = ""
            if stats['success'] + stats['failure'] > 0:
                rate = stats['success'] / (stats['success'] + stats['failure']) * 100
                success_rate = f" ({rate:.0f}%)"
            
            status_icon = "✅" if stats['success'] > 0 else "⭕"
            
            if st.button(f"{status_icon} {problem['title']}{success_rate}", 
                        key=f"problem_{problem_id}",
                        use_container_width=True):
                st.session_state.selected_problem = problem_id
                st.session_state.show_hints[problem_id] = False
                st.session_state.current_hint_index[problem_id] = 0
    
    # Main content area
    if st.session_state.selected_problem is None:
        st.markdown("""
        ## Welcome to the SHL Coding Exam Prep Tool! 👋
        
        This tool helps you practice coding problems similar to those found in SHL assessments.
        
        ### How to use:
        1. **Select a problem** from the sidebar
        2. **Read the problem statement** carefully
        3. **Write your solution** in the code editor
        4. **Submit** to test your solution
        5. **Use hints** if you get stuck
        6. **Track your progress** and improve over time
        
        ### Features:
        - ✅ Real-time code testing
        - 💡 Progressive hints
        - 📊 Progress tracking
        - 🎯 SHL-style problems
        
        **Select a problem from the sidebar to get started!**
        """)
        return
    
    # Display selected problem
    problem = st.session_state.problems[st.session_state.selected_problem]
    
    st.header(f"Problem {problem['id']}: {problem['title']}")
    
    # Problem statistics
    display_problem_stats(problem['id'])
    
    # Problem statement
    st.subheader("📝 Problem Statement")
    st.markdown(problem['statement'])
    
    # Function signature
    st.subheader("✏️ Function Signature")
    st.code(problem['function_signature'], language='python')
    
    # Hints section
    st.subheader("💡 Hints")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Show Next Hint", key="hint_button"):
            st.session_state.show_hints[problem['id']] = True
            current_idx = st.session_state.current_hint_index[problem['id']]
            if current_idx < len(problem['hints']) - 1:
                st.session_state.current_hint_index[problem['id']] += 1
    
    with col2:
        if st.button("Reset Hints", key="reset_hints"):
            st.session_state.show_hints[problem['id']] = False
            st.session_state.current_hint_index[problem['id']] = 0
    
    if st.session_state.show_hints[problem['id']]:
        hint_idx = st.session_state.current_hint_index[problem['id']]
        for i in range(hint_idx + 1):
            st.markdown(f'<div class="hint-box">💡 <strong>Hint {i+1}:</strong> {problem["hints"][i]}</div>', 
                       unsafe_allow_html=True)
    
    # Code editor
    st.subheader("👨‍💻 Your Solution")
    
    # Pre-fill with function signature
    default_code = problem['function_signature'] + "\n    # Your code here\n    pass"
    
    if ACE_AVAILABLE:
        user_code = st_ace(
            value=default_code,
            language='python',
            theme='monokai',
            key=f"ace_editor_{problem['id']}",
            height=300,
            auto_update=True,
            font_size=14,
            tab_size=4,
            wrap=False,
            annotations=None,
            markers=None
        )
    else:
        user_code = st.text_area(
            "Write your solution:",
            value=default_code,
            height=300,
            key=f"code_editor_{problem['id']}"
        )
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Submit Solution", type="primary"):
            if user_code.strip():
                with st.spinner("Testing your solution..."):
                    success, result = execute_user_code(user_code, problem['test_cases'])
                    
                    # Update statistics
                    if success:
                        st.session_state.user_stats[problem['id']]['success'] += 1
                        st.markdown(f'<div class="success-box">🎉 <strong>Success!</strong><br>{result}</div>', 
                                   unsafe_allow_html=True)
                    else:
                        st.session_state.user_stats[problem['id']]['failure'] += 1
                        st.markdown(f'<div class="error-box">❌ <strong>Failed!</strong><br>{result}</div>', 
                                   unsafe_allow_html=True)
            else:
                st.error("Please write some code before submitting!")
    
    with col2:
        if st.button("👀 Show Solution"):
            st.subheader("📚 Reference Solution")
            st.code(problem['solution'], language='python')
            
            # Test the reference solution
            success, result = execute_user_code(problem['solution'], problem['test_cases'])
            st.markdown(f'<div class="success-box">✅ <strong>Reference Solution Test Results:</strong><br>{result}</div>', 
                       unsafe_allow_html=True)
    
    # Test cases preview
    with st.expander("👁️ View Test Cases"):
        st.markdown("**Test Cases:**")
        for i, test_case in enumerate(problem['test_cases']):
            st.markdown(f"**Test {i+1}:**")
            st.markdown(f"- Input: `{test_case['input']}`")
            st.markdown(f"- Expected Output: `{test_case['expected']}`")

if __name__ == "__main__":
    main()
