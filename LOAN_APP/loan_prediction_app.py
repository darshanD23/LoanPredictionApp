import streamlit as st
import sqlite3
import pandas as pd
import pickle
import base64


# Load the trained model
model = pickle.load(open(r'C:\Users\DN10\Downloads\LOAN_APP\loan_model.pkl', 'rb'))

# Function to add background image with opacity for background only
def add_bg_from_local(image_path):
    """ Function to add background image with opacity for only the background """
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()

    # Apply background image with a semi-transparent overlay for opacity
    st.markdown(
        f"""
        <style>
        .stApp {{
            position: relative;
            background-image: url(data:image/jpeg;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            height: 100vh;
        }}

        .stApp::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.2;  /* Adjust opacity (0.4 is 40%) */
            # z-index: -1; /* Put the overlay behind the content */
        }}

        /* Darken the fonts */
        .stText, .stButton, .stTitle, .stSubheader, .stMarkdown {{
            color: #333333;  /* Darker color for text */
        }}

        .stButton {{
            # background-color: #007BFF;  /* Blue background for visibility */
            color: white;  /* White text color */
            font-weight: bold;  /* Make the text bold */
            border: none;  /* Remove any borders */
            padding: 10px 20px;  /* Add padding to make the button larger */
            border-radius: 5px;  /* Rounded corners for the button */
            transition: background-color 0.3s ease, padding 0.3s ease;  /* Smooth transition for color and padding */
            background-size: 20%;  /* Reduce the background size */
            background-position: center;  /* Ensure the background is centered */
            background-repeat: no-repeat;  /* Ensure no repeating background */
        }}
        .stButton:hover {{
            background-color: #0056b3;  /* Darker blue when hovering */
            padding: 5px 10px;  /* Reduce padding on hover to shrink the button */
            background-size: 50% 50%;  /* Make the background smaller and control the hover effect */
            background-position: center; 
        }}

          /* Reduce width of input fields and text areas */
        .stTextInput, .stTextArea, .stNumberInput{{
            border-radius: 5px;  /* Optional: Add rounded corners */
            background-color: transparent;  /* Optional: Make the background transparent */
            width: 40%;  /* Adjust the percentage to your preference */
        }}
       
        </style>
        """, 
        unsafe_allow_html=True
    )

add_bg_from_local("C:/Users/DN10/Downloads/LOAN_APP/assets/background_image.jpg")



# ================== DATABASE SETUP ================== #
def init_db():
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS feedback 
                 (username TEXT, feedback TEXT)''')
    conn.commit()
    conn.close()

# Add default admin account
def add_admin():
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
              ("admin", "admin123", "admin"))
    conn.commit()
    conn.close()


# Initialize DB and admin user
init_db()
add_admin()

# ================== AUTHENTICATION AND USER MANAGEMENT ================== #
def authenticate(username, password):
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def register_user(username, password):
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, "user"))
        conn.commit()
        return True
    except sqlite3.IntegrityError:  # Username already exists
        return False
    finally:
        conn.close()

def get_registered_users():
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute("SELECT username, role FROM users WHERE role = 'user'")
    users = c.fetchall()
    conn.close()
    return users

def delete_user(username):
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Insert feedback into database
def add_feedback(username, feedback):
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (username, feedback) VALUES (?, ?)", (username, feedback))
    conn.commit()
    conn.close()

# Fetch User Details with Feedback
# Fetch User Details with Feedback (Excluding Admin)
def get_user_details_with_feedback():
    conn = sqlite3.connect('loan_app.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.username, u.role, IFNULL(f.feedback, 'No Feedback') AS feedback
        FROM users u
        LEFT JOIN feedback f ON u.username = f.username
        WHERE u.role != 'admin'
    ''')
    data = c.fetchall()
    conn.close()
    return data



# ================== ADMIN LOGIN PAGE ================== #
def login_page_admin():
    st.subheader("Admin Login")
    username = st.text_input("Enter Admin Username")
    password = st.text_input("Enter Admin Password", type="password")
    
    if st.button("Login as Admin"):
        if username == "admin" and password == "admin123":
            st.success("Welcome Admin!")
            st.session_state['role'] = "admin"
            st.session_state['logged_in_admin'] = True
            st.rerun()
        else:
            st.error("Invalid Admin credentials!")

# Admin Dashboard
def admin_dashboard():
    st.title("Admin Dashboard")
    
    # Display user details along with feedback
    st.subheader("User Details and Feedback")
    user_feedback_data = get_user_details_with_feedback()
    df = pd.DataFrame(user_feedback_data, columns=['Username', 'Role', 'Feedback'])
    st.table(df)

    # Manage Users Section
    st.subheader("Manage Users")
    user_to_delete = st.text_input("Enter Username to Delete")
    if st.button("Delete User"):
        delete_user(user_to_delete)
        st.success(f"User '{user_to_delete}' deleted successfully")
        st.rerun()  # Refresh the dashboard after deletion
    
    # Logout Button
    if st.button("Logout"):
        st.session_state['role'] = None
        st.rerun()


# ================== USER DASHBOARD ================== #
# def user_dashboard():
#     st.title("Loan Approval Prediction Dashboard")
#     st.sidebar.title("Navigation")
#     choice = st.sidebar.radio("Go To", ["Home", "Feedback"])

#     if choice == "Home":
#         st.subheader("Loan Approval Prediction Form")
        
#         # Loan input fields
#         no_of_dependents = st.number_input("Number of Dependents", min_value=0, value=0)
#         education = st.selectbox("Education Level", ["Graduate", "Non-Graduate"])
#         self_employed = st.selectbox("Self-Employed", ["Yes", "No"])
#         income_annum = st.number_input("Annual Income (in INR)", min_value=0)
#         loan_amount = st.number_input("Loan Amount", min_value=0)
#         loan_term = st.number_input("Loan Term (in years)", min_value=0)
#         cibil_score = st.number_input("CIBIL Score", min_value=0)
#         residential_assets_value = st.number_input("Residential Assets Value", min_value=0)
#         commercial_assets_value = st.number_input("Commercial Assets Value", min_value=0)
#         luxury_assets_value = st.number_input("Luxury Assets Value", min_value=0)
#         bank_asset_value = st.number_input("Bank Asset Value", min_value=0)

#         # Encode categorical features
#         education_num = 1 if education == "Graduate" else 0
#         self_employed_num = 1 if self_employed == "Yes" else 0

#         input_data = pd.DataFrame({
#             'no_of_dependents': [no_of_dependents],
#             'education': [education_num],
#             'self_employed': [self_employed_num],
#             'income_annum': [income_annum],
#             'loan_amount': [loan_amount],
#             'loan_term': [loan_term],
#             'cibil_score': [cibil_score],
#             'residential_assets_value': [residential_assets_value],
#             'commercial_assets_value': [commercial_assets_value],
#             'luxury_assets_value': [luxury_assets_value],
#             'bank_asset_value': [bank_asset_value]
#         })

#         if st.button("Predict"):
#             prediction = model.predict(input_data)
#             if prediction[0] == 1:
#                 st.success("Congratulations! The loan is APPROVED ✅")
#             else:
#                 st.error("Sorry, the loan is REJECTED ❌")

#     elif choice == "Feedback":
#         st.subheader("Feedback")
#         feedback = st.text_area("Enter your feedback here")
#         if st.button("Submit Feedback"):
#             add_feedback(st.session_state['username'], feedback)
#             st.success("Feedback Submitted Successfully")
    
#     if st.button("Logout"):
#         st.session_state['role'] = None
#         st.session_state['logged_in_user'] = False
#         st.rerun()


def user_dashboard():
    st.title("Loan Approval Prediction Dashboard")
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go To", ["Home", "Feedback"])

    if choice == "Home":
        st.subheader("Loan Approval Prediction Form")

        # Input fields with tooltips
        no_of_dependents = st.number_input(
            "Number of Dependents", min_value=0, max_value=20, step=1,
            help="Enter the number of dependents (e.g., 0 for no dependents)."
        )
        income_annum = st.number_input(
            "Annual Income (in INR)", min_value=0, step=1000,
            help="Enter your annual income. Ensure the loan amount doesn't exceed 50% of this."
        )
        loan_amount = st.number_input(
            "Loan Amount", min_value=0, step=500,
            help="Enter the loan amount requested. Should not exceed 50% of annual income."
        )
        loan_term = st.number_input(
            "Loan Term (in years)", min_value=0, max_value=40, step=1,
            help="Enter the loan repayment term in years (e.g., 1-40 years)."
        )
        cibil_score = st.number_input(
            "CIBIL Score", min_value=0, max_value=900, step=1,
            help="Enter your CIBIL score (300-900). A score below 500 may reduce approval chances."
        )
        residential_assets_value = st.number_input(
            "Residential Assets Value", min_value=0, step=1000,
            help="Enter the value of your residential assets in INR."
        )
        commercial_assets_value = st.number_input(
            "Commercial Assets Value", min_value=0, step=1000,
            help="Enter the value of your commercial assets in INR."
        )
        luxury_assets_value = st.number_input(
            "Luxury Assets Value", min_value=0, step=1000,
            help="Enter the value of your luxury assets in INR."
        )
        bank_asset_value = st.number_input(
            "Bank Asset Value", min_value=0, step=1000,
            help="Enter the value of your bank assets in INR."
        )

        # Select box fields with tooltips
        education = st.selectbox(
            "Education Level", ["Graduate", "Non-Graduate"],
            index=None, placeholder="Select Education Level",
            help="Choose 'Graduate' if you have a degree, otherwise select 'Non-Graduate'."
        )
        self_employed = st.selectbox(
            "Self-Employed", ["Yes", "No"],
            index=None, placeholder="Select Self-Employed Status",
            help="Choose 'Yes' if you are self-employed, otherwise select 'No'."
        )

        # Predict button logic
        if st.button("Predict"):
            # Check for empty fields
            if any(field is None or field == "" for field in [education, self_employed]):
                st.error("Please fill in all the fields before predicting.")
            elif loan_amount > income_annum * 0.5:
                st.error("Loan amount should not exceed 50% of Annual Income.")
            elif cibil_score < 500:
                st.warning("CIBIL score is too low, loan approval may be difficult.")
            else:
                # Encode categorical features
                education_num = 1 if education == "Graduate" else 0
                self_employed_num = 1 if self_employed == "Yes" else 0

                input_data = pd.DataFrame({
                    'no_of_dependents': [no_of_dependents],
                    'education': [education_num],
                    'self_employed': [self_employed_num],
                    'income_annum': [income_annum],
                    'loan_amount': [loan_amount],
                    'loan_term': [loan_term],
                    'cibil_score': [cibil_score],
                    'residential_assets_value': [residential_assets_value],
                    'commercial_assets_value': [commercial_assets_value],
                    'luxury_assets_value': [luxury_assets_value],
                    'bank_asset_value': [bank_asset_value]
                })

                # Prediction logic
                prediction = model.predict(input_data)
                if prediction[0] == 1:
                    st.success("Congratulations! The loan is APPROVED ✅")
                else:
                    st.error("Sorry, the loan is REJECTED ❌")

    elif choice == "Feedback":
        st.subheader("Feedback")
        feedback = st.text_area("Enter your feedback here")
        if st.button("Submit Feedback"):
            add_feedback(st.session_state.get('username', 'Anonymous'), feedback)
            st.success("Feedback Submitted Successfully")

    # Logout functionality
    if st.button("Logout"):
        st.session_state['logged_in_user'] = False
        st.rerun()


# ================== USER LOGIN/REGISTRATION ================== #
def user_login_register():
    st.subheader("User Login/Register")
    choice = st.radio("Choose an option", ["Login", "Register"])

    # Register Section
    if choice == "Register":
        username = st.text_input("Choose a Username", key="register_username")
        password = st.text_input("Choose a Password", type="password", key="register_password")
        
        if st.button("Register"):
            if username and password:
                if register_user(username, password):
                    st.success(f"User '{username}' registered successfully! Please log in.")
                    # Reset role and username to force user to log in manually
                    st.session_state['role'] = None
                    st.session_state['username'] = None
                else:
                    st.error("Username already exists. Please choose a different one.")
            else:
                st.warning("Username and Password cannot be empty!")

    # Login Section
    elif choice == "Login":
        username = st.text_input("Enter Username", key="login_username")
        password = st.text_input("Enter Password", type="password", key="login_password")
        
        if st.button("Login"):
            if username and password:
                role = authenticate(username, password)
                if role == "user":
                    st.success(f"Welcome, {username}!")
                    st.session_state['role'] = "user"
                    st.session_state['username'] = username
                    st.rerun()  # Redirect to user dashboard
                else:
                    st.error("Invalid username or password. Please try again!")
            else:
                st.warning("Please enter both username and password.")


# ================== MAIN APPLICATION ================== #
if 'role' not in st.session_state:
    st.session_state['role'] = None

if st.session_state['role'] is None:
    st.title("Welcome To Loan Approval Prediction Application")  
    

    login_option = st.selectbox("Select your role:", ["Admin", "User"])

    if login_option == "Admin":
        login_page_admin()
    elif login_option == "User":
        user_login_register()
else:
    if st.session_state['role'] == "admin":
        admin_dashboard()
    elif st.session_state['role'] == "user":
        user_dashboard()
