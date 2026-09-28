# Dictionary Word Finder

Dictionary Word Finder is an AI-powered desktop dictionary application built with C++20 and Qt 6. It provides a modern user interface for registration, authentication, word lookup, saved words, search history, profile management, and theme switching.

## Features

- User registration and login
- Password hashing with a secure hash algorithm
- AI-powered word search using the Google Gemini API
- Definitions, synonyms, antonyms, examples, pronunciation, and related words
- Saved word bookmarks
- Search history with delete and clear actions
- Profile management
- Light and dark themes
- SQLite database persistence

## Technology Stack

- C++20
- Qt 6 Widgets
- Qt SQL
- Qt Network
- Qt JSON
- SQLite
- Google Gemini API
- CMake

## Project Structure

- src/database: SQLite database management
- src/models: domain models
- src/services: authentication and Gemini API integration
- src/ui: Qt windows and widgets
- src/utils: password hashing and validation helpers
- resources: Qt resource files and SVG assets

## Installation

1. Install Qt 6 and CMake.
2. Clone the repository.
3. Create a `.env` file in the project root using `.env.example` as a template.
4. Add your Gemini API key.
5. Configure the build directory.
6. Build the project with CMake.
7. Run the application.

## Environment Configuration

The application expects an environment variable named `GEMINI_API_KEY`.

Example `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

The application reads the environment variable at runtime. Do not commit the real API key to source control.

## Build

```bash
cmake -S . -B build
cmake --build build
```

## Run

```bash
./build/DictionaryWordFinder
```

## Security Notes

- Passwords are never stored as plain text.
- SQL statements use prepared queries.
- User data is isolated by `user_id`.
- API keys are kept out of source code.

## License

This project is licensed under the MIT License.
