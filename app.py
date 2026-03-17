import streamlit as st
import requests

API_URL = "http://localhost:5000/api"

# 1.Function part
def get_instances_count(user):
    try:
        instances = list_instances(user)
        total = len(instances)
        running = 0
        for i in instances:
            status = i.get('status') # get the value of key 'status'
            if status == 'running':
                running += 1
        return total, running, total - running # 'total-running' is stopped
    except:
        return 0, 0, 0

def create_instance(payload):
    try:
        resp = requests.post(f"{API_URL}/create", json=payload)
        return resp.json()
    except:
        return {"success": False, "error": "Connection failed"}

def list_instances(user):
    try:
        resp = requests.get(f"{API_URL}/list", params={"user": user})
        return resp.json()
    except:
        return []

def stop_instance(instance_id):
    try:
        resp = requests.post(f"{API_URL}/stop/{instance_id}")
        return resp.json()
    except:
        return {"success": False}

def start_instance(instance_id):
    try:
        resp = requests.post(f"{API_URL}/start/{instance_id}")
        return resp.json()
    except:
        return {"success": False}


def main():
    st.set_page_config(layout="wide")
    # Universal CSS Styling Code
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        }
        .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 255, 150, 0.4);
        background: linear-gradient(45deg, #0d8b7a, #2ed573);
        }
        .stButton > button:active {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(0, 255, 150, 0.3);
        }
        .stButton>button {
            border-radius: 20px;
            border: none;
            background: linear-gradient(45deg, #11998e, #38ef7d);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    if 'user' not in st.session_state:
        st.session_state.user = "demo"

    with st.sidebar:
        st.title("Cloud Service")
        st.text(f"User: {st.session_state.user}")
        menu = st.radio("Menu", ["Index", "Create", "My Instances"])

        new_user = st.text_input("Switch User", st.session_state.user)
        if new_user and new_user != st.session_state.user:
            st.session_state.user = new_user
            st.rerun()

    if menu == "Index":
        st.title("Index")
        total, running, stopped = get_instances_count(st.session_state.user)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total)
        col2.metric("Running", running)
        col3.metric("Stopped", stopped)

    elif menu == "Create":
        st.title("Create Instance")
        with st.form("create_form"):
            col1, col2 = st.columns(2)
            with col1:
                type_choice = st.radio("Type", ["VM", "Container"], horizontal=True)
            with col2:
                name = st.text_input("Name")

            if type_choice == "VM":
                os_list = ["Ubuntu", "Fedora"]
            else:
                os_list = ["ubuntu:22.04", "python:3.9", "nginx"]
            os_choice = st.selectbox("OS", os_list)

            col1, col2 = st.columns(2)
            with col1:
                cpu = st.slider("CPU", 1, 4, 2)
            with col2:
                memory = st.selectbox("memory", ["1GB", "2GB", "4GB"])

            if st.form_submit_button("Create"):
                if not name:
                    st.error("Please enter a name")
                else:
                    payload = {
                        "name": name,
                        "type": "vm" if type_choice == "VM" else "container",
                        "os": os_choice,
                        "cpu": cpu,
                        "memory": memory,
                        "user": st.session_state.user
                    }
                    result = create_instance(payload)
                    if result.get('success'):
                        st.success("Create success")
                    else:
                        st.error("Create failed")

    elif menu == "My Instances":
        st.title("My Instances")
        if st.button("Rerun"):
            st.rerun()

        instances = list_instances(st.session_state.user)

        if not instances:
            st.write("No instance")
        else:
            running = 0
            for i in instances:
                if i.get('status') == 'running':
                    running += 1
            st.write(f"Total: {len(instances)} , Running: {running} ")
            st.write("---")

            for i, inst in enumerate(instances): #Get index and content at the same time
                inst_id = inst.get('id', '')
                inst_name = inst.get('name', '')
                inst_type = inst.get('type', '')
                inst_os = inst.get('os', '')
                inst_cpu = inst.get('cpu', '')
                inst_mem = inst.get('memory', '')
                inst_status = inst.get('status', '')

                st.write(f"{i + 1}. {inst_name} | {inst_type} | {inst_os} | {inst_cpu}cores | {inst_mem} | {inst_status}")

                col1, col2 = st.columns([1, 10])
                with col1:
                    if inst_status == 'running':
                        if st.button("Stop", key=f"s{inst_id}"):# s+inst_id = stop inst_id
                            stop_instance(inst_id)
                            st.rerun()
                    else:
                        if st.button("Start", key=f"t{inst_id}"):# t+inst_id = start inst_id
                            start_instance(inst_id)
                            st.rerun()
                st.write("---")


if __name__ == "__main__":
    main()