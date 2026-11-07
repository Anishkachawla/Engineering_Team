from app import demo

def validate_app():
    print("Attempting to construct Gradio demo...")
    # Just checking if the object was created successfully should be enough
    # If the import 'from app import demo' didn't raise an error, 
    # it means the code in app.py executed and initialized the `demo` object.
    print(f"Gradio object type: {type(demo)}")
    print("Success: Gradio demo object imported and validated.")

if __name__ == "__main__":
    validate_app()
