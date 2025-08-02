import streamlit as st
import json
import re
import traceback
import sys
from io import StringIO
from collections import defaultdict
from urllib.parse import urlparse, parse_qs
import time
from default_problems import get_default_problems

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
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
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
    """Load problems from memory and merge with uploaded problems"""
    # Start with default problems
    all_problems = get_default_problems()
    
    # Add uploaded problems if any
    if hasattr(st.session_state, 'uploaded_problems') and st.session_state.uploaded_problems:
        # Merge uploaded problems, giving them IDs starting from 21
        next_id = max(all_problems.keys()) + 1
        for problem in st.session_state.uploaded_problems.values():
            # Create a copy of the problem with a new ID if it conflicts
            new_problem = problem.copy()
            if problem['id'] in all_problems:
                new_problem['id'] = next_id
                next_id += 1
            all_problems[new_problem['id']] = new_problem
    
    return all_problems

def execute_user_code(code, test_cases):
    """Execute user code with test cases and return results"""
    try:
        # Create a local namespace for execution
        local_namespace = {}
        
        # Execute the user's code
        exec(code, local_namespace)
        
        # Find the function name from the code (assumes single function definition)
        func_name = None
        for name, obj in local_namespace.items():
            if callable(obj) and not name.startswith('__'):
                func_name = name
                break
        
        if not func_name:
            return False, "No function found in your code"
        
        user_function = local_namespace[func_name]
        results = []
        
        # Test each case
        for i, case in enumerate(test_cases):
            try:
                # Call function with test input
                result = user_function(*case['input'])
                expected = case['expected']
                
                if result == expected:
                    results.append(f"✅ Test {i+1}: PASSED")
                else:
                    results.append(f"❌ Test {i+1}: FAILED<br>Expected: {expected}<br>Got: {result}")
            except Exception as e:
                results.append(f"❌ Test {i+1}: ERROR - {str(e)}")
        
        # Check if all tests passed
        all_passed = all("PASSED" in result for result in results)
        return all_passed, "<br>".join(results)
        
    except Exception as e:
        return False, f"Error executing code: {str(e)}"

def test_user_code(code):
    """Execute user code for testing and capture output"""
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr
    
    try:
        # Create string buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Create a local namespace for execution
        local_namespace = {}
        
        # Redirect stdout and stderr to capture print statements and errors
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Execute the user's code
            exec(code, local_namespace)
        
        # Get the captured output
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()
        
        # Find the function name from the code (assumes single function definition)
        func_name = None
        for name, obj in local_namespace.items():
            if callable(obj) and not name.startswith('__'):
                func_name = name
                break
        
        # Prepare result message
        result_parts = []
        
        if stdout_output:
            result_parts.append(f"<strong>Output:</strong><br><pre>{stdout_output}</pre>")
        
        if stderr_output:
            result_parts.append(f"<strong>Errors:</strong><br><pre style='color: red;'>{stderr_output}</pre>")
        
        if func_name:
            result_parts.append(f"<strong>Function found:</strong> {func_name}()")
        else:
            result_parts.append("<strong>⚠️ Warning:</strong> No function found in your code")
        
        if not stdout_output and not stderr_output:
            result_parts.append("<strong>Info:</strong> Code executed successfully (no output)")
        
        return True, "<br><br>".join(result_parts)
        
    except Exception as e:
        return False, f"<strong>Execution Error:</strong><br><pre style='color: red;'>{str(e)}</pre>"

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
        
        # File uploader for additional problems
        with st.expander("📁 Upload Additional Problems"):
            st.markdown("**Upload a JSON file to add more problems**")
            uploaded_file = st.file_uploader(
                "Select JSON file",
                type=['json'],
                help="Upload a JSON file containing additional problems in the same format"
            )
            
            if uploaded_file is not None:
                try:
                    # Read and parse the uploaded file
                    content = uploaded_file.read().decode('utf-8')
                    problems_data = json.loads(content)
                    
                    # Store in session state and reload
                    if 'problems' in problems_data:
                        st.session_state.uploaded_problems = {problem['id']: problem for problem in problems_data['problems']}
                    else:
                        # Assume the uploaded file is a list of problems
                        st.session_state.uploaded_problems = {problem['id']: problem for problem in problems_data}
                    
                    # Reload all problems (this will merge default + uploaded)
                    st.session_state.problems = load_problems()
                    st.success(f"✅ {len(st.session_state.uploaded_problems)} additional problems loaded!")
                    st.rerun()  # Refresh the app
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON format: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
        
        st.markdown("---")
        
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
        
        ### 🎯 Features:
        - **20 Built-in Problems**: Ready-to-use coding challenges covering common topics
        - **Upload Additional Problems**: Add your own problems via JSON file upload
        - **Real-time Testing**: Instant feedback on your solutions
        - **Progressive Hints**: Get help when you're stuck
        - **Progress Tracking**: Monitor your success rate and improvement
        
        ### 🚀 How to use:
        1. **Select a problem** from the sidebar (20 problems available by default)
        2. **Read the problem statement** and examples carefully
        3. **Write your solution** in the code editor
        4. **Submit** to test against multiple test cases
        5. **Use hints** if you need guidance
        6. **Track your progress** and identify areas for improvement
        
        ### 📁 Adding More Problems:
        You can upload additional problems by:
        - Using the "Upload Additional Problems" section in the sidebar
        - Uploading a JSON file with problems in the same format
        - Problems will be merged with the existing 20 default problems
        
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
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        test_clicked = st.button("🔍 Test Solution", use_container_width=True)
    
    with col2:
        submit_clicked = st.button("🚀 Submit Solution", type="primary", use_container_width=True)
    
    with col3:
        show_solution_clicked = st.button("👀 Show Solution", use_container_width=True)
    
    # Handle test button click
    if test_clicked:
        if user_code.strip():
            with st.spinner("Testing your code..."):
                success, result = test_user_code(user_code)
                if success:
                    st.markdown(f'<div class="info-box">🔍 <strong>Test Results:</strong><br>{result}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ <strong>Test Failed:</strong><br>{result}</div>', 
                               unsafe_allow_html=True)
        else:
            st.error("Please write some code before testing!")
    
    # Handle submit button click
    if submit_clicked:
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
    
    # Handle show solution button click - display in full width
    if show_solution_clicked:
        st.markdown("---")
        st.subheader("📚 Reference Solution")
        
        # Use full width container for the solution
        if ACE_AVAILABLE:
            st_ace(
                value=problem['solution'],
                language='python',
                theme='monokai',
                key=f"solution_editor_{problem['id']}",
                height=250,
                auto_update=False,
                font_size=14,
                tab_size=4,
                wrap=False,
                readonly=True
            )
        else:
            st.text_area(
                "Reference Solution:",
                value=problem['solution'],
                height=250,
                key=f"solution_display_{problem['id']}",
                disabled=True
            )
        
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