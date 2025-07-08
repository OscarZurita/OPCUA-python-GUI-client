# OPC UA Desktop Client

This is a Python desktop application that connects to a local OPC UA server and displays information through a graphical user interface built with PyQt5.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the OPC UA server (in a separate terminal):
   ```bash
   python serverV1.py
   ```
3. Run the application:
   ```bash
   python main.py
   ``` 

## Next Steps

- **Improve GUI Style:**

- **User Management:**
  - Add features for creating, editing, and deleting users.

- **Asset Creation:**
  - Implement functionality to create and manage new glasses (AAS models) dynamically from the GUI admin interface.
 
- **Password encryption:**
  - It would be crucial to encrypt passwords when we move to production
 
