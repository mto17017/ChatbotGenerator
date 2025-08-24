# Chatbot Generator

This project allows you to generate a custom chatbot from a website URL or a CSV file.

## How to Run the Generator

### 1. Setup the Generator Backend

1.  **Navigate to the generator backend directory:**
    ```bash
    cd generator-backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API key:**
    -   Open the `.env` file.
    -   Replace `YOUR_API_KEY_HERE` with your actual Gemini API key.

5.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The generator backend will be running at `http://localhost:8000`.

### 2. Setup the Generator Frontend

1.  **Navigate to the generator frontend directory in a new terminal:**
    ```bash
    cd generator-frontend
    ```

2.  **Install the dependencies:**
    ```bash
    npm install
    ```

3.  **Run the frontend server:**
    ```bash
    npm run dev
    ```
    The generator frontend will be running at `http://localhost:3000`.

### 3. Generate Your Chatbot!

1.  Open your browser and go to `http://localhost:3000`.
2.  Choose to generate from a URL or a CSV file.
3.  After the chatbot is generated, a "Test Your Chatbot" button will appear.
4.  Click the button to go to a new page where you can chat with your newly created chatbot.

