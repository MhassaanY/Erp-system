import streamlit as st
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
import pandas as pd

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api")

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.last_activity = None
    st.session_state.inventory = []
    st.session_state.filtered_inventory = []

# Set page config
st.set_page_config(
    page_title="ERP System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        max-width: 1200px;
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
    .success-msg {
        color: #198754;
        font-weight: 500;
    }
    .error-msg {
        color: #dc3545;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def check_session_timeout() -> bool:
    """Check if the session has timed out due to inactivity"""
    if st.session_state.last_activity:
        inactive_duration = datetime.now() - st.session_state.last_activity
        if inactive_duration > timedelta(minutes=30):  # 30 minutes timeout
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.last_activity = None
            st.error("Your session has timed out. Please log in again.")
            return False
    st.session_state.last_activity = datetime.now()
    return True

def make_authenticated_request(method: str, endpoint: str, **kwargs) -> Optional[Dict]:
    """Helper function to make authenticated API requests"""
    if not st.session_state.token:
        return None
    
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f"Bearer {st.session_state.token}"
    
    try:
        url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:  # Unauthorized
            st.session_state.token = None
            st.session_state.user = None
            st.error("Your session has expired. Please log in again.")
            st.rerun()
            return None
            
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def login(username: str, password: str) -> bool:
    """Authenticate user with the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": username, "password": password, "grant_type": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            
            # Get user info
            user_response = make_authenticated_request("GET", "/users/me")
            if user_response and user_response.status_code == 200:
                st.session_state.user = user_response.json()
                st.session_state.last_activity = datetime.now()
                st.session_state.inventory = []
                st.session_state.filtered_inventory = []
                load_inventory()
                return True
        else:
            error_detail = response.json().get("detail", "Invalid credentials")
            st.error(f"Login failed: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def register(username: str, email: str, password: str) -> bool:
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/register",
            json={"username": username, "email": email, "password": password}
        )
        
        if response.status_code == 201:
            st.success("Registration successful! You can now log in.")
            return True
        else:
            error_detail = response.json().get("detail", "Registration failed")
            if isinstance(error_detail, dict):
                for field, errors in error_detail.items():
                    if isinstance(errors, list):
                        st.error(f"{field}: {', '.join(errors)}")
                    else:
                        st.error(f"{field}: {errors}")
            else:
                st.error(f"Registration failed: {error_detail}")
            return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False

def load_inventory():
    """Load inventory items from the API"""
    response = make_authenticated_request("GET", "/items/")
    if response and response.status_code == 200:
        st.session_state.inventory = response.json()
        st.session_state.filtered_inventory = st.session_state.inventory.copy()

# UI Components
def show_login_form():
    """Display login form"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://via.placeholder.com/200x50?text=ERP+System", width=200)
        st.markdown("<h2 style='text-align: center;'>Welcome Back</h2>", unsafe_allow_html=True)
        
        # Login Form
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password")
                elif login(username, password):
                    st.rerun()
        
        # Registration Section
        st.markdown("<div style='text-align: center; margin: 20px 0;'>OR</div>", unsafe_allow_html=True)
        
        with st.expander("Create New Account", expanded=False):
            with st.form("register_form"):
                new_username = st.text_input("Choose a username", key="reg_username")
                new_email = st.text_input("Email", key="reg_email")
                new_password = st.text_input("Choose a password", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm password", type="password", key="reg_confirm_password")
                
                if st.form_submit_button("Register", use_container_width=True):
                    if not all([new_username, new_email, new_password, confirm_password]):
                        st.error("All fields are required")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        register(new_username, new_email, new_password)

def show_sidebar():
    """Display the sidebar with user info and navigation"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Logo", width=150)
        st.markdown(f"### {st.session_state.user['username']}")
        st.markdown(f"*{st.session_state.user['email']}*")
        
        st.markdown("---")
        
        # Navigation
        menu = ["Dashboard", "Inventory", "Reports", "Settings"]
        selection = st.sidebar.radio("Navigation", menu, index=0)
        
        st.markdown("---")
        
        # Quick Stats
        if st.session_state.inventory:
            total_items = len(st.session_state.inventory)
            total_quantity = sum(item['quantity'] for item in st.session_state.inventory)
            total_value = sum(item['quantity'] * item['price'] for item in st.session_state.inventory)
            
            st.markdown("### Quick Stats")
            st.metric("Total Items", total_items)
            st.metric("Total Quantity", total_quantity)
            st.metric("Total Value", f"${total_value:,.2f}")
        
        st.markdown("---")
        
        # Logout button
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("*ERP System v1.0.0*")
        st.markdown("* 2023 Your Company*")
    
    return selection

def show_inventory():
    """Display inventory management interface"""
    st.title(" Inventory Management")
    
    # Filters
    with st.expander(" Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            name_filter = st.text_input("Search by name")
        with col2:
            min_qty = st.number_input("Min quantity", min_value=0, value=0)
        with col3:
            max_price = st.number_input("Max price", min_value=0.0, value=1000.0, step=10.0)
    
    # Apply filters
    filtered = st.session_state.inventory.copy()
    if name_filter:
        filtered = [item for item in filtered if name_filter.lower() in item['name'].lower()]
    if min_qty > 0:
        filtered = [item for item in filtered if item['quantity'] >= min_qty]
    if max_price > 0:
        filtered = [item for item in filtered if item['price'] <= max_price]
    
    st.session_state.filtered_inventory = filtered
    
    # Add new item button
    if st.button(" Add New Item", use_container_width=True):
        st.session_state.show_add_item = True
    
    # Display inventory table
    if not st.session_state.filtered_inventory:
        st.info("No items found. Add some items to get started!")
    else:
        # Convert to DataFrame for better display
        df = pd.DataFrame([{
            "ID": item.get("id", ""),
            "Name": item.get("name", ""),
            "Description": item.get("description", ""),
            "Quantity": item.get("quantity", 0),
            "Unit Price": f"${item.get('price', 0):.2f}",
            "Total Value": f"${item.get('quantity', 0) * item.get('price', 0):.2f}",
            "Last Updated": (
                (item.get("date_updated") or item.get("date_created") or "")[:10] 
                if (item.get("date_updated") or item.get("date_created")) 
                else "N/A"
            )
        } for item in st.session_state.filtered_inventory if item])
        
        # Display the table with delete buttons
        # Table header
        header_cols = st.columns([1, 3, 4, 1, 1, 1, 1])
        headers = ["ID", "Name", "Description", "Qty", "Price", "Total", "Actions"]
        for i, header in enumerate(headers):
            header_cols[i].subheader(header, help=f"Click to sort by {header}" if header != "Actions" else "")
        
        # Table rows
        for item in st.session_state.filtered_inventory:
            cols = st.columns([1, 3, 4, 1, 1, 1, 1])
            with cols[0]:
                st.text(str(item.get("id", "")))
            with cols[1]:
                st.text(item.get("name", ""))
            with cols[2]:
                st.text(item.get("description", "")[:50] + ("..." if len(item.get("description", "")) > 50 else ""))
            with cols[3]:
                st.text(str(item.get("quantity", 0)))
            with cols[4]:
                st.text(f"${item.get('price', 0):.2f}")
            with cols[5]:
                st.text(f"${item.get('quantity', 0) * item.get('price', 0):.2f}")
            with cols[6]:
                if st.button("🗑️", key=f"delete_{item['id']}"):
                    st.session_state.item_to_delete = item['id']
                    st.session_state.item_to_delete_name = item.get('name', 'this item')
                    st.session_state.show_delete_confirm = True
                    st.rerun()
        
        # Delete confirmation dialog
        if st.session_state.get('show_delete_confirm', False):
            # Create a container for the confirmation
            with st.container():
                # Add some CSS for the overlay
                st.markdown("""
                    <style>
                    .stApp [data-testid="stHorizontalBlock"] {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background-color: rgba(0, 0, 0, 0.5);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 1000;
                    }
                    .delete-confirm-box {
                        background: white;
                        padding: 2rem;
                        border-radius: 10px;
                        max-width: 500px;
                        width: 90%;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Create the confirmation dialog
                with st.container():
                    st.warning("⚠️ Confirm Deletion")
                    st.write(f"Are you sure you want to delete \"{st.session_state.get('item_to_delete_name', 'this item')}\"?")
                    st.caption("This action cannot be undone.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Yes, delete it", key="confirm_delete_yes"):
                            response = make_authenticated_request(
                                "DELETE", 
                                f"/items/{st.session_state.item_to_delete}"
                            )
                            if response and response.status_code == 204:  # 204 No Content is standard for successful DELETE
                                st.session_state.show_delete_confirm = False
                                st.session_state.item_to_delete = None
                                st.session_state.item_to_delete_name = None
                                st.success("Item deleted successfully!")
                                load_inventory()
                                st.rerun()
                            else:
                                error = response.json().get("detail", "Failed to delete item") if response else "Failed to connect to server"
                                st.error(f"Error: {error}")
                                st.session_state.show_delete_confirm = False
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key="confirm_delete_no"):
                            st.session_state.show_delete_confirm = False
                            st.session_state.item_to_delete = None
                            st.session_state.item_to_delete_name = None
                            st.rerun()
                
                # Add a bit of spacing
                st.write("")
                st.write("")
                st.write("")
                
                # Stop further execution to show the dialog
                st.stop()
    
    # Add/Edit Item Form
    if st.session_state.get("show_add_item", False):
        with st.form("item_form"):
            st.subheader("Add New Item")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name*")
                price = st.number_input("Unit Price*", min_value=0.0, step=0.01, format="%.2f")
            with col2:
                quantity = st.number_input("Quantity*", min_value=0, step=1)
                description = st.text_area("Description")
            
            submitted = st.form_submit_button("Save Item")
            if submitted:
                if not all([name, str(price), str(quantity)]):
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    response = make_authenticated_request(
                        "POST", "/items/",
                        json={
                            "name": name,
                            "description": description,
                            "quantity": quantity,
                            "price": price
                        }
                    )
                    
                    if response and response.status_code == 201:
                        st.success("Item added successfully!")
                        load_inventory()
                        st.session_state.show_add_item = False
                        st.rerun()
                    else:
                        error = response.json().get("detail", "Failed to add item") if response else "Failed to connect to server"
                        st.error(f"Error: {error}")
            
            if st.form_submit_button("Cancel"):
                st.session_state.show_add_item = False
                st.experimental_rerun()

def show_dashboard():
    """Display the main dashboard"""
    st.title(" Dashboard")
    
    # Summary Cards
    if not st.session_state.inventory:
        st.info("No inventory data available. Add some items to see analytics.")
        return
    
    # Calculate metrics
    total_items = len(st.session_state.inventory)
    total_quantity = sum(item['quantity'] for item in st.session_state.inventory)
    total_value = sum(item['quantity'] * item['price'] for item in st.session_state.inventory)
    low_stock = sum(1 for item in st.session_state.inventory if item['quantity'] < 10)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", total_items)
    with col2:
        st.metric("Total Quantity", total_quantity)
    with col3:
        st.metric("Total Value", f"${total_value:,.2f}")
    with col4:
        st.metric("Low Stock Items", low_stock, delta_color="inverse")
    
    # Charts
    st.markdown("### Inventory Overview")
    
    # Create a bar chart of item quantities
    if st.session_state.inventory:
        chart_data = pd.DataFrame({
            'Item': [item['name'] for item in st.session_state.inventory],
            'Quantity': [item['quantity'] for item in st.session_state.inventory],
            'Value': [item['quantity'] * item['price'] for item in st.session_state.inventory]
        })
        
        # Sort by quantity for better visualization
        chart_data = chart_data.sort_values('Quantity', ascending=False)
        
        # Display charts in tabs
        tab1, tab2 = st.tabs(["By Quantity", "By Value"])
        
        with tab1:
            st.bar_chart(chart_data.set_index('Item')['Quantity'])
        
        with tab2:
            st.bar_chart(chart_data.set_index('Item')['Value'])
    
    # Low stock warning
    if low_stock > 0:
        st.warning(f" You have {low_stock} item(s) with low inventory. Consider restocking soon.")

def main():
    """Main application function"""
    # Check if user is logged in
    if not st.session_state.token or not st.session_state.user:
        show_login_form()
    else:
        # Update session activity
        if not check_session_timeout():
            return
        
        # Load inventory if not already loaded
        if not st.session_state.inventory:
            with st.spinner("Loading inventory..."):
                load_inventory()
        
        # Show main interface
        selection = show_sidebar()
        
        # Main content area
        if selection == "Dashboard":
            show_dashboard()
        elif selection == "Inventory":
            show_inventory()
        elif selection == "Reports":
            st.title(" Reports")
            st.info("Reports feature coming soon!")
        elif selection == "Settings":
            st.title(" Settings")
            st.info("Settings feature coming soon!")

if __name__ == "__main__":
    main()
