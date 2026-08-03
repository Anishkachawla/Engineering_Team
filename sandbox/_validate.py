from app import create_ui

try:
    demo = create_ui()
    print("UI constructed successfully!")
except Exception as e:
    print(f"Error constructing UI: {e}")
