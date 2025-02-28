# AI Coding Mentor

**An interactive AI-powered learning platform designed to help you master coding concepts.**


## Overview

The AI Coding Mentor is a web application that combines educational resources, interactive quizzes, and an AI chat assistant to guide users through their coding journey. It's built using Python, Streamlit for the user interface, and MongoDB for data storage. The app leverages vector search for efficient resource retrieval and integrates with the Parlant AI platform for conversational support.

## Key Features

*   **Learning Roadmaps:**
    *   Structured learning paths broken down into topics and subtopics.
    *   Progress tracking with completion status for each subtopic and topic.
    *   Ability to add new topics and subtopics to customize learning.
*   **Interactive Quizzes:**
    *   Engaging quizzes to test your knowledge of various coding concepts.
    *   Questions and answers stored in a database.
*   **Resource Library:**
    *   A curated collection of coding resources like articles, tutorials, and documentation.
    *   Vector search capability for finding relevant resources using natural language queries.
*   **AI Chat Assistant:**
    *   Integration with the Parlant platform to provide an interactive chat experience.
    *   Ask questions, get explanations, and receive guidance from an AI tutor.
* **Multiple roadmaps**:
    * Users can select between multiple roadmaps.

## Technologies Used

*   **Python:** The primary programming language.
*   **Streamlit:** For building the web application interface.
*   **MongoDB:** A NoSQL database for storing data (roadmaps, quizzes, resources, etc.).
*   **Pymongo:** The Python driver for MongoDB.
*   **Python-dotenv:** For managing environment variables.
*   **Pydantic:** For data validation and settings management.
*   **Sentence Transformers:** For generating vector embeddings and implementing semantic search.
*   **Parlant SDK:** For integrating AI chat functionality.
* **Einops**: For tensor operations.

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.8+
    *   pip (Python package installer)
    *   MongoDB Atlas account (or a local MongoDB instance)
    *   Parlant platform account (for AI chat integration)

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/dimipash/AI_coding_mentor.git
    cd AI_coding_mentor
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    *   Create a `.env` file in the root directory of the project.
    *   Add your MongoDB connection credentials:
        ```
        MONGO_PWD=your_mongodb_password
        MONGO_USER=your_mongodb_username
        ```
    *   *Optional:* Add any other environment variables that your application needs.

5.  **Parlant SDK:**
    *   The `parlant-sdk` is a private package. You'll need to install it separately. Follow the instructions provided by the Parlant team for installation.
    * If you have access to the source code, do:
        ```
        pip install -e <parlant-sdk_path>
        ```
    * If you have a .whl file, use:
    ```
    pip install <parlant-sdk_path>.whl
    ```
6.  **MongoDB Index:**
    *   You need to create a vector search index in your MongoDB database to use the resource search feature.
    *   Run the `create_index` function in `database.py` (you can add temporary code to the main function of the file to run it):
        ```python
        from database import Database
        db = Database()
        db.create_index()
        ```
    * It will create an index named vector_index.
    *  You might need to wait a couple of minutes before using the index.

7. **Create agents in Parlant**
    * Create your agents in parlant, and get the id.
    * update the agent id in the chat component.

8. **Run the app**
    * Run the app using streamlit:
    ```bash
    streamlit run pages/1_Roadmap.py
    ```
    Or you can run the other pages.
    * Open your browser and go to http://localhost:8501

## Usage

1.  **Explore Roadmaps:**
    *   Navigate to the "Roadmap" page to view structured learning paths.
    *   Track your progress by marking subtopics as completed.
    * Add new subtopics and topics.
2.  **Take Quizzes:**
    *   Go to the "Quizzes" page to access various coding quizzes.
    *   Test your knowledge and get instant feedback.
3.  **Search Resources:**
    *   Use the "Resources" page to explore the library of learning materials.
    *   Utilize the powerful vector search to find resources using natural language.
4.  **Chat with the AI Tutor:**
    *   Interact with the AI tutor on any page to ask questions, get explanations, or receive guidance.

